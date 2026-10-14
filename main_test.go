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
