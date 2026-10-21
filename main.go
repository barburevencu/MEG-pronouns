// Pronouns — MEG experiment on pronoun resolution (French).
//
// The session opens with a localizer (localizer.go): a one-back task on words
// and pictures of the 32 nouns, a 64-trial training block and two blocks of
// 512. Then the main task:
//
// Each trial: fixation (1000 ms), sentence 1 word by word (6 words, each
// 500 ms on, no blank in between), a 1000 ms break, sentence 2 (3 words, same
// timing), then a felicity judgment (two green buttons, max 3000 ms) answered
// once the last word has gone off, and 500 ms of feedback on the fixation
// cross (green correct, red incorrect, dark grey timeout). The cross is hidden
// while a word is on screen. 160 trials per subject
// in 5 blocks of 32, with a pause before each block that the operator ends with SPACE. Trials come
// from counterbalancing/counterbalancing.csv (make_counterbalancing.py), embedded in the binary.
//
// Trigger codes (see triggers/make_trigger_table.py, triggers/triggers.csv):
//
//	1-64            localizer: word (1-32) or picture (33-64) of concept 1-32
//	16*role + cell  word onsets (role 1-9, cell = condition bits, 16-159)
//	160 + trial     trial start, fixation onset (161-192)
//	200 + block     pause / instruction screen before block (201-205)
//	206 + block     localizer: pause / instruction screen (206 training, 207-208)
//	211 / 212 / 213 feedback onset: correct / incorrect / timeout (localizer:
//	                hit / false alarm / miss)
//	255             end screen
//
// Every code is written right after the flip that shows the event, together
// with the photodiode square (top-left). Button presses are recorded by the
// MEG itself on its own STI lines.
//
// Usage:
//
//	go run . -w -s 1               # windowed test, keyboard (← / →)
//	go run . -s 1 -meg             # MEG: parallel-port triggers and buttons
//	go run . -s 1 -meg -block 3    # resume a session at block 3 (skips the localizer)
//	go run . -s 1 -meg -localizer 2  # only localizer block 2, then the main task
package main

import (
	"bytes"
	_ "embed"
	"encoding/csv"
	"flag"
	"fmt"
	"image"
	"image/color"
	"image/png"
	"io"
	"log"
	"math"
	"math/rand/v2"
	"os"
	"path/filepath"
	"runtime"
	"runtime/debug"
	"strconv"
	"strings"
	"time"

	"github.com/Zyko0/go-sdl3/ttf"
	"github.com/chrplr/goxpyriment/apparatus"
	"github.com/chrplr/goxpyriment/assets_embed"
	"github.com/chrplr/goxpyriment/control"
	"github.com/chrplr/goxpyriment/results"
	"github.com/chrplr/goxpyriment/stimuli"
	"github.com/chrplr/goxpyriment/triggers"
)

//go:embed counterbalancing/counterbalancing.csv
var counterbalancingCSV []byte

// ---------------------------------------------------------------------------
// Timing (ms)

const (
	fixationMs       = 1000 // initial fixation, and the break between sentences
	wordOnMs         = 500  // each word stays on until the next
	wordOffMs        = 0
	responseWindowMs = 3000
	feedbackMs       = 500
	endScreenMs      = 5000
	nBlocks          = 5
)

// dataDir is where the data files go, relative to the project folder (the
// folder holding the executable), so the folder can be copied anywhere.
const dataDir = "data"

// ---------------------------------------------------------------------------
// Appearance (change freely)

var (
	backgroundColor = control.Black
	textColor       = control.White
	fixColor        = control.RGB(192, 192, 192) // light grey
	correctColor    = control.RGB(153, 229, 153)
	incorrectColor  = control.RGB(240, 128, 128)
	timeoutColor    = control.RGB(96, 96, 96) // dark grey
)

const (
	megShiftX = 330 // in -meg fullscreen, everything is drawn this many pixels left of the screen center (MEG projector)
	// Word size: the widest word of both tasks, and the localizer's pictures,
	// span this visual angle on the MEG screen.
	defaultWordDeg    = 10
	defaultScreenCm   = 75  // width of the projected image (estimate; measure it)
	defaultDistanceCm = 104 // viewing distance in the MEG
	fixSize           = 16  // fixation cross, width and height in pixels
	fixThickness      = 2   // fixation cross, line thickness in pixels
	dotSize           = 10  // localizer feedback dot on a word, diameter in pixels
)

// ---------------------------------------------------------------------------
// MEG hardware (NeuroSpin, as in the Pushmi experiment)
//
// Triggers go out on the data lines of /dev/parport1. The response pad's green
// buttons come in on status lines: left green on pin 15 (nError) of
// /dev/parport0, right green on pin 12 (PaperOut) of /dev/parport1, as
// measured on the rig with tools/buttontest (Pushmi's constants.py swaps left
// green with right blue, which is pin 10 of /dev/parport0). A button is down
// when its bit differs from the value read at startup.

const (
	triggerPort    = "/dev/parport1"
	leftGreenPort  = "/dev/parport0"
	rightGreenPort = "/dev/parport1"
	leftGreenMask  = 0x08 // status register bit 3, pin 15
	rightGreenMask = 0x20 // status register bit 5, pin 12
	pollInterval   = 500 * time.Microsecond
)

// ---------------------------------------------------------------------------
// Trigger codes

const (
	codeTrialStart = 160 // + trial_number
	codeBlockStart = 200 // + block_number
	codeCorrect    = 211
	codeIncorrect  = 212
	codeTimeout    = 213
	codeEnd        = 255
)

// Word roles, numbered as in the trigger table.
const (
	roleDetSubj = iota + 1
	roleNounSubj
	roleVerb
	roleDans
	roleDetPlace
	roleNounPlace
	rolePronoun
	roleEtait
	roleAdjective
)

var roleNames = map[int]string{
	roleDetSubj: "det_subj", roleNounSubj: "noun_subj", roleVerb: "verb",
	roleDans: "dans", roleDetPlace: "det_place", roleNounPlace: "noun_place",
	rolePronoun: "pronoun", roleEtait: "etait", roleAdjective: "adjective",
}

var (
	canonicalRoles    = []int{roleDetSubj, roleNounSubj, roleVerb, roleDans, roleDetPlace, roleNounPlace}
	nonCanonicalRoles = []int{roleDans, roleDetPlace, roleNounPlace, roleDetSubj, roleNounSubj, roleVerb}
	sentence2Roles    = []int{rolePronoun, roleEtait, roleAdjective}
)

// ---------------------------------------------------------------------------
// Trials

type word struct {
	text     string
	role     int
	sentence int // 1 or 2
	position int // 1-based, within its sentence
	code     byte
	stim     *stimuli.TextLine
}

type trial struct {
	block, number int
	fields        map[string]string // the counterbalancing row
	cell          int
	correctKey    string // "left" or "right"
	words         []word // the 6 words of sentence 1, then the 3 of sentence 2
}

// loadTrials returns the subject's trials from the counterbalancing table, in
// presentation order, with each word's role and trigger code.
func loadTrials(raw []byte, subject int) ([]*trial, error) {
	r := csv.NewReader(bytes.NewReader(raw))
	header, err := r.Read()
	if err != nil {
		return nil, fmt.Errorf("reading header: %w", err)
	}
	var trials []*trial
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
		t, err := newTrial(f)
		if err != nil {
			return nil, fmt.Errorf("line %d: %w", line, err)
		}
		trials = append(trials, t)
	}
	if len(trials) == 0 {
		return nil, fmt.Errorf("no trials for subject %d", subject)
	}
	for i, t := range trials {
		if want := (i/32+1)*1000 + i%32 + 1; t.block*1000+t.number != want {
			return nil, fmt.Errorf("trial %d is block %d trial %d: rows not in presentation order", i+1, t.block, t.number)
		}
	}
	return trials, nil
}

func newTrial(f map[string]string) (*trial, error) {
	t := &trial{fields: f, correctKey: f["correct_key"]}
	var err error
	if t.block, err = strconv.Atoi(f["block_number"]); err != nil {
		return nil, fmt.Errorf("block_number: %w", err)
	}
	if t.number, err = strconv.Atoi(f["trial_number"]); err != nil {
		return nil, fmt.Errorf("trial_number: %w", err)
	}
	if t.correctKey != "left" && t.correctKey != "right" {
		return nil, fmt.Errorf("correct_key %q", t.correctKey)
	}

	canonical := f["canonical_order"] == "1"
	if f["congruent"] == "1" {
		t.cell |= 1
	}
	if canonical {
		t.cell |= 2
	}
	if f["pronoun_gender"] == "f" {
		t.cell |= 4
	}
	if f["agent_gender"] == "f" {
		t.cell |= 8
	}

	roles1 := nonCanonicalRoles
	if canonical {
		roles1 = canonicalRoles
	}
	for s, spec := range []struct {
		text  string
		roles []int
	}{{f["sentence1"], roles1}, {f["sentence2"], sentence2Roles}} {
		texts := strings.Fields(strings.TrimSuffix(spec.text, "."))
		if len(texts) != len(spec.roles) {
			return nil, fmt.Errorf("sentence%d %q has %d words, expected %d", s+1, spec.text, len(texts), len(spec.roles))
		}
		for i, txt := range texts {
			role := spec.roles[i]
			t.words = append(t.words, word{
				text: txt, role: role, sentence: s + 1, position: i + 1,
				code: byte(16*role + t.cell),
			})
		}
	}

	// The roles must match the words the table says the sentence contains.
	check := map[int]string{
		roleNounSubj: f["subject"], roleVerb: f["verb"], roleAdjective: f["adjective"],
	}
	for _, w := range t.words {
		if want, ok := check[w.role]; ok && w.text != want {
			return nil, fmt.Errorf("%s is %q, expected %q (%s)", roleNames[w.role], w.text, want, f["stimulus"])
		}
	}
	return t, nil
}

// ---------------------------------------------------------------------------
// Responses

// responder reports the first press of the left or right response button.
type responder interface {
	// poll returns "left", "right" or "" and the SDL-clock time of the check.
	// It returns control.EndLoop on ESC or window close.
	poll() (string, uint64, error)
	desc() string
}

// keyboardResponder: ← and → (offline / behavioural testing).
type keyboardResponder struct{ kb *apparatus.Keyboard }

func (k keyboardResponder) poll() (string, uint64, error) {
	key, ts, quit := k.kb.PollKeysWithTS()
	switch {
	case quit || key == control.K_ESCAPE:
		return "", 0, control.EndLoop
	case key == control.K_LEFT:
		return "left", ts, nil
	case key == control.K_RIGHT:
		return "right", ts, nil
	}
	return "", 0, nil
}

func (keyboardResponder) desc() string { return "keyboard (left/right arrows)" }

// autoResponder answers at random 500-1500 ms after it starts being polled,
// for unattended timing checks (-auto).
type autoResponder struct {
	kb      *apparatus.Keyboard
	rng     *rand.Rand
	startNS uint64
}

func (a *autoResponder) poll() (string, uint64, error) {
	if key, _, quit := a.kb.PollKeysWithTS(); quit || key == control.K_ESCAPE {
		return "", 0, control.EndLoop
	}
	now := control.TicksNS()
	if a.startNS == 0 {
		a.startNS = now
		return "", 0, nil
	}
	if now-a.startNS < uint64(500+a.rng.IntN(1000))*1_000_000 {
		return "", 0, nil
	}
	a.startNS = 0
	return [2]string{"left", "right"}[a.rng.IntN(2)], now, nil
}

func (*autoResponder) desc() string { return "automatic random answers (-auto)" }

// buttonResponder reads the MEG response pad through the parallel ports'
// status lines. The operator's keyboard still answers ESC.
type buttonResponder struct {
	kb          *apparatus.Keyboard
	left, right *triggers.ParallelPort
	baseL       byte
	baseR       byte
	downL       bool
	downR       bool
}

func newButtonResponder(kb *apparatus.Keyboard, left, right *triggers.ParallelPort) (*buttonResponder, error) {
	b := &buttonResponder{kb: kb, left: left, right: right}
	var err error
	if b.baseL, err = left.ReadStatus(); err != nil {
		return nil, err
	}
	if b.baseR, err = right.ReadStatus(); err != nil {
		return nil, err
	}
	return b, nil
}

func (b *buttonResponder) poll() (string, uint64, error) {
	if key, _, quit := b.kb.PollKeysWithTS(); quit || key == control.K_ESCAPE {
		return "", 0, control.EndLoop
	}
	ts := control.TicksNS()
	sl, err := b.left.ReadStatus()
	if err != nil {
		return "", 0, err
	}
	sr, err := b.right.ReadStatus()
	if err != nil {
		return "", 0, err
	}
	// Report a button on the transition to "down" only, so a button held
	// from the previous screen is not taken as a new answer.
	downL := (sl^b.baseL)&leftGreenMask != 0
	downR := (sr^b.baseR)&rightGreenMask != 0
	pressL, pressR := downL && !b.downL, downR && !b.downR
	b.downL, b.downR = downL, downR
	switch {
	case pressL:
		return "left", ts, nil
	case pressR:
		return "right", ts, nil
	}
	return "", 0, nil
}

func (b *buttonResponder) desc() string {
	return fmt.Sprintf("MEG green buttons: left %s mask 0x%02x, right %s mask 0x%02x (baselines 0x%02x, 0x%02x)",
		leftGreenPort, leftGreenMask, rightGreenPort, rightGreenMask, b.baseL, b.baseR)
}

// drain forgets presses made before now (keyboard queue, buttons held down).
func drain(r responder) error {
	for i := 0; i < 1000; i++ {
		btn, _, err := r.poll()
		if err != nil {
			return err
		}
		if btn == "" {
			return nil
		}
	}
	return nil
}

// waitResponse polls until a button is pressed or deadlineNS passes. It
// returns "" and 0 on timeout.
func waitResponse(r responder, deadlineNS uint64) (string, uint64, error) {
	for {
		btn, ts, err := r.poll()
		if err != nil || btn != "" {
			return btn, ts, err
		}
		if deadlineNS > 0 && control.TicksNS() >= deadlineNS {
			return "", 0, nil
		}
		time.Sleep(pollInterval)
	}
}

// ---------------------------------------------------------------------------

func main() {
	meg := flag.Bool("meg", false, "MEG mode: triggers on "+triggerPort+", answers with the green buttons of the response pad (otherwise: keyboard arrows, no triggers)")
	photodiode := flag.String("photodiode", "auto", "photodiode square in the top-left corner: on, off, or auto (on with -meg)")
	photodiodeSize := flag.Float64("photodiode-size", control.DefaultPhotodiodeSize, "side of the photodiode square, in pixels")
	ttlMs := flag.Float64("ttl-ms", 0, "how long each trigger code stays on the lines, in ms (0 = 3 frames, 25 ms at 120 Hz)")
	startBlock := flag.Int("block", 1, "block to start from (to resume an interrupted session)")
	fontPath := flag.String("font", "", "TTF font file for the words (default: the bundled Inconsolata)")
	wordDeg := flag.Float64("word-deg", defaultWordDeg, "width of the widest word (and of the localizer's pictures), in degrees of visual angle")
	screenCm := flag.Float64("screen-cm", defaultScreenCm, "width of the projected screen image, in cm")
	distanceCm := flag.Float64("distance-cm", defaultDistanceCm, "viewing distance, in cm")
	auto := flag.Bool("auto", false, "answer automatically at random and start blocks without SPACE (timing checks)")
	outDir := flag.String("o", dataDir, "folder for the data files; a relative path is taken from the project folder")
	cbPath := flag.String("cb", "", "read the counterbalancing table from this file instead of the embedded copy")
	locFlag := flag.String("localizer", "train,1,2", "localizer blocks to run before the main task: none, or a comma list of train, 1, 2 (default: all, or none with -block > 1)")

	// The setup dialog (shown when -s is not given) offers the same default.
	exp := control.NewExperimentFromFlags("Pronouns", backgroundColor, textColor, 32,
		control.InfoField{Name: "output_dir", Label: "Results folder (relative to the Pronouns folder)", Default: dataDir})
	defer exp.End()

	// -o if given, else the dialog's folder, else the default; a relative
	// folder is taken from the project folder.
	dir := *outDir
	if chosen := strings.TrimSpace(exp.Info["output_dir"]); chosen != "" && !flagGiven("o") {
		dir = chosen
	}
	if !filepath.IsAbs(dir) {
		dir = filepath.Join(projectDir(), dir)
	}
	if err := moveDataFiles(exp.Data, dir); err != nil {
		exp.Fatal("data folder: %v", err)
	}
	log.Printf("pronouns %s", buildVersion())
	log.Printf("data will be saved to %s", exp.Data.FullPath)

	if *startBlock < 1 || *startBlock > nBlocks {
		exp.Fatal("-block %d: must be between 1 and %d", *startBlock, nBlocks)
	}

	// Trials.
	cb, cbSource := counterbalancingCSV, "embedded:counterbalancing/counterbalancing.csv"
	if *cbPath != "" {
		var err error
		if cb, err = os.ReadFile(*cbPath); err != nil {
			exp.Fatal("%v", err)
		}
		cbSource = *cbPath
	}
	trials, err := loadTrials(cb, exp.SubjectID)
	if err != nil {
		exp.Fatal("%s: %v", cbSource, err)
	}
	congruentKey := trials[0].fields["congruent_key"]

	// Localizer: all blocks, unless -localizer says otherwise; resuming the
	// main task (-block > 1) skips it unless -localizer is given.
	runLoc, err := parseLocalizerBlocks(*locFlag)
	if err != nil {
		exp.Fatal("%v", err)
	}
	if *startBlock > 1 && !flagGiven("localizer") {
		runLoc = [locBlocks]bool{}
	}
	locTrials, err := loadLocalizer(localizerCSV, exp.SubjectID)
	if err != nil {
		exp.Fatal("localizer/localizer.csv: %v", err)
	}
	log.Printf("localizer blocks (0 = training): %v", runLoc)
	log.Printf("subject %d: %d trials from %s, congruent = %s button", exp.SubjectID, len(trials), cbSource, congruentKey)

	// Hardware: one parallel port carries both the trigger codes (data lines)
	// and the right button (status lines), so it is opened once, here, and
	// shared by the onset marker and the button reader.
	var resp responder = keyboardResponder{exp.Keyboard}
	var ttlOut apparatus.MarkerOutput
	if *meg {
		trig := triggers.NewParallelPort(triggerPort)
		if err := trig.Open(); err != nil {
			exp.Fatal("trigger port: %v", err)
		}
		ttlOut = trig
		left := trig
		if leftGreenPort != triggerPort {
			left = triggers.NewParallelPort(leftGreenPort)
			if err := left.Open(); err != nil {
				exp.Fatal("left button port: %v", err)
			}
			defer left.Close()
		}
		b, err := newButtonResponder(exp.Keyboard, left, trig)
		if err != nil {
			exp.Fatal("response buttons: %v", err)
		}
		resp = b
	}
	if *auto { // after -meg: the triggers still go out
		resp = &autoResponder{kb: exp.Keyboard, rng: rand.New(rand.NewPCG(1, 2))}
	}
	usePhotodiode := *photodiode == "on" || (*photodiode == "auto" && *meg)
	if *photodiode != "on" && *photodiode != "off" && *photodiode != "auto" {
		exp.Fatal("-photodiode %q: on, off or auto", *photodiode)
	}
	if usePhotodiode || ttlOut != nil {
		desc := ""
		if ttlOut != nil {
			desc = "parallel port " + triggerPort
		}
		exp.Marker = apparatus.NewMarker(apparatus.MarkerOptions{
			Photodiode:  usePhotodiode,
			Size:        float32(*photodiodeSize),
			Output:      ttlOut,
			OutputDesc:  desc,
			TTLDuration: time.Duration(*ttlMs * float64(time.Millisecond)),
		})
		exp.Screen.SetMarker(exp.Marker)
		if ttlOut != nil {
			if err := ttlOut.AllLow(); err != nil {
				exp.Fatal("trigger port: %v", err)
			}
		}
	}
	exp.AddExperimentInfo("program: pronouns " + buildVersion())
	exp.AddExperimentInfo("counterbalancing: " + cbSource)
	exp.AddExperimentInfo("responses: " + resp.desc())
	exp.AddExperimentInfo(fmt.Sprintf("triggers: %v; photodiode: %v (%.0f px, top-left); ttl duration: %v",
		ttlOut != nil, usePhotodiode, *photodiodeSize, exp.Marker.TTLDuration()))
	exp.AddExperimentInfo(fmt.Sprintf("congruent_key: %s; start block: %d", congruentKey, *startBlock))
	exp.AddExperimentInfo(fmt.Sprintf("localizer blocks run (training, 1, 2): %v", runLoc))
	log.Print("responses: " + resp.desc())

	// The MEG projector's image is off center: in -meg fullscreen, move the
	// point every stimulus is positioned from. The photodiode square stays in
	// the screen's top-left corner.
	var shift float32
	if *meg && exp.Fullscreen {
		shift = megShiftX
		w, h := exp.DrawArea()
		center := control.Origin()
		center.X, center.Y = w/2-shift, h/2
		exp.Screen.CanvasOffset = &center
	}
	exp.AddExperimentInfo(fmt.Sprintf("stimuli shifted left by %.0f px", shift))
	log.Printf("stimuli shifted left by %.0f px", shift)

	// Stimuli, all built and uploaded before the run.
	// The word font is scaled so that the widest word of the session (main
	// task and localizer) spans -word-deg on a screen -screen-cm wide seen
	// from -distance-cm: measured at a reference size, then scaled.
	newFont := func(size float32) (*ttf.Font, error) {
		if *fontPath != "" {
			return control.FontFromFile(*fontPath, size)
		}
		return control.FontFromMemory(assets_embed.InconsolataFont, size)
	}
	drawW, _ := exp.DrawArea()
	targetPx := 2 * *distanceCm * math.Tan(*wordDeg/2*math.Pi/180) / *screenCm * float64(drawW)
	texts := map[string]bool{}
	for _, t := range trials {
		for _, w := range t.words {
			texts[w.text] = true
		}
	}
	for _, t := range locTrials {
		if t.modality == "word" {
			texts[t.item] = true
		}
	}
	const refSize = 100
	refFont, err := newFont(refSize)
	if err != nil {
		exp.Fatal("font: %v", err)
	}
	var refW float32
	for text := range texts {
		line := stimuli.NewTextLine(text, 0, 0, textColor)
		line.Font = refFont
		if err := stimuli.PreloadVisualOnScreen(exp.Screen, line); err != nil {
			exp.Fatal("measuring %q: %v", text, err)
		}
		refW = max(refW, line.Width)
		line.Unload()
	}
	refFont.Close()
	fontSize := float32(refSize * targetPx / float64(refW))
	font, err := newFont(fontSize)
	if err != nil {
		exp.Fatal("font: %v", err)
	}
	fix := newCross(fixSize, fixThickness, fixColor)
	fixCorrect := newCross(fixSize, fixThickness, correctColor)
	fixIncorrect := newCross(fixSize, fixThickness, incorrectColor)
	fixTimeout := newCross(fixSize, fixThickness, timeoutColor)
	dotCorrect := newDot(dotSize, correctColor)
	dotIncorrect := newDot(dotSize, incorrectColor)
	for _, v := range []stimuli.VisualStimulus{fix, fixCorrect, fixIncorrect, fixTimeout, dotCorrect, dotIncorrect} {
		if err := stimuli.PreloadVisualOnScreen(exp.Screen, v); err != nil {
			exp.Fatal("preloading the fixation cross: %v", err)
		}
	}
	for _, t := range trials {
		for i := range t.words {
			w := &t.words[i]
			w.stim = stimuli.NewTextLine(w.text, 0, 0, textColor)
			w.stim.Font = font
			if err := stimuli.PreloadVisualOnScreen(exp.Screen, w.stim); err != nil {
				exp.Fatal("preloading %q: %v", w.text, err)
			}
		}
	}

	// Instruction screens (instructions.go).
	instr, err := newInstructions(exp, congruentKey)
	if err != nil {
		exp.Fatal("instructions: %v", err)
	}

	// Localizer stimuli: the words in the main task's font and size; the
	// pictures span -word-deg, like the widest word.
	var locWordPx float32
	var longest string
	locWords := map[string]*stimuli.TextLine{}
	for _, t := range locTrials {
		if t.modality != "word" || locWords[t.item] != nil {
			continue
		}
		w := stimuli.NewTextLine(t.item, 0, 0, textColor)
		w.Font = font
		if err := stimuli.PreloadVisualOnScreen(exp.Screen, w); err != nil {
			exp.Fatal("preloading %q: %v", t.item, err)
		}
		locWords[t.item] = w
		if w.Width > locWordPx {
			locWordPx, longest = w.Width, t.item
		}
	}
	locPictures := map[string]*stimuli.Picture{}
	for _, t := range locTrials {
		if !runLoc[t.block] {
			continue
		}
		if t.modality == "word" {
			t.stim = locWords[t.item]
			continue
		}
		if locPictures[t.image] == nil {
			data, err := localizerImages.ReadFile("localizer/images/" + t.image)
			if err != nil {
				exp.Fatal("%v", err)
			}
			p := stimuli.NewPictureFromMemory(data, 0, 0)
			p.Width, p.Height = float32(targetPx), float32(targetPx)
			if err := stimuli.PreloadVisualOnScreen(exp.Screen, p); err != nil {
				exp.Fatal("preloading %s: %v", t.image, err)
			}
			locPictures[t.image] = p
		}
		t.stim = locPictures[t.image]
	}
	locSizes := fmt.Sprintf("words: %.1f pt, widest word %.0f px = %.1f deg (screen %.0f cm wide, %.0f px, seen from %.0f cm); widest localizer word %q %.0f px; pictures %.0f px",
		fontSize, targetPx, *wordDeg, *screenCm, drawW, *distanceCm, longest, locWordPx, targetPx)
	exp.AddExperimentInfo(locSizes)
	log.Print(locSizes)

	// Data: one row per event. Times are ms from the session start (the
	// start of the run) on the SDL clock that also stamps flips and key
	// presses; for words, the intended time is relative to the trial onset.
	exp.AddDataVariableNames([]string{
		"block_number", "trial_number", "event", "sentence", "position", "role", "word", "code",
		"time_ms", "trial_time_ms", "intended_trial_time_ms", "duration_ms",
		"response", "correct_key", "correct", "rt_ms",
		"cell", "congruent", "canonical_order", "pronoun_gender", "agent_gender", "pronoun_referent", "stimulus",
		"task", "modality", "match",
	})

	var t0 uint64
	ms := func(ns uint64) string {
		if ns == 0 {
			return "NA"
		}
		return strconv.FormatFloat(float64(int64(ns-t0))/1e6, 'f', 1, 64)
	}
	dur := func(a, b uint64) string {
		if a == 0 || b == 0 {
			return "NA"
		}
		return strconv.FormatFloat(float64(int64(b-a))/1e6, 'f', 1, 64)
	}
	addRow := func(t *trial, event string, w *word, code int, ts uint64, trialTime, intended, duration string,
		response, correct, rt string) {
		block, number, sentence, position, role, text := "NA", "NA", "NA", "NA", "NA", "NA"
		cell, cong, canon, pg, ag, ref, stim, ck := "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA"
		if t != nil {
			block, number = strconv.Itoa(t.block), strconv.Itoa(t.number)
			cell, ck = strconv.Itoa(t.cell), t.correctKey
			cong, canon = t.fields["congruent"], t.fields["canonical_order"]
			pg, ag, ref = t.fields["pronoun_gender"], t.fields["agent_gender"], t.fields["pronoun_referent"]
			stim = t.fields["stimulus"]
		}
		if w != nil {
			sentence, position = strconv.Itoa(w.sentence), strconv.Itoa(w.position)
			role, text = roleNames[w.role], w.text
		}
		exp.Data.Add(block, number, event, sentence, position, role, text, code,
			ms(ts), trialTime, intended, duration, response, ck, correct, rt,
			cell, cong, canon, pg, ag, ref, stim, "main", "NA", "NA")
	}
	// Localizer rows use the same columns: block_number 0 (training), 1 or 2,
	// the item in "word", times relative to the stimulus onset.
	addLocRow := func(t *locTrial, event string, code int, ts uint64, trialTime, duration, response, correct, rt string) {
		block, number, item, modality, match, ck := "NA", "NA", "NA", "NA", "NA", "NA"
		if t != nil {
			block, number, item, modality = strconv.Itoa(t.block), strconv.Itoa(t.number), t.item, t.modality
			match = t.fields["match"]
			if t.match {
				ck = "right"
			}
		}
		exp.Data.Add(block, number, event, "NA", "NA", "NA", item, code,
			ms(ts), trialTime, "NA", duration, response, ck, correct, rt,
			"NA", "NA", "NA", "NA", "NA", "NA", "NA", "localizer", modality, match)
	}

	// saveBlock writes the rows so far to disk at the end of every block, so
	// that a crash or a freeze loses at most the block in progress. (ESC, a
	// Go error or panic still save everything when the program ends.)
	saveBlock := func(what string) {
		if err := exp.Data.Save(); err != nil {
			log.Printf("saving the data after %s: %v (kept in memory, saved again later)", what, err)
		}
	}

	// showMarked presents v with code on the trigger lines and the photodiode
	// square, and returns the flip time.
	showMarked := func(v stimuli.VisualStimulus, code int) (uint64, error) {
		exp.Marker.Arm(byte(code))
		return exp.ShowTS(v)
	}

	// showScreens shows the named lists of instruction screens one by one; the
	// operator advances each with SPACE (not with -auto). The first screen
	// carries code; log writes the rows "pause" (first screen), "instruction"
	// (later ones) and "pause_end" (the SPACE that starts the block).
	showScreens := func(names []string, done, total, code int, log func(event string, code int, ts uint64, duration, response string)) error {
		var screens []*instructionScreen
		for _, name := range names {
			list, err := instr.screens(name, done, total)
			if err != nil {
				return err
			}
			screens = append(screens, list...)
		}
		for i, sc := range screens {
			var onset uint64
			if i == 0 {
				onset, err = showMarked(sc, code)
				log("pause", code, onset, "NA", "NA")
			} else {
				onset, err = exp.ShowTS(sc)
				log("instruction", 0, onset, "NA", "NA")
			}
			sc.Unload()
			if err != nil {
				return err
			}
			ts := control.TicksNS()
			if !*auto {
				exp.Keyboard.Clear()
				if _, ts, err = exp.Keyboard.GetKeyEventTS([]control.Keycode{control.K_SPACE}, -1); err != nil {
					return err
				}
			}
			if i == len(screens)-1 {
				log("pause_end", 0, ts, dur(onset, ts), "space")
			}
		}
		return nil
	}
	locLog := func(event string, code int, ts uint64, duration, response string) {
		addLocRow(nil, event, code, ts, "NA", duration, response, "NA", "NA")
	}
	mainLog := func(event string, code int, ts uint64, duration, response string) {
		addRow(nil, event, nil, code, ts, "NA", "NA", duration, response, "NA", "NA")
	}

	// The fixed part of every trial's stream: fixation, 6 words, break, 3 words.
	// The last word of sentence 1 is followed by its wordOffMs of fixation plus
	// the 1000 ms break; the adjective's stream ends when it goes off.
	buildStream := func(t *trial) []stimuli.StreamElement {
		el := []stimuli.StreamElement{{Stimulus: fix, DurationOn: fixationMs * time.Millisecond}}
		for i, w := range t.words {
			off := wordOffMs * time.Millisecond
			switch {
			case i == 5:
				off += fixationMs * time.Millisecond
			case i == len(t.words)-1:
				off = 0
			}
			el = append(el, stimuli.StreamElement{Stimulus: w.stim, DurationOn: wordOnMs * time.Millisecond, DurationOff: off})
		}
		return el
	}

	err = exp.Run(func() error {
		t0 = control.TicksNS()

		// Localizer.
		locRNG := rand.New(rand.NewPCG(uint64(exp.SubjectID), 3))
		ranLoc, lastLoc := false, -1
		for b := 0; b < locBlocks; b++ {
			if !runLoc[b] {
				continue
			}
			var block []*locTrial
			for _, t := range locTrials {
				if t.block == b {
					block = append(block, t)
				}
			}
			runtime.GC()
			// Before the first block run: the full instructions; then, before
			// training, its own screen; after training, a recap; otherwise a pause.
			var names []string
			switch {
			case !ranLoc:
				names = append(names, "localizer_intro")
				if b == 0 {
					names = append(names, "localizer_before_training")
				}
			case lastLoc == 0:
				names = append(names, "localizer_after_training")
			default:
				names = append(names, "localizer_pause")
			}
			if err := showScreens(names, 0, 0, codeLocBlock+b, locLog); err != nil {
				return err
			}
			ranLoc, lastLoc = true, b
			if err := drain(resp); err != nil {
				return err
			}

			timing, outcome, runErr := runLocalizerBlock(exp, block, resp, *auto, locRNG, fix, fixCorrect, fixIncorrect, dotCorrect, dotIncorrect)
			// Log what was presented, also after ESC.
			for i, tl := range timing {
				t, o := block[i], outcome[i]
				addLocRow(t, "loc_stimulus", t.code, tl.OnsetNS, "0.0", dur(tl.OnsetNS, tl.OffsetNS), "NA", "NA", "NA")
				rel := func(ns uint64) string { return dur(tl.OnsetNS, ns) }
				if o.pressNS != 0 {
					correct := "0"
					if t.match && !o.late {
						correct = "1"
					}
					event := "loc_response"
					if o.late {
						event = "loc_response_late"
					}
					addLocRow(t, event, 0, o.pressNS, rel(o.pressNS), "NA", "right", correct, rel(o.pressNS))
				}
				if o.feedback != 0 {
					event := map[int]string{codeLocHit: "loc_feedback_hit", codeLocFalseAlarm: "loc_feedback_false_alarm", codeLocMiss: "loc_feedback_miss"}[o.feedback]
					addLocRow(t, event, o.feedback, o.fbNS, rel(o.fbNS), "NA", "NA", "NA", "NA")
				}
			}
			if runErr != nil {
				return runErr
			}
			saveBlock(fmt.Sprintf("localizer block %d", b))
		}

		for _, t := range trials {
			if t.block < *startBlock {
				continue
			}

			// Pause (or instructions) before each block.
			if t.number == 1 {
				runtime.GC()
				if t.block == *startBlock {
					first := "main_intro_alone"
					if ranLoc {
						first = "main_intro_after_localizer"
					}
					if err := showScreens([]string{first, "main_intro"}, 0, 0, codeBlockStart+t.block, mainLog); err != nil {
						return err
					}
				} else if err := showScreens([]string{"main_pause"}, t.block-1, nBlocks, codeBlockStart+t.block, mainLog); err != nil {
					return err
				}
			}

			// Words.
			trialCode := codeTrialStart + t.number
			onFrame := func(ctx stimuli.FrameContext) error {
				if ctx.OnPhase && ctx.Frame == 0 {
					code := trialCode
					if ctx.Index > 0 {
						code = int(t.words[ctx.Index-1].code)
					}
					exp.Marker.Arm(byte(code))
				}
				// A word replaces the cross while it is on screen.
				if err := ctx.Screen.Clear(); err != nil {
					return err
				}
				if ctx.OnPhase && ctx.Index > 0 {
					return t.words[ctx.Index-1].stim.Draw(ctx.Screen)
				}
				return fix.Draw(ctx.Screen)
			}
			gc := debug.SetGCPercent(-1)
			_, timing, err := stimuli.PresentStreamOfStimuliHooks(exp.Screen, buildStream(t), 0, 0, onFrame, nil)
			if err != nil {
				debug.SetGCPercent(gc)
				return err
			}

			// Response window: from the flip that takes the adjective down.
			openNS, err := exp.ShowTS(fix)
			if err != nil {
				debug.SetGCPercent(gc)
				return err
			}
			if err := drain(resp); err != nil {
				debug.SetGCPercent(gc)
				return err
			}
			btn, pressNS, err := waitResponse(resp, openNS+responseWindowMs*1_000_000)
			if err != nil {
				debug.SetGCPercent(gc)
				return err
			}

			// Feedback.
			fb, code, correct := fixTimeout, codeTimeout, "NA"
			switch {
			case btn == t.correctKey:
				fb, code, correct = fixCorrect, codeCorrect, "1"
			case btn != "":
				fb, code, correct = fixIncorrect, codeIncorrect, "0"
			}
			fbNS, err := showMarked(fb, code)
			debug.SetGCPercent(gc)
			if err != nil {
				return err
			}

			// Log the trial.
			trialNS := timing[0].OnsetNS
			rel := func(ns uint64) string { return dur(trialNS, ns) }
			addRow(t, "fixation", nil, trialCode, trialNS, "0.0", "0", dur(timing[0].OnsetNS, timing[0].OffsetNS), "NA", "NA", "NA")
			for i := range t.words {
				w := &t.words[i]
				tl := timing[i+1]
				intended := fixationMs + (w.position-1)*(wordOnMs+wordOffMs)
				if w.sentence == 2 {
					intended += 6*(wordOnMs+wordOffMs) + fixationMs
				}
				// The on-phase ends at the next flip: the next element's onset,
				// or (for the adjective) the response-window flip.
				offNS := openNS
				if i+2 < len(timing) {
					offNS = timing[i+1].OffsetNS
				}
				addRow(t, "word", w, int(w.code), tl.OnsetNS, rel(tl.OnsetNS), strconv.Itoa(intended), dur(tl.OnsetNS, offNS), "NA", "NA", "NA")
			}
			respIntended := strconv.Itoa(2*fixationMs + 8*(wordOnMs+wordOffMs) + wordOnMs)
			addRow(t, "response_window", nil, 0, openNS, rel(openNS), respIntended, "NA", "NA", "NA", "NA")
			rt := "NA"
			if btn != "" {
				rt = dur(openNS, pressNS)
				addRow(t, "response", nil, 0, pressNS, rel(pressNS), "NA", "NA", btn, correct, rt)
			}
			event := map[int]string{codeCorrect: "feedback_correct", codeIncorrect: "feedback_incorrect", codeTimeout: "feedback_timeout"}[code]
			addRow(t, event, nil, code, fbNS, rel(fbNS), "NA", "NA", btn, correct, rt)

			if err := exp.Wait(feedbackMs - int((control.TicksNS()-fbNS)/1_000_000)); err != nil {
				return err
			}
			if t.number == 32 {
				saveBlock(fmt.Sprintf("block %d", t.block))
			}
		}

		ends, err := instr.screens("end", 0, 0)
		if err != nil {
			return err
		}
		onset, err := showMarked(ends[0], codeEnd)
		ends[0].Unload()
		if err != nil {
			return err
		}
		addRow(nil, "end", nil, codeEnd, onset, "NA", "NA", "NA", "NA", "NA", "NA")
		if err := exp.Wait(endScreenMs); err != nil {
			return err
		}
		return control.EndLoop
	})
	if err != nil && !control.IsEndLoop(err) {
		exp.Fatal("experiment error: %v", err)
	}
}

// newCross returns a "+" of the given width and line thickness, in pixels,
// as an image.
func newCross(size, thickness int, c control.Color) *stimuli.Picture {
	img := image.NewNRGBA(image.Rect(0, 0, size, size))
	lo, hi := (size-thickness)/2, (size+thickness)/2
	for y := 0; y < size; y++ {
		for x := 0; x < size; x++ {
			if (x >= lo && x < hi) || (y >= lo && y < hi) {
				img.SetNRGBA(x, y, color.NRGBA{c.R, c.G, c.B, 255})
			}
		}
	}
	var buf bytes.Buffer
	if err := png.Encode(&buf, img); err != nil {
		panic(err) // encoding an in-memory image cannot fail
	}
	return stimuli.NewPictureFromMemory(buf.Bytes(), 0, 0)
}

// newDot returns a filled disc of the given diameter, in pixels, as an image.
func newDot(size int, c control.Color) *stimuli.Picture {
	img := image.NewNRGBA(image.Rect(0, 0, size, size))
	r := float64(size) / 2
	for y := 0; y < size; y++ {
		for x := 0; x < size; x++ {
			if dx, dy := float64(x)+0.5-r, float64(y)+0.5-r; dx*dx+dy*dy <= r*r {
				img.SetNRGBA(x, y, color.NRGBA{c.R, c.G, c.B, 255})
			}
		}
	}
	var buf bytes.Buffer
	if err := png.Encode(&buf, img); err != nil {
		panic(err) // encoding an in-memory image cannot fail
	}
	return stimuli.NewPictureFromMemory(buf.Bytes(), 0, 0)
}

// buildVersion returns the git commit the program was built from (stamped by
// go build), with "+changes" if the working tree had uncommitted edits.
func buildVersion() string {
	info, ok := debug.ReadBuildInfo()
	if !ok {
		return "(unknown build)"
	}
	rev, dirty := "", false
	for _, s := range info.Settings {
		switch s.Key {
		case "vcs.revision":
			rev = s.Value
		case "vcs.modified":
			dirty = s.Value == "true"
		}
	}
	if rev == "" {
		return "(no commit: built with go run or outside git)"
	}
	if len(rev) > 7 {
		rev = rev[:7]
	}
	if dirty {
		rev += "+changes"
	}
	return rev
}

// projectDir is the Pronouns folder: the folder holding the executable, or
// the current folder when running a temporary executable built by go run.
func projectDir() string {
	exe, err := os.Executable()
	if err != nil || strings.HasPrefix(exe, os.TempDir()) || strings.Contains(exe, "go-build") {
		wd, _ := os.Getwd()
		return wd
	}
	return filepath.Dir(exe)
}

// flagGiven reports whether a flag was set on the command line.
func flagGiven(name string) bool {
	given := false
	flag.Visit(func(f *flag.Flag) { given = given || f.Name == name })
	return given
}

// moveDataFiles moves the session's data and info files to dir. The library
// creates them before the program can resolve the folder: in ~/goxpy_data, or
// in the dialog's folder taken relative to the current directory.
func moveDataFiles(d *results.DataFile, dir string) error {
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return err
	}
	for _, f := range []*results.OutputFile{d.OutputFile, d.InfoFile} {
		if err := f.Save(); err != nil {
			return err
		}
		dest := filepath.Join(dir, filepath.Base(f.FullPath))
		if err := os.Rename(f.FullPath, dest); err != nil {
			// Different file system: copy, then remove the original.
			b, rerr := os.ReadFile(f.FullPath)
			if rerr != nil {
				return rerr
			}
			if werr := os.WriteFile(dest, b, 0o644); werr != nil {
				return werr
			}
			if rmErr := os.Remove(f.FullPath); rmErr != nil {
				return rmErr
			}
		}
		if old := f.Directory; old != dir {
			_ = os.Remove(old) // only succeeds if the move left it empty
		}
		f.Directory, f.FullPath = dir, dest
	}
	return nil
}
