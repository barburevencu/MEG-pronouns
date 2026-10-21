// Localizer: a one-back task on the 32 nouns, run before the main task.
//
// Words and pictures alternate, each on screen for a full second, with no
// blank in between. The participant presses the right green button when the
// stimulus is the same concept as the previous one (a match). A picture has the
// fixation cross on top of it; a word has none. Feedback: green at a press on
// a match, red at a press on a non-match, red 800 ms after a match's onset if
// there was no press, shown by the cross on a picture and by a small dot at
// the centre of a word; it disappears at the next stimulus. Sequences come from localizer/localizer.csv (make_localizer.py).

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
	locOnMs       = 1000 // each stimulus stays on until the next
	locDeadlineMs = 800  // a match not answered by then is a miss
	locBlocks     = 3    // 0 = training, 1 and 2
	codeLocBlock  = 206  // + block, instruction / pause screen
)

// The localizer reuses the main task's feedback codes.
const (
	codeLocHit        = codeCorrect
	codeLocFalseAlarm = codeIncorrect
	codeLocMiss       = codeTimeout
)

type locTrial struct {
	block, number int
	modality      string // "word" or "image"
	item, image   string
	concept, code int
	match         bool
	fields        map[string]string
	stim          stimuli.VisualStimulus
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
		t := &locTrial{modality: f["modality"], item: f["item"], image: f["image"], match: f["match"] == "1", fields: f}
		for _, v := range []struct {
			dst  *int
			name string
		}{{&t.block, "block"}, {&t.number, "trial_number"}, {&t.concept, "concept"}, {&t.code, "code"}} {
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

// locOutcome is what happened on one localizer trial.
type locOutcome struct {
	pressNS  uint64 // first press of the right button during the trial, 0 if none
	late     bool   // press on a match after the 800 ms deadline
	feedback int    // feedback code sent (0 if none)
	fbNS     uint64 // time the feedback frame was drawn (just before its flip)
}

// runLocalizerBlock presents one block as a single stream and returns the
// stimulus timing and each trial's outcome. Presses are read every frame, the
// right button only. With auto, it answers 80% of the matches and 3% of the
// non-matches, 400-700 ms after the onset, so every kind of feedback occurs.
func runLocalizerBlock(exp *control.Experiment, trials []*locTrial, resp responder, auto bool, rng *rand.Rand,
	fix, fixHit, fixWrong, dotHit, dotWrong stimuli.VisualStimulus) ([]stimuli.TimingLog, []locOutcome, error) {
	out := make([]locOutcome, len(trials))
	onset := make([]uint64, len(trials))
	autoRT := make([]uint64, len(trials)) // 0: no press
	for i, t := range trials {
		if p := map[bool]float64{true: 0.8, false: 0.03}[t.match]; rng.Float64() < p {
			autoRT[i] = uint64(400+rng.IntN(300)) * 1_000_000
		}
	}
	half := uint64(exp.Screen.FrameDuration()) / 2
	cur := -1 // trial whose second is running
	cross := fix

	el := make([]stimuli.StreamElement, len(trials))
	for i, t := range trials {
		el[i] = stimuli.StreamElement{Stimulus: t.stim, DurationOn: locOnMs * time.Millisecond}
	}

	onFrame := func(ctx stimuli.FrameContext) error {
		onsetFrame := ctx.OnPhase && ctx.Frame == 0

		// A press belongs to the trial whose second is running; on an onset
		// frame that is still the previous trial (the new stimulus is not up).
		var pressNS uint64
		if auto {
			if key, _, quit := exp.Keyboard.PollKeysWithTS(); quit || key == control.K_ESCAPE {
				return control.EndLoop
			}
			if cur >= 0 && autoRT[cur] != 0 && out[cur].pressNS == 0 && onset[cur] != 0 && ctx.NowNS >= onset[cur]+autoRT[cur] {
				pressNS = ctx.NowNS
			}
		} else {
			btn, ts, err := resp.poll()
			if err != nil {
				return err
			}
			if btn == "right" {
				pressNS = ts
			}
		}
		feedback := 0
		if cur >= 0 && pressNS != 0 && out[cur].pressNS == 0 {
			o := &out[cur]
			o.pressNS = pressNS
			switch {
			case !trials[cur].match:
				feedback, cross = codeLocFalseAlarm, fixWrong
			case o.feedback == codeLocMiss:
				o.late = true
			default:
				feedback, cross = codeLocHit, fixHit
			}
		}
		// Miss: no press on a match by the deadline (the frame drawn now is
		// flipped within half a frame of it).
		if cur >= 0 && trials[cur].match && out[cur].pressNS == 0 && out[cur].feedback == 0 && onset[cur] != 0 &&
			ctx.NowNS+half >= onset[cur]+locDeadlineMs*1_000_000 {
			feedback, cross = codeLocMiss, fixWrong
		}

		if onsetFrame {
			// The new stimulus replaces any feedback; a press seen just now
			// is logged for the previous trial, without feedback.
			cur, cross = ctx.Index, fix
			exp.Marker.Arm(byte(trials[cur].code))
		} else if feedback != 0 {
			out[cur].feedback, out[cur].fbNS = feedback, ctx.NowNS
			exp.Marker.Arm(byte(feedback))
		}

		// The stream has drawn the stimulus; on a picture the cross goes on
		// top, on a word only the feedback dot.
		if trials[ctx.Index].modality == "word" {
			switch cross {
			case fixHit:
				return dotHit.Draw(ctx.Screen)
			case fixWrong:
				return dotWrong.Draw(ctx.Screen)
			}
			return nil
		}
		return cross.Draw(ctx.Screen)
	}
	onOnset := func(i int, ns uint64) error {
		onset[i] = ns
		return nil
	}

	_, timing, err := stimuli.PresentStreamOfStimuliHooks(exp.Screen, el, 0, 0, onFrame, onOnset)
	return timing, out, err
}
