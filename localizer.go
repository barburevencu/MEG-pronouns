// Localizer: an animal-detection task on words and pictures, run after the
// main task.
//
// Each stimulus is on for 600 ms, followed by 200 ms of fixation. Stimuli come
// in mini-blocks of one modality, words and pictures alternating: the 32
// people and places of the main task, plus animals (about 11% of the trials).
// Between mini-blocks, a 10 s screen announces the next modality, with a
// counter of the seconds left, and the percentage of animals hit in the
// mini-block just done (the screen after a block gives the block's). The participant presses the right green button
// when they see an animal. In
// a word mini-block the cross is the main task's (small, light grey), the
// word drawn on top of it; in a picture mini-block it is the large grey cross,
// drawn on top of the picture. A press 200-1200 ms after an animal's onset is
// a hit. No press gets feedback, in training as in the main blocks: the
// participant only learns the percentage of animals hit, on the screen after
// each mini-block. Sequences come from localizer/localizer.csv
// (make_localizer.py).

package main

import (
	"bytes"
	"embed"
	"encoding/csv"
	"fmt"
	"io"
	"math/rand/v2"
	"strconv"
	"strings"
	"time"

	"github.com/chrplr/goxpyriment/control"
	"github.com/chrplr/goxpyriment/stimuli"
)

//go:embed localizer/localizer.csv
var localizerCSV []byte

//go:embed localizer/images/*.png
var localizerImages embed.FS

const (
	locOnMs           = 600  // stimulus on
	locOffMs          = 200  // fixation after it
	locHitFromMs      = 200  // a press this long after an animal's onset ...
	locHitUntilMs     = 1200 // ... and up to this long after it is a hit
	locBlocks         = 3    // 0 = training, 1 and 2
	codeLocBlock      = 207  // + block, instruction / pause screen
	locBreakS         = 10   // screen announcing the next mini-block, in seconds
	codeLocNextWords  = 250  // onset of that screen, before a word mini-block
	codeLocNextImages = 251  // ... before a picture mini-block
)

type locTrial struct {
	block, number, miniblock int
	modality                 string // "word" or "image"
	item, image              string
	concept, code            int
	target                   bool // an animal
	fields                   map[string]string
	stim                     stimuli.VisualStimulus
}

// loadLocalizer returns the subject's localizer trials, block by block, in
// presentation order.
func loadLocalizer(raw []byte, subject int) ([]*locTrial, error) {
	r := csv.NewReader(bytes.NewReader(raw))
	header, err := r.Read()
	if err != nil {
		return nil, fmt.Errorf("reading header: %w", err)
	}
	var trials []*locTrial
	for line := 2; ; line++ {
		rec, err := r.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			return nil, err
		}
		f := make(map[string]string, len(header))
		for i, h := range header {
			f[h] = rec[i]
		}
		if f["subject_id"] != strconv.Itoa(subject) {
			continue
		}
		t := &locTrial{modality: f["modality"], item: f["item"], image: f["image"], target: f["target"] == "1", fields: f}
		for _, v := range []struct {
			dst  *int
			name string
		}{{&t.block, "block"}, {&t.number, "trial_number"}, {&t.miniblock, "miniblock"}, {&t.concept, "concept"}, {&t.code, "code"}} {
			if *v.dst, err = strconv.Atoi(f[v.name]); err != nil {
				return nil, fmt.Errorf("line %d: %s: %w", line, v.name, err)
			}
		}
		if t.modality != "word" && t.modality != "image" {
			return nil, fmt.Errorf("line %d: modality %q", line, t.modality)
		}
		trials = append(trials, t)
	}
	if len(trials) == 0 {
		return nil, fmt.Errorf("no localizer trials for subject %d", subject)
	}
	for i, t := range trials {
		if i == 0 || t.block != trials[i-1].block {
			if t.number != 1 || (i > 0 && t.block != trials[i-1].block+1) {
				return nil, fmt.Errorf("block %d trial %d: rows not in presentation order", t.block, t.number)
			}
		} else if t.number != trials[i-1].number+1 {
			return nil, fmt.Errorf("block %d trial %d: rows not in presentation order", t.block, t.number)
		}
	}
	return trials, nil
}

// parseLocalizerBlocks reads -localizer: "none", or a comma list of "train",
// "1" and "2". It returns which blocks to run.
func parseLocalizerBlocks(s string) ([locBlocks]bool, error) {
	var run [locBlocks]bool
	if strings.TrimSpace(s) == "none" {
		return run, nil
	}
	for _, part := range strings.Split(s, ",") {
		switch strings.TrimSpace(part) {
		case "train":
			run[0] = true
		case "1":
			run[1] = true
		case "2":
			run[2] = true
		default:
			return run, fmt.Errorf("-localizer %q: none, or a comma list of train, 1, 2", s)
		}
	}
	return run, nil
}

// locOutcome is what happened on one animal trial.
type locOutcome struct {
	hitNS uint64 // the press that made it a hit, 0 for a miss
}

// locPress is one press of the right button during a block.
type locPress struct {
	ns    uint64
	trial int // the trial it answers: the animal for a hit, else the trial on screen (or in its fixation)
	hit   bool
}

// locCrosses are the fixation crosses of the two kinds of mini-block.
type locCrosses struct {
	word, image stimuli.VisualStimulus
}

// runLocalizerBlock presents one mini-block as a single stream and returns the
// stimulus timing, each trial's outcome (for animals) and every press.
// Presses are read every frame, the right button only. With auto, it answers
// 85% of the animals and 1% of the other trials, 400-700 ms after the onset.
func runLocalizerBlock(exp *control.Experiment, trials []*locTrial, resp responder, auto bool, rng *rand.Rand,
	crosses locCrosses) ([]stimuli.TimingLog, []locOutcome, []locPress, error) {
	out := make([]locOutcome, len(trials))
	var presses []locPress
	onset := make([]uint64, len(trials))
	autoRT := make([]uint64, len(trials)) // 0: no press
	for i, t := range trials {
		if p := map[bool]float64{true: 0.85, false: 0.01}[t.target]; rng.Float64() < p {
			autoRT[i] = uint64(400+rng.IntN(300)) * 1_000_000
		}
	}
	cur := -1        // trial whose stimulus or fixation is on screen
	lastTarget := -1 // latest animal shown
	seen := 0        // ctx.Events already read (keyboard)

	el := make([]stimuli.StreamElement, len(trials))
	for i, t := range trials {
		el[i] = stimuli.StreamElement{Stimulus: preloaded{t.stim},
			DurationOn: locOnMs * time.Millisecond, DurationOff: locOffMs * time.Millisecond}
	}

	onFrame := func(ctx stimuli.FrameContext) error {
		// A press belongs to the trial on screen; on an onset frame that is
		// still the previous trial (the new stimulus is not up).
		var pressNS uint64
		if auto {
			if key, _, quit := exp.Keyboard.PollKeysWithTS(); quit || key == control.K_ESCAPE {
				return control.EndLoop
			}
			if cur >= 0 && autoRT[cur] != 0 && onset[cur] != 0 && ctx.NowNS >= onset[cur]+autoRT[cur] {
				pressNS, autoRT[cur] = ctx.NowNS, 0
			}
		} else {
			btn, ts, err := streamPoll(resp, ctx, &seen)
			if err != nil {
				return err
			}
			if btn == "right" {
				pressNS = ts
			}
		}
		if pressNS != 0 && cur >= 0 {
			p := locPress{ns: pressNS, trial: cur}
			if a := lastTarget; a >= 0 && out[a].hitNS == 0 &&
				pressNS >= onset[a]+locHitFromMs*1_000_000 && pressNS <= onset[a]+locHitUntilMs*1_000_000 {
				p.trial, p.hit = a, true
				out[a].hitNS = pressNS
			}
			presses = append(presses, p)
		}

		if ctx.OnPhase && ctx.Frame == 0 {
			// The stimulus code goes with the onset.
			cur = ctx.Index
			exp.Marker.Arm(byte(trials[cur].code))
		}

		t := trials[ctx.Index]
		cross := crosses.image
		if t.modality == "word" {
			cross = crosses.word
		}
		if err := ctx.Screen.Clear(); err != nil {
			return err
		}
		// A picture under its cross; a word on top of its cross.
		if ctx.OnPhase && t.modality == "image" {
			if err := t.stim.Draw(ctx.Screen); err != nil {
				return err
			}
		}
		if err := cross.Draw(ctx.Screen); err != nil {
			return err
		}
		if ctx.OnPhase && t.modality == "word" {
			return t.stim.Draw(ctx.Screen)
		}
		return nil
	}
	onOnset := func(i int, ns uint64) error {
		onset[i] = ns
		if trials[i].target {
			lastTarget = i
		}
		return nil
	}

	_, timing, err := stimuli.PresentStreamOfStimuliHooks(exp.Screen, el, 0, 0, onFrame, onOnset)
	return timing, out, presses, err
}
