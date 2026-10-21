// Instruction screens: one or two sentences each, with a picture under the
// text on some (the response pad, or a localizer example). The texts are in
// instructions/screens.json; instructions/preview.html shows them all.

package main

import (
	"bytes"
	"embed"
	"encoding/json"
	"fmt"
	"image"
	_ "image/png"
	"strings"

	"github.com/Zyko0/go-sdl3/sdl"
	"github.com/Zyko0/go-sdl3/ttf"
	"github.com/chrplr/goxpyriment/apparatus"
	"github.com/chrplr/goxpyriment/assets_embed"
	"github.com/chrplr/goxpyriment/control"
	"github.com/chrplr/goxpyriment/stimuli"
)

//go:embed instructions/screens.json instructions/pad_*.png instructions/example_*.png
var instructionFiles embed.FS

// Proportions of the screen, as in instructions/preview.html.
const (
	instrTextWidth  = 0.55       // longest line, of the drawing-area width
	instrFontHeight = 13.0 / 270 // font size, of the drawing-area height
	instrPadHeight  = 140.0 / 270
	instrExHeight   = 95.0 / 270
	instrGap        = 0.03 // between text and picture, of the height
)

type screenSpec struct {
	Text  string `json:"text"`
	Image string `json:"image"`
}

// loadScreens reads instructions/screens.json: lists of screens by name.
func loadScreens() (map[string][]screenSpec, error) {
	raw, err := instructionFiles.ReadFile("instructions/screens.json")
	if err != nil {
		return nil, err
	}
	var all map[string]json.RawMessage
	if err := json.Unmarshal(raw, &all); err != nil {
		return nil, fmt.Errorf("instructions/screens.json: %w", err)
	}
	screens := map[string][]screenSpec{}
	for name, v := range all {
		if strings.HasPrefix(name, "_") {
			continue
		}
		var list []screenSpec
		if err := json.Unmarshal(v, &list); err != nil {
			return nil, fmt.Errorf("instructions/screens.json, %s: %w", name, err)
		}
		screens[name] = list
	}
	return screens, nil
}

// instructionScreen is one screen: the text, and the picture under it.
type instructionScreen struct {
	stimuli.BaseVisual
	text *stimuli.TextBox
	pic  *stimuli.Picture // nil if none
}

func (s *instructionScreen) Draw(screen *apparatus.Screen) error {
	if err := s.text.Draw(screen); err != nil {
		return err
	}
	if s.pic != nil {
		return s.pic.Draw(screen)
	}
	return nil
}

func (s *instructionScreen) Present(screen *apparatus.Screen, clear, update bool) error {
	return stimuli.PresentDrawable(s, screen, clear, update)
}

func (s *instructionScreen) Unload() error { return s.text.Unload() }

// instructions builds the screens; pictures are loaded once and kept.
type instructions struct {
	exp          *control.Experiment
	specs        map[string][]screenSpec
	font         *ttf.Font
	pics         map[string]*stimuli.Picture
	congruentKey string
}

func newInstructions(exp *control.Experiment, congruentKey string) (*instructions, error) {
	specs, err := loadScreens()
	if err != nil {
		return nil, err
	}
	_, h := exp.DrawArea()
	font, err := control.FontFromMemory(assets_embed.InconsolataFont, h*instrFontHeight)
	if err != nil {
		return nil, err
	}
	return &instructions{exp: exp, specs: specs, font: font, pics: map[string]*stimuli.Picture{}, congruentKey: congruentKey}, nil
}

// screens returns the named list, with {natural}/{odd} set from the
// subject's mapping and {done}/{total} from the arguments.
func (in *instructions) screens(name string, done, total int) ([]*instructionScreen, error) {
	specs, ok := in.specs[name]
	if !ok {
		return nil, fmt.Errorf("instructions/screens.json has no %q", name)
	}
	side := map[string]string{"left": "gauche", "right": "droite"}
	other := map[string]string{"left": "right", "right": "left"}[in.congruentKey]
	fill := strings.NewReplacer("{natural}", side[in.congruentKey], "{odd}", side[other],
		"{done}", fmt.Sprint(done), "{total}", fmt.Sprint(total))
	var out []*instructionScreen
	for _, sp := range specs {
		s, err := in.build(fill.Replace(sp.Text), sp.Image)
		if err != nil {
			return nil, err
		}
		out = append(out, s)
	}
	return out, nil
}

func (in *instructions) build(text, img string) (*instructionScreen, error) {
	w, h := in.exp.DrawArea()
	box := stimuli.NewTextBox(text, int32(instrTextWidth*w), sdl.FPoint{}, textColor)
	box.Font = in.font
	if err := stimuli.PreloadVisualOnScreen(in.exp.Screen, box); err != nil {
		return nil, err
	}
	s := &instructionScreen{text: box}
	if img == "" {
		return s, nil
	}
	if img == "pad_congruent" {
		img += "_" + in.congruentKey
	}
	pic := in.pics[img]
	if pic == nil {
		data, err := instructionFiles.ReadFile("instructions/" + img + ".png")
		if err != nil {
			return nil, err
		}
		cfg, _, err := image.DecodeConfig(bytes.NewReader(data))
		if err != nil {
			return nil, fmt.Errorf("%s.png: %w", img, err)
		}
		frac := float32(instrExHeight)
		if strings.HasPrefix(img, "pad_") {
			frac = instrPadHeight
		}
		pic = stimuli.NewPictureFromMemory(data, 0, 0)
		pic.Height = frac * h
		pic.Width = pic.Height * float32(cfg.Width) / float32(cfg.Height)
		if err := stimuli.PreloadVisualOnScreen(in.exp.Screen, pic); err != nil {
			return nil, err
		}
		in.pics[img] = pic
	}
	// Text above, picture below, the whole block centred vertically (y up).
	gap := instrGap * h
	total := box.Height + gap + pic.Height
	box.SetPosition(sdl.FPoint{Y: total/2 - box.Height/2})
	s.pic = &stimuli.Picture{BaseVisual: stimuli.BaseVisual{Position: sdl.FPoint{Y: total/2 - box.Height - gap - pic.Height/2}},
		Texture: pic.Texture, Width: pic.Width, Height: pic.Height}
	return s, nil
}
