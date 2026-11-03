package main

import (
	"encoding/csv"
	"os"
	"strconv"
	"strings"
	"testing"
)

// Every subject's trials load, and every word's code matches triggers.csv.
func TestTrialsMatchTriggerTable(t *testing.T) {
	f, err := os.Open("triggers/triggers.csv")
	if err != nil {
		t.Fatal(err)
	}
	defer f.Close()
	rows, err := csv.NewReader(f).ReadAll()
	if err != nil {
		t.Fatal(err)
	}
	col := map[string]int{}
	for i, h := range rows[0] {
		col[h] = i
	}
	type key struct{ role, sentence, position string }
	table := map[int]key{}
	for _, r := range rows[1:] {
		if r[col["role"]] == "" {
			continue
		}
		code, _ := strconv.Atoi(r[col["code"]])
		table[code] = key{r[col["role"]], r[col["sentence"]], r[col["position"]]}
	}

	for s := 1; s <= 30; s++ {
		trials, err := loadTrials(counterbalancingCSV, s)
		if err != nil {
			t.Fatalf("subject %d: %v", s, err)
		}
		if len(trials) != trainingTrials+nBlocks*trialsPerBlock {
			t.Fatalf("subject %d: %d trials", s, len(trials))
		}
		for _, tr := range trials {
			if len(tr.words) != 9 {
				t.Fatalf("subject %d: %d words in %q", s, len(tr.words), tr.fields["stimulus"])
			}
			for _, w := range tr.words {
				want, ok := table[int(w.code)]
				got := key{roleNames[w.role], strconv.Itoa(w.sentence), strconv.Itoa(w.position)}
				if !ok || want != got {
					t.Fatalf("subject %d, %q: code %d is %v in triggers.csv, program has %v",
						s, w.text, w.code, want, got)
				}
			}
		}
	}
}

// Every subject's localizer loads with the designed structure, and every
// stimulus code matches triggers.csv.
func TestLocalizer(t *testing.T) {
	f, err := os.Open("triggers/triggers.csv")
	if err != nil {
		t.Fatal(err)
	}
	defer f.Close()
	rows, err := csv.NewReader(f).ReadAll()
	if err != nil {
		t.Fatal(err)
	}
	col := map[string]int{}
	for i, h := range rows[0] {
		col[h] = i
	}
	type key struct{ modality, item string }
	table := map[int]key{}
	for _, r := range rows[1:] {
		if r[col["task"]] == "localizer" && r[col["modality"]] != "" {
			code, _ := strconv.Atoi(r[col["code"]])
			table[code] = key{r[col["modality"]], r[col["item"]]}
		}
	}
	if len(table) != 96 {
		t.Fatalf("%d localizer stimulus codes in triggers.csv, expected 96", len(table))
	}

	// training, blocks 1 and 2, in order: mini-blocks, showings of each
	// person/place per mini-block, animals per mini-block
	want := []struct{ minis, reps, animals int }{{2, 1, 4}, {8, 2, 8}, {8, 2, 8}}
	other := map[string]string{"word": "image", "image": "word"}
	for s := 1; s <= 30; s++ {
		trials, err := loadLocalizer(localizerCSV, s)
		if err != nil {
			t.Fatalf("subject %d: %v", s, err)
		}
		byBlock := map[int][]*locTrial{}
		for _, tr := range trials {
			byBlock[tr.block] = append(byBlock[tr.block], tr)
			if got := (key{tr.modality, tr.item}); table[tr.code] != got {
				t.Fatalf("subject %d: code %d is %v in triggers.csv, sequence has %v", s, tr.code, table[tr.code], got)
			}
			if tr.target != (tr.concept > 32) {
				t.Fatalf("subject %d block %d trial %d: target column wrong", s, tr.block, tr.number)
			}
			if _, err := localizerImages.ReadFile("localizer/images/" + tr.image); err != nil {
				t.Fatalf("subject %d: %v", s, err)
			}
		}
		// Odd subjects start training and block 1 with words, block 2 with
		// the other modality.
		first := map[bool]string{true: "word", false: "image"}[s%2 == 1]
		for b, w := range want {
			block := byBlock[b]
			size := 32*w.reps + w.animals
			if len(block) != w.minis*size {
				t.Fatalf("subject %d block %d: %d trials", s, b, len(block))
			}
			start := first
			if b == 2 {
				start = other[first]
			}
			animals := map[key]int{}
			lastAnimal := 0
			for mini := 0; mini < w.minis; mini++ {
				modality := start
				if mini%2 == 1 {
					modality = other[start]
				}
				counts := map[int]int{}
				for _, tr := range block[mini*size : (mini+1)*size] {
					if tr.miniblock != mini+1 || tr.modality != modality {
						t.Fatalf("subject %d block %d trial %d: mini-block %d %s, expected %d %s",
							s, b, tr.number, tr.miniblock, tr.modality, mini+1, modality)
					}
					counts[tr.concept]++
					if tr.target {
						animals[key{tr.modality, tr.item}]++
						if tr.number < 6 || lastAnimal > 0 && tr.number-lastAnimal < 7 || tr.number%size == 0 {
							t.Fatalf("subject %d block %d trial %d: animal too early, too close to the previous one, or last of its mini-block", s, b, tr.number)
						}
						lastAnimal = tr.number
					}
				}
				n := 0
				for k := 1; k <= 48; k++ {
					if k <= 32 && counts[k] != w.reps {
						t.Fatalf("subject %d block %d mini-block %d: concept %d shown %d times", s, b, mini+1, k, counts[k])
					}
					if k > 32 {
						n += counts[k]
					}
				}
				if n != w.animals {
					t.Fatalf("subject %d block %d mini-block %d: %d animals", s, b, mini+1, n)
				}
			}
			for i := 1; i < len(block); i++ {
				if block[i].concept == block[i-1].concept {
					t.Fatalf("subject %d block %d trial %d: same concept twice in a row", s, b, block[i].number)
				}
			}
			// Training: 8 different animals, each once; blocks 1 and 2: every
			// animal word and picture twice.
			wantN, wantDistinct := 2, 32
			if b == 0 {
				wantN, wantDistinct = 1, 8
			}
			if len(animals) != wantDistinct {
				t.Fatalf("subject %d block %d: %d distinct animal stimuli", s, b, len(animals))
			}
			names := map[string]bool{}
			for k, c := range animals {
				names[k.item] = true
				if c != wantN {
					t.Fatalf("subject %d block %d: %v shown %d times", s, b, k, c)
				}
			}
			if b == 0 && len(names) != 8 {
				t.Fatalf("subject %d training: an animal both as word and as picture", s)
			}
		}
	}
}

// Every list of instruction screens the program shows exists, and every
// picture they name is embedded.
func TestInstructionScreens(t *testing.T) {
	screens, err := loadScreens()
	if err != nil {
		t.Fatal(err)
	}
	for _, name := range []string{"main_intro_two_parts", "main_intro_alone", "main_intro",
		"main_before_training", "main_after_training", "main_ready", "main_pause",
		"localizer_intro_after_main", "localizer_intro_alone", "localizer_intro", "localizer_before_training",
		"localizer_after_training", "localizer_pause", "localizer_next_words", "localizer_next_images", "localizer_end", "end"} {
		list := screens[name]
		if len(list) == 0 {
			t.Fatalf("instructions/screens.json: no %q", name)
		}
		if strings.HasPrefix(name, "localizer_next_") && (len(list) != 1 || list[0].Image != "") {
			t.Fatalf("instructions/screens.json: %q must be one screen, without a picture", name)
		}
		for _, s := range list {
			if s.Image == "" {
				continue
			}
			files := []string{s.Image}
			if s.Image == "pad_congruent" {
				files = []string{"pad_congruent_left", "pad_congruent_right"}
			}
			for _, f := range files {
				if _, err := instructionFiles.ReadFile("instructions/" + f + ".png"); err != nil {
					t.Fatalf("%s: %v", name, err)
				}
			}
		}
	}
}
