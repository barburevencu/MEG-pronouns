# Pronouns — MEG experiment

French pronoun resolution, word-by-word reading (RSVP) with a felicity judgment,
written with [goxpyriment](https://github.com/chrplr/goxpyriment).

The session opens with a **localizer**: a one-back task on the 32 nouns, words
and pictures alternating, each on screen for a full second with no blank in
between (a grey 1.92 cm fixation cross with a thin black outline stays on the pictures, and the words are drawn on top of it). The
participant presses the right green button when the stimulus is the same
concept as the previous one; the cross turns green on a correct press, red on a press on a
non-match or on a match left unanswered for 800 ms. A training block
of 64 trials (every word and picture once, 4 matches, ~1 min), then two blocks
of 512 (every word and picture 8 times, 32 matches, ~8.5 min each). Match
positions are random (never two in a row), every concept is matched once per
block, word→picture in one block and picture→word in the other. For decoding,
leave out the match trials and the trial after each match. Its words are in the
main task's font and size. Word size: the widest word of the session spans
8° of visual angle (on the 65 cm wide projected image, seen from 104 cm;
change with `-screen-cm`, `-distance-cm`, `-word-deg`), and the pictures are
8° wide too. On the 1920 px MEG screen that is about 430 px (≈ 72 pt); the
localizer's cross is 1.92 cm, about 57 px.

| File | What it is |
|---|---|
| `counterbalancing/stimuli.csv` | the word lists |
| `counterbalancing/make_counterbalancing.py` | writes `counterbalancing/counterbalancing.csv` (all subjects, 160 trials each, 5 blocks of 32) from `counterbalancing/stimuli.csv` |
| `triggers/make_trigger_table.py` | writes `triggers/triggers.csv`, every trigger code and what is on screen when it fires |
| `pictures/` | the image prompts (`faces_prompts.md` people, `places_prompts.md` places); the full-size PNGs are not committed |
| `localizer/make_localizer.py` | writes `localizer/localizer.csv` (all subjects' localizer sequences) and `localizer/images/` (the pictures shrunk to 512 px) from `pictures/` |
| `main.go` | the experiment; `counterbalancing/counterbalancing.csv` is embedded in the binary |
| `localizer.go` | the localizer; `localizer/localizer.csv` and `localizer/images/` are embedded |
| `instructions.go`, `instructions/screens.json` | the instruction screens (one or two sentences each, some with a picture), embedded; the operator advances each with SPACE |
| `instructions/make_button_images.py` | draws the response-pad pictures (`pad_*.png`) from `response_pad_reference.png`, green buttons highlighted and labelled |
| `instructions/make_preview.py` | draws the localizer example pictures and `instructions/preview.html`, every screen as the program shows it (run after editing `screens.json`) |
| `main_test.go` | checks that every subject loads, every word code matches `triggers/triggers.csv`, and every localizer sequence has the designed structure |
| `demo/pronouns_demo.html` | standalone browser demo to share: instructions (one short screen at a time, SPACE), 32 localizer trials (→ for a match) and 10 pronoun trials of subject 1 (← / →); trials and pictures are embedded |
| `.github/workflows/pages.yml` | publishes the demo at https://barburevencu.github.io/MEG-pronouns/ whenever it changes on `main` |
| `demo/make_demo.py` | refreshes the demo's localizer sequence and pictures (run after changing the stimuli or the pictures) |
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
./pronouns -s 1 -meg -block 3      # resume at block 3 after a crash (no localizer, no instructions)
./pronouns -s 1 -meg -localizer 2  # localizer block 2 only, then the main task
./pronouns -s 1 -meg -block 1     # main task only (same as -localizer none)
./pronouns -w -s 1 -auto -block 5  # unattended timing check, random answers
```

| Flag | Meaning |
|---|---|
| `-s N` | subject (must be in the counterbalancing table) |
| `-meg` | triggers on `/dev/parport1`, answers with the green buttons of the response pad |
| `-block N` | start the main task at block N (after a crash): the localizer is skipped (`-block 1` = `-localizer none`); with N > 1 the instructions are skipped too, and the session opens on block N's pause screen (`-localizer` still runs localizer blocks if given) |
| `-localizer LIST` | localizer blocks to run: `none`, or a comma list of `train`, `1`, `2` (default all, or none with `-block`) |
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
from `instructions/screens.json`. The operator advances every screen with
SPACE; the last one starts the block. ESC aborts at any time; what
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
the item in `word`, `modality` and `match`; events `loc_stimulus`,
`loc_response` (RT from the stimulus onset; `loc_response_late` after a missed
deadline), `loc_feedback_hit`, `loc_feedback_false_alarm`, `loc_feedback_miss`.
Localizer trigger codes: word of concept k = k (1-32), picture = 32 + k, pause
screens 206-208, feedback 211-213; they overlap main-task codes, so split the
recording at the main task's first pause code (201-205).

The data are written to disk at the end of every block (localizer and main
task), so a crash or a frozen computer loses at most the block in progress;
on ESC or a program error, everything presented is saved.

`data/Pronouns_sub-NNN_date-….csv` in the project folder (beside the executable; `-o FOLDER` to change), one row per event (`pause`,
`fixation`, `word`, `response_window`, `response`, `feedback_*`, `end`), with
the code sent, the time on the SDL clock (ms from the start of the run), the
time within the trial and its intended value, word on-durations, the answer,
its correctness and RT (from the adjective's onset: presses count as soon as it appears, until 3 s after it goes off), and the trial's
condition columns. The `-info.txt` beside it has the session metadata and the
marker statistics (codes sent, write errors).
