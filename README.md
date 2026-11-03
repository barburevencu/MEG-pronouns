# Pronouns — MEG experiment

French pronoun resolution, word-by-word reading (RSVP) with a felicity judgment,
written with [goxpyriment](https://github.com/chrplr/goxpyriment).

The session opens with the **main task** (pronoun pairs and felicity judgments),
then a **localizer**: an animal-detection task on words and pictures of the 32
nouns (16 people, 16 places) and of 16 animals (`localizer/animals.csv`, 8
masculine and 8 feminine, matched to the people and places in length and in
film and book frequency: mean 8.1 letters, log frequencies 0.69 and 0.77 vs.
0.66 and 0.77). Each stimulus is on for 600 ms, then 200 ms of fixation. The
stimuli come in mini-blocks of one modality, words and pictures alternating,
with a 10 s screen between two mini-blocks announcing the next modality
(« Maintenant : des mots. » / « des images. ») and counting down the seconds;
in word mini-blocks the main task's small cross stays on with the word drawn on
top, in picture mini-blocks a grey 1.92 cm cross with a thin black outline sits
on top of the picture and stays on in the blank. The participant presses the
right green button on an animal; a press 200–1200 ms after an animal's onset is
a hit. No press gets feedback, in training either: the screen after each
mini-block gives the percentage of animals hit. A training block of 72 trials (a word and a picture mini-block of 36:
every person and place once, 4 animals; ~1.1 min), then two blocks of 576 (8
mini-blocks of 72: every person and place twice, 8 animals; each animal word
and picture twice per block; ~8.8 min each). Animals are 11% of the trials,
never in a block's first 5 trials or a mini-block's last, with at least 6 other trials
between two of them; the same concept never comes twice in a row. Odd subjects
start training and block 1 with words, even subjects with pictures; block 2
starts with the other modality. Until the animal pictures exist, the program
shows placeholders (the name on a grey square; add `pictures/<animal>.png` and
rerun `make_localizer.py`). Its words are in the
main task's font and size. Word size: the widest word of the session spans
8° of visual angle (on the 65 cm wide projected image, seen from 104 cm;
change with `-screen-cm`, `-distance-cm`, `-word-deg`), and the pictures are
8° wide too. On the 1920 px MEG screen that is about 430 px (≈ 72 pt); the
localizer's large cross is 1.92 cm, about 57 px.

| File | What it is |
|---|---|
| `counterbalancing/stimuli.csv` | the word lists |
| `counterbalancing/make_counterbalancing.py` | writes `counterbalancing/counterbalancing.csv` (all subjects, 6 blocks of 40: 32 main trials + 8 fillers) from `counterbalancing/stimuli.csv` and `counterbalancing/fillers.csv` |
| `counterbalancing/fillers.csv` | the 48 filler items: 12 person-adjectives, each natural after 2 verbs and odd after 2 others, with an example sentence |
| `triggers/make_trigger_table.py` | writes `triggers/triggers.csv`, every trigger code and what is on screen when it fires |
| `pictures/` | the image prompts (`faces_prompts.md` people, `places_prompts.md` places, `animals_prompts.md` the localizer's animals); the full-size PNGs are not committed |
| `localizer/animals.csv` | the 16 animals, with gender, length and log frequencies (Lexique 3.83, as in `stimuli.csv`) |
| `localizer/make_localizer.py` | writes `localizer/localizer.csv` (all subjects' localizer sequences) and `localizer/images/` (the pictures shrunk to 512 px, placeholders for animals without a picture) from `pictures/` |
| `main.go` | the experiment; `counterbalancing/counterbalancing.csv` is embedded in the binary |
| `localizer.go` | the localizer; `localizer/localizer.csv` and `localizer/images/` are embedded |
| `instructions.go`, `instructions/screens.json` | the instruction screens (one or two sentences each, some with a picture), embedded; the operator advances each with SPACE |
| `instructions/make_button_images.py` | draws the response-pad pictures (`pad_*.png`) from `response_pad_reference.png`, green buttons highlighted and labelled |
| `instructions/make_preview.py` | draws `instructions/preview.html`, every screen as the program shows it (run after editing `screens.json`) |
| `main_test.go` | checks that every subject loads, every word code matches `triggers/triggers.csv`, and every localizer sequence has the designed structure |
| `demo/pronouns_demo.html` | standalone browser demo to share: instructions (one short screen at a time, SPACE), 72 localizer trials (a localizer training block; → on an animal) and 10 pronoun trials of subject 1 (← / →); trials and pictures are embedded. Key 0 in its menu shows the MEG program's instruction screens, in session order (→ / ← to browse) |
| `.github/workflows/pages.yml` | publishes the demo at https://barburevencu.github.io/MEG-pronouns/ whenever it changes on `main` |
| `demo/make_demo.py` | refreshes the demo's localizer sequence and pictures, and its copy of the MEG instruction screens (run after changing the stimuli, the pictures or `instructions/screens.json`) |
| `tools/buttontest` | prints which parallel-port pin each response-pad button moves (run on the MEG computer: `go build -o buttontest ./tools/buttontest && ./buttontest`) |
| `data/` | session data (created by the experiment) |

The Python scripts can be run from any folder. After changing
`counterbalancing/counterbalancing.csv`, rebuild (it is embedded), or pass it with `-cb`.

## Build

```bash
go build -o pronouns .
```

goxpyriment is pinned to an unreleased commit of its main branch (the onset
marker is not in a release yet). On a machine without a Go module cache, if
`go build` complains about the checksum database, run once:

```bash
GONOSUMDB=github.com/chrplr/goxpyriment GOPROXY=direct go mod download
```

## On the MEG computer: download, don't build

Do not run `go build` on the MEG computer: compiling needs 1-2 GB of memory
and froze it once. Every push to `main` makes GitHub build the Linux programs
(`.github/workflows/rig.yml`, 1-2 minutes) and publish them as the release
`rig`. In the project folder on the MEG computer:

```bash
curl -L -o pronouns-linux https://github.com/barburevencu/MEG-pronouns/releases/download/rig/pronouns-linux && chmod +x pronouns-linux
./pronouns-linux -s 1 -meg
```

The program prints the commit it was built from (`pronouns d14ff6a`) at
startup and in the `-info.txt` file; compare it with the latest commit on
GitHub. `buttontest-linux` is in the same release.

## Run

```bash
./pronouns -w -s 1                 # windowed test, answers with ← / →
./pronouns -s 1 -meg               # MEG session, subject 1
./pronouns -s 1 -meg -block 3      # resume the main task at block 3 after a crash, then the localizer
./pronouns -s 1 -meg -localizer none          # main task only
./pronouns -s 1 -meg -main=false -localizer 2 # localizer block 2 only (crash during the localizer)
./pronouns -w -s 1 -auto -block 6 -localizer none  # unattended timing check, random answers
```

| Flag | Meaning |
|---|---|
| `-s N` | subject (must be in the counterbalancing table) |
| `-meg` | triggers on `/dev/parport1`, answers with the green buttons of the response pad |
| `-block N` | start the main task at block N (after a crash), without the training block; with N > 1 its instructions are skipped too, and the session opens on block N's pause screen. The localizer still follows (add `-localizer none` to skip it) |
| `-localizer LIST` | localizer blocks to run after the main task: `none`, or a comma list of `train`, `1`, `2` (default all) |
| `-main=false` | skip the main task: run only the localizer blocks chosen with `-localizer` |
| `-photodiode on/off/auto` | white square top-left at every trigger; `auto` = on with `-meg` |
| `-photodiode-size N` | its side, in pixels (default 100) |
| `-ttl-ms N` | trigger pulse width (default 0 = 3 frames, 25 ms at 120 Hz) |
| `-font FILE.ttf` | word font (default: bundled Inconsolata) |
| `-word-deg N` | width of the widest word and of the localizer's pictures, in degrees (default 8) |
| `-screen-cm N`, `-distance-cm N` | width of the projected image and viewing distance (default 65 and 104, the MEG's); windowed (`-w`), the window's width stands for the screen's |
| `-o FOLDER` | where to save the data; relative paths are taken from the project folder (default `data`) |
| `-cb FILE` | counterbalancing table from disk instead of the embedded copy |
| `-auto` | random answers, blocks start without SPACE (timing checks; works with `-meg`) |
| `-w` | windowed (never for recording) |

Before each block come instruction screens (all of them before the first
block of each part, a short pause screen with the response pad otherwise),
from `instructions/screens.json`. The participant advances them with the right
green button (→ on the keyboard; SPACE works too); presses in the first 0.5 s of a screen are ignored. The last screen
before a block waits for the operator's SPACE only, and the
block starts after a countdown (3, 2, 1, one second each, in the words' font). ESC aborts at any time; what
was presented so far is saved.

## MEG rig (Linux)

- Triggers: data lines of `/dev/parport1`. Buttons: status lines, left green
  on pin 15 of `/dev/parport0`, right green on pin 12 of `/dev/parport1`,
  measured with `tools/buttontest` (Pushmi's table swaps left green and right
  blue). Rest of the pad: left yellow pin 13 and right blue pin 10 of
  `/dev/parport0`, right yellow pin 10 of `/dev/parport1`, left blue pin 10 of
  `/dev/parport2`.
- The user needs to be in the `lp` group, `ppdev` loaded, and the `lp`
  printer module unloaded (`sudo rmmod lp`), otherwise opening the port can
  hang. See goxpyriment's `triggers/notes/parallel.md`.
- With `-meg` in fullscreen, every stimulus is drawn 330 px left of the
  screen center (`megShiftX` in `main.go`), to match the projector; the
  photodiode square stays in the top-left corner. Windowed (`-w`) or without
  `-meg`, nothing is shifted.
- ProPixx at 120 Hz: run `ProPixxsetup.sh` (Pushmi) first.
- Read the codes from STI001–STI008, or STI101 with `mask=255`: the buttons
  are recorded on their own STI lines.
- The trigger fires when the frame is handed to the display, 1–3 frames before
  the photons; measure that lag once with the photodiode and subtract it.

## Data

Localizer rows have `task` = `localizer`, `block_number` 0 (training), 1 or 2,
the item in `word`, `modality`, `miniblock` (1-8), `category` (`person`,
`place`, `animal`) and `target` (1 for an animal); events
`loc_miniblock_screen` (the screen before a mini-block, on its first trial's
row), `loc_stimulus` (its
measured on-duration; for an animal, `correct` 1 if hit, 0 if missed, and the
RT), `loc_response` (every press, on the animal it hit, correct 1, or else on
the trial on screen, a false alarm, correct 0; time and RT from that trial's
onset). Localizer trigger codes: word of person/place k
= k (1-32), its picture = 32 + k, word of animal a = 64 + a (65-80), its
picture = 80 + a (81-96), pause screens 207-209,
screen before a word / picture mini-block 250 / 251; they overlap
main-task codes, so split the recording at the localizer's first pause code
(207-209).

The data are written to disk at the end of every block (localizer and main
task), so a crash or a frozen computer loses at most the block in progress;
on ESC or a program error, everything presented is saved.

`data/Pronouns_sub-NNN_date-….csv` in the project folder (beside the executable; `-o FOLDER` to change), one row per event (`pause`,
`countdown`, `fixation`, `word`, `response_window`, `response`, `feedback_*`, `iti`, `end`), with
the code sent, the time on the SDL clock (ms from the start of the run), the
time within the trial and its intended value, word on-durations, the answer,
its correctness and RT (from the adjective's onset: presses count as soon as it appears, until 3 s after that onset), and the trial's
condition columns: `trial_type` (`main` or `filler`), `judgment` (`natural` or `odd`, the correct answer), and for main trials
`congruent`, `pronoun_referent` and the rest.

**Training.** The main task opens with a training block (block 0, pause code 210):
20 trials, one more set of 16 main trials (one per condition cell, with a random half of
each adjective list) and 4 of the 48 fillers (2 natural, 2 odd, gender and word order crossed,
rotating over subjects), with a main trial first and never two fillers in a row, and feedback as
in the real blocks. No training sentence repeats the first sentence of a trial in the real blocks.
`-block N` skips it.

**Fillers.** Each block has 8 fillers among its 32 main trials, at random positions,
never two in a row. They look like main trials, but the pronoun always refers to the person,
and the judgment depends on whether the adjective fits the verb ("Le marin courait… Il était
assis" is odd). Each block has one filler per judgment × person's gender × word order; items rotate over
blocks and versions across subjects (a cycle of 24), and every person and place is used 3 times.
Filler words have their own trigger codes: 214 + 4 × (role − 1) + 2 × canonical + natural (214–249),
so they can be left out of main-trial analyses by code or by `trial_type`.

*How the filler rotation works.* In each block the 4 natural fillers take the 4 versions
(Il/Elle × two word orders), so 6 blocks give 24 slots for the 24 natural items; the 24 odd
items have 24 slots of their own. Subject 1 puts item *i* in slot *i*; every next subject moves
every item one slot on (subject *n*: slot *i + n − 1*, wrapping after 24). Over 24 subjects each
item fills every slot once: every block 4 times, every version 6 times. The order of versions
shifts by one from block to block, so items do not keep the same version; an adjective's two
natural (or two odd) items are 12 slots, i.e. 3 blocks, apart; and odd items run 2 blocks ahead
of natural ones, so an adjective's 4 uses fall in 4 different blocks. Subject 25 starts the cycle
again: the design is exactly balanced for 24 or 48 subjects; with 30, subjects 25–30 repeat
subjects 1–6. The `-info.txt` beside it has the session metadata and the
marker statistics (codes sent, write errors).
