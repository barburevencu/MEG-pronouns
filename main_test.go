package main

import (
	"encoding/csv"
	"os"
	"strconv"
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
		if len(trials) != 160 {
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
	if len(table) != 64 {
		t.Fatalf("%d localizer stimulus codes in triggers.csv, expected 64", len(table))
	}

	want := []struct{ reps, matches int }{{1, 4}, {8, 32}, {8, 32}} // training, blocks 1 and 2, in order
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
			if _, err := localizerImages.ReadFile("localizer/images/" + tr.image); err != nil {
				t.Fatalf("subject %d: %v", s, err)
			}
		}
		direction := map[int]string{} // concept -> modality of the match in block 1
		for b, w := range want {
			block := byBlock[b]
			if len(block) != 64*w.reps {
				t.Fatalf("subject %d block %d: %d trials", s, b, len(block))
			}
			counts := map[key]int{}
			matches := 0
			for i, tr := range block {
				counts[key{tr.modality, tr.item}]++
				if wantMod := [2]string{"word", "image"}[i%2]; tr.modality != wantMod {
					t.Fatalf("subject %d block %d trial %d: %s, expected %s", s, b, tr.number, tr.modality, wantMod)
				}
				isMatch := i > 0 && block[i-1].concept == tr.concept
				if tr.match != isMatch {
					t.Fatalf("subject %d block %d trial %d: match column wrong", s, b, tr.number)
				}
				if tr.match {
					matches++
					if block[i-1].match {
						t.Fatalf("subject %d block %d trial %d: two matches in a row", s, b, tr.number)
					}
					switch b {
					case 1:
						direction[tr.concept] = tr.modality
					case 2:
						if direction[tr.concept] == tr.modality {
							t.Fatalf("subject %d: concept %d matched the same way in both blocks", s, tr.concept)
						}
					}
				}
			}
			if len(counts) != 64 {
				t.Fatalf("subject %d block %d: %d distinct stimuli", s, b, len(counts))
			}
			for k, n := range counts {
				if n != w.reps {
					t.Fatalf("subject %d block %d: %v shown %d times", s, b, k, n)
				}
			}
			if matches != w.matches {
				t.Fatalf("subject %d block %d: %d matches", s, b, matches)
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
	for _, name := range []string{"localizer_intro", "localizer_before_training", "localizer_after_training",
		"localizer_pause", "main_intro_after_localizer", "main_intro_alone", "main_intro", "main_pause", "end"} {
		list := screens[name]
		if len(list) == 0 {
			t.Fatalf("instructions/screens.json: no %q", name)
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
