"""Write triggers.csv: every MEG trigger code, the event it marks, what is on
screen from that moment, and when it happens within a trial.

Word codes are 16 * role + cell, where cell packs the trial's condition:
    bit 0 congruent, bit 1 canonical order, bit 2 pronoun feminine, bit 3 agent feminine.
Times are ms from the trial's fixation onset (code 160 + trial_number).

The localizer (task "localizer", before the main task) reuses codes 1-64 for its
stimuli: word of concept k = k, picture = 32 + k, concepts numbered as in
stimuli.csv (people 1-16, places 17-32). Its blocks open with codes 206-208, so
the two tasks are separate segments of the recording.
"""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent

WORD_ON, WORD_SOA = 500, 500  # each word stays on until the next
FIX = 1000                     # initial fixation and inter-sentence break
RESPONSE_WINDOW = 3000
FEEDBACK = 500
LOC_ON, LOC_SOA, LOC_DEADLINE = 1000, 1000, 800

# role: (name, sentence, position if canonical, position if non-canonical)
ROLES = {
    1: ("det_subj", 1, 1, 4),
    2: ("noun_subj", 1, 2, 5),
    3: ("verb", 1, 3, 6),
    4: ("dans", 1, 4, 1),
    5: ("det_place", 1, 5, 2),
    6: ("noun_place", 1, 6, 3),
    7: ("pronoun", 2, 1, 1),
    8: ("etait", 2, 2, 2),
    9: ("adjective", 2, 3, 3),
}
EXAMPLE = {  # canonical / non-canonical words, for the on_screen column
    "det_subj": ("Le", "le"), "noun_subj": ("mécanicien",) * 2, "verb": ("rêvait",) * 2,
    "dans": ("dans", "Dans"), "det_place": ("la",) * 2, "noun_place": ("classe",) * 2,
    "pronoun": ("Il/Elle",) * 2, "etait": ("était",) * 2, "adjective": ("<adjective>",) * 2,
}

S2_START = FIX + 6 * WORD_SOA + FIX          # 5000
RESP_OPEN = S2_START + 2 * WORD_SOA + WORD_ON  # 6500


def word_onset(sentence, position):
    start = FIX if sentence == 1 else S2_START
    return start + (position - 1) * WORD_SOA


rows = []


def add(code, event, on_screen, onset, duration, task="main", **cond):
    rows.append({"task": task, "code": code, "event": event, "on_screen": on_screen,
                 "onset_ms": onset, "duration_ms": duration, **cond})


for t in range(1, 33):
    add(160 + t, f"trial_start (trial_number={t})", "fixation cross (light grey)", 0, FIX)

for role, (name, sentence, pos_can, pos_non) in ROLES.items():
    for cell in range(16):
        congruent, canonical = cell & 1, cell >> 1 & 1
        pron_f, agent_f = cell >> 2 & 1, cell >> 3 & 1
        pos = pos_can if canonical else pos_non
        add(16 * role + cell, f"word: {name}",
            f"'{EXAMPLE[name][0 if canonical else 1]}' (no fixation cross)",
            word_onset(sentence, pos), WORD_ON,
            role=name, sentence=sentence, position=pos, cell=cell,
            congruent=congruent, canonical_order=canonical,
            pronoun_gender="f" if pron_f else "m", agent_gender="f" if agent_f else "m")

add(None, "inter_sentence_break", "fixation cross (light grey)", FIX + 6 * WORD_SOA,
    FIX)
add(None, "response_window_opens", "fixation cross (light grey)", RESP_OPEN,
    f"until response, max {RESPONSE_WINDOW}")
# Button presses are recorded by the MEG on their own STI lines; the PC marks
# only the feedback onset (first frame after the press, or the timeout).
add(211, "feedback: correct", "fixation cross turns green", f"{RESP_OPEN} + RT", FEEDBACK)
add(212, "feedback: incorrect", "fixation cross turns red", f"{RESP_OPEN} + RT", FEEDBACK)
add(213, "feedback: timeout (no response)", "fixation cross turns dark grey",
    RESP_OPEN + RESPONSE_WINDOW, FEEDBACK)
for b in range(1, 6):
    add(200 + b, f"pause/instruction screen before block {b}",
        ("instructions" if b == 1 else "pause text") + "; the operator's SPACE starts the block",
        "", "until SPACE")
add(255, "end of experiment", "end screen", "", 5000)

# Localizer: one stimulus every second, times from the stimulus onset.
with open(HERE.parent / "counterbalancing" / "stimuli.csv", newline="", encoding="utf-8") as f:
    stim = list(csv.reader(f))
nouns = [r[stim[0].index(col)] for col in ("people", "places") for r in stim[1:]]
for k, noun in enumerate(nouns, 1):
    for code, modality, on_screen in ((k, "word", f"'{noun}' (no fixation cross; feedback as a dot at its centre)"),
                                      (32 + k, "image", f"picture of '{noun}' with the fixation cross on it")):
        add(code, f"localizer {modality}: {noun}", on_screen, 0,
            f"{LOC_ON} (until the next stimulus)", task="localizer",
            modality=modality, concept=k, item=noun)
for b, what in ((0, "training"), (1, "block 1"), (2, "block 2")):
    add(206 + b, f"localizer: instruction/pause screen before {what}",
        "text; the operator's SPACE starts the block", "", "until SPACE", task="localizer")
add(211, "localizer feedback: hit", "cross on a picture, or dot on a word, turns green (press on a match)", "RT",
    "until the next stimulus", task="localizer")
add(212, "localizer feedback: false alarm", "cross on a picture, or dot on a word, turns red (press on a non-match)", "RT",
    "until the next stimulus", task="localizer")
add(213, "localizer feedback: miss", "cross on a picture, or dot on a word, turns red (no press on a match)", LOC_DEADLINE,
    f"{LOC_SOA - LOC_DEADLINE}", task="localizer")

rows.sort(key=lambda r: (r["task"] != "main", r["code"] is None, r["code"] or 0))
fields = ["task", "code", "event", "on_screen", "onset_ms", "duration_ms", "role", "sentence",
          "position", "cell", "congruent", "canonical_order", "pronoun_gender", "agent_gender",
          "modality", "concept", "item"]
with open(HERE / "triggers.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
codes = [(r["task"], r["code"]) for r in rows if r["code"] is not None]
assert len(codes) == len(set(codes)) and all(1 <= c <= 255 for _, c in codes)
print(f"Wrote {len(codes)} codes to triggers.csv")
