# Pronouns — MEG experiment

French pronoun resolution, word-by-word reading (RSVP) with a felicity judgment,
written with [goxpyriment](https://github.com/chrplr/goxpyriment).

| File | What it is |
|---|---|
| `counterbalancing/stimuli.csv` | the word lists |
| `counterbalancing/make_counterbalancing.py` | writes `counterbalancing/counterbalancing.csv` (all subjects, 160 trials each, 5 blocks of 32) from `counterbalancing/stimuli.csv` |
| `triggers/make_trigger_table.py` | writes `triggers/triggers.csv`, every trigger code and what is on screen when it fires |
| `main.go` | the experiment; `counterbalancing/counterbalancing.csv` is embedded in the binary |
| `main_test.go` | checks that every subject loads and every word code matches `triggers/triggers.csv` |
| `demo/pronouns_demo.html` | standalone browser demo (10 trials of subject 1, ← / →) to share; trials are embedded, so refresh it after changing the stimuli |
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

## Run

```bash
./pronouns -w -s 1                 # windowed test, answers with ← / →
./pronouns -s 1 -meg               # MEG session, subject 1
./pronouns -s 1 -meg -block 3      # resume at block 3 after a crash
./pronouns -w -s 1 -auto -block 5  # unattended timing check, random answers
```

| Flag | Meaning |
|---|---|
| `-s N` | subject (must be in the counterbalancing table) |
| `-meg` | triggers on `/dev/parport1`, answers with the green buttons of the response pad |
| `-block N` | start at block N; the first screen is then the instructions |
| `-photodiode on/off/auto` | white square top-left at every trigger; `auto` = on with `-meg` |
| `-photodiode-size N` | its side, in pixels (default 100) |
| `-ttl-ms N` | trigger pulse width (default 0 = 3 frames, 25 ms at 120 Hz) |
| `-font FILE.ttf`, `-font-size N` | word font (default: bundled Inconsolata, 48 pt) |
| `-o FOLDER` | where to save the data; relative paths are taken from the project folder (default `data`) |
| `-cb FILE` | counterbalancing table from disk instead of the embedded copy |
| `-auto` | random answers, blocks start without SPACE (timing checks; works with `-meg`) |
| `-w` | windowed (never for recording) |

The session opens on the instructions; before each later block a pause screen
(with a reminder of the buttons) is shown. The operator starts every block,
the first included, with SPACE. ESC aborts at any time; what
was presented so far is saved.

## MEG rig (Linux)

- Triggers: data lines of `/dev/parport1`. Buttons: status lines, left green
  on pin 10 of `/dev/parport0`, right green on pin 12 of `/dev/parport1` (as in
  Pushmi). The button pins are an inference from Pushmi's expyriment code and
  must be checked on the rig.
- The user needs to be in the `lp` group, `ppdev` loaded, and the `lp`
  printer module unloaded (`sudo rmmod lp`), otherwise opening the port can
  hang. See goxpyriment's `triggers/notes/parallel.md`.
- ProPixx at 120 Hz: run `ProPixxsetup.sh` (Pushmi) first.
- Read the codes from STI001–STI008, or STI101 with `mask=255`: the buttons
  are recorded on their own STI lines.
- The trigger fires when the frame is handed to the display, 1–3 frames before
  the photons; measure that lag once with the photodiode and subtract it.

## Data

`data/Pronouns_sub-NNN_date-….csv` in the project folder (beside the executable; `-o FOLDER` to change), one row per event (`pause`,
`fixation`, `word`, `response_window`, `response`, `feedback_*`, `end`), with
the code sent, the time on the SDL clock (ms from the start of the run), the
time within the trial and its intended value, word on-durations, the answer,
its correctness and RT (from the adjective's offset), and the trial's
condition columns. The `-info.txt` beside it has the session metadata and the
marker statistics (codes sent, write errors).
