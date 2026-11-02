"""Write triggers.csv: every MEG trigger code, the event it marks, what is on
screen from that moment, and when it happens within a trial.

Word codes are 16 * role + cell, where cell packs the trial's condition:
    bit 0 congruent, bit 1 canonical order, bit 2 pronoun feminine, bit 3 agent feminine.
Times are ms from the trial's fixation onset (code 160 + trial_number).

The localizer (task "localizer", after the main task) reuses codes 1-96 for its
stimuli: word of person/place k = k, its picture = 32 + k, concepts numbered as
in stimuli.csv (people 1-16, places 17-32); word of animal a = 64 + a, its
picture = 80 + a, animals numbered as in localizer/animals.csv (concepts 33-48).
Its blocks open with codes 207-209, so the two tasks are separate segments of
the recording.
"""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent

WORD_ON, WORD_SOA = 300, 300  # each word stays on until the next
FIX = 1000                     # initial fixation and inter-sentence break
RESPONSE_WINDOW = 3000
FEEDBACK = 500
ITI = 2000                     # plain cross after the feedback, no code
LOC_ON, LOC_OFF, LOC_FEEDBACK = 300, 500, 500
LOC_HIT_WINDOW = (200, 1200)  # a press this long after an animal's onset is a hit

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

S2_START = FIX + 6 * WORD_SOA + FIX          # 3800
RESP_OPEN = S2_START + 2 * WORD_SOA  # 4400: the adjective's onset
ADJ_OFF = RESP_OPEN + WORD_ON        # 4700


def word_onset(sentence, position):
    start = FIX if sentence == 1 else S2_START
    return start + (position - 1) * WORD_SOA


rows = []


def add(code, event, on_screen, onset, duration, task="main", **cond):
    rows.append({"task": task, "code": code, "event": event, "on_screen": on_screen,
                 "onset_ms": onset, "duration_ms": duration, **cond})


for t in range(1, 41):  # 32 main trials + 8 fillers per block
    add(160 + t, f"trial_start (trial_number={t})", "fixation cross (light grey)", 0, FIX)

for role, (name, sentence, pos_can, pos_non) in ROLES.items():
    for cell in range(16):
        congruent, canonical = cell & 1, cell >> 1 & 1
        pron_f, agent_f = cell >> 2 & 1, cell >> 3 & 1
        pos = pos_can if canonical else pos_non
        add(16 * role + cell, f"word: {name}",
            f"'{EXAMPLE[name][0 if canonical else 1]}' (on the fixation cross)",
            word_onset(sentence, pos), WORD_ON,
            role=name, sentence=sentence, position=pos, cell=cell,
            congruent=congruent, canonical_order=canonical,
            pronoun_gender="f" if pron_f else "m", agent_gender="f" if agent_f else "m")

# Fillers (trial_type "filler"): the pronoun refers to the person; the
# adjective fits ("natural") or clashes with the verb ("odd").
for role, (name, sentence, pos_can, pos_non) in ROLES.items():
    for canonical in (0, 1):
        for natural in (0, 1):
            pos = pos_can if canonical else pos_non
            add(214 + 4 * (role - 1) + 2 * canonical + natural, f"filler word: {name}",
                f"'{EXAMPLE[name][0 if canonical else 1]}' (on the fixation cross)",
                word_onset(sentence, pos), WORD_ON,
                role=name, sentence=sentence, position=pos, canonical_order=canonical,
                judgment="natural" if natural else "odd")

add(None, "inter_sentence_break", "fixation cross (light grey)", FIX + 6 * WORD_SOA,
    FIX)
add(None, "response_window_opens", "the adjective (presses count from its onset; RT from there)", RESP_OPEN,
    f"until response, at most until {ADJ_OFF + RESPONSE_WINDOW}")
# Button presses are recorded by the MEG on their own STI lines; the PC marks
# only the feedback onset (first frame after the press, or the timeout).
add(211, "feedback: correct", "fixation cross turns green", f"{RESP_OPEN} + RT, at the earliest {ADJ_OFF}", FEEDBACK)
add(212, "feedback: incorrect", "fixation cross turns red", f"{RESP_OPEN} + RT, at the earliest {ADJ_OFF}", FEEDBACK)
add(213, "feedback: timeout (no response)", "fixation cross turns dark grey",
    ADJ_OFF + RESPONSE_WINDOW, FEEDBACK)
add(None, "countdown (no code)", "3, 2, 1, one second each, after the operator's SPACE",
    "before trial 1 of every block (main and localizer)", 3000)
add(None, "inter_trial_interval", "fixation cross (light grey)", f"feedback onset + {FEEDBACK}", ITI)
for b in range(1, 7):
    add(200 + b, f"pause/instruction screen before block {b}",
        ("instructions" if b == 1 else "pause text") + "; the operator's SPACE starts the block",
        "", "until SPACE")
add(210, "instruction screens before the training block (block 0, 20 trials)",
    "instructions; the operator's SPACE starts the block", "", "until SPACE")
add(255, "end of experiment", "end screen", "", 5000)

# Localizer: a stimulus every 800 ms (300 on, 500 of fixation), times from
# the stimulus onset. Word mini-blocks show the main task's small cross, the
# word on top; picture mini-blocks the large grey cross, on top of the picture.
with open(HERE.parent / "counterbalancing" / "stimuli.csv", newline="", encoding="utf-8") as f:
    stim = list(csv.reader(f))
nouns = [r[stim[0].index(col)] for col in ("people", "places") for r in stim[1:]]
with open(HERE.parent / "localizer" / "animals.csv", newline="", encoding="utf-8") as f:
    animals = [r["animals"] for r in csv.DictReader(f)]
for k, noun in enumerate(nouns + animals, 1):
    word, image = (k, 32 + k) if k <= 32 else (32 + k, 48 + k)
    for code, modality, on_screen in ((word, "word", f"'{noun}' on the small fixation cross"),
                                      (image, "image", f"picture of '{noun}', the large fixation cross on top")):
        add(code, f"localizer {modality}: {noun}" + (" (animal: target)" if k > 32 else ""), on_screen, 0,
            f"{LOC_ON}, then {LOC_OFF} of fixation", task="localizer",
            modality=modality, concept=k, item=noun)
for b, what in ((0, "training"), (1, "block 1"), (2, "block 2")):
    add(207 + b, f"localizer: instruction/pause screen before {what}",
        "text; the operator's SPACE starts the block", "", "until SPACE", task="localizer")
add(211, "localizer feedback: hit (training block only)",
    f"the fixation cross turns green (press {LOC_HIT_WINDOW[0]}-{LOC_HIT_WINDOW[1]} ms after an animal's onset)",
    "animal onset + RT", LOC_FEEDBACK, task="localizer")

rows.sort(key=lambda r: (r["task"] != "main", r["code"] is None, r["code"] or 0))
fields = ["task", "code", "event", "on_screen", "onset_ms", "duration_ms", "role", "sentence",
          "position", "cell", "congruent", "judgment", "canonical_order", "pronoun_gender", "agent_gender",
          "modality", "concept", "item"]
with open(HERE / "triggers.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
codes = [(r["task"], r["code"]) for r in rows if r["code"] is not None]
assert len(codes) == len(set(codes)) and all(1 <= c <= 255 for _, c in codes)
print(f"Wrote {len(codes)} codes to triggers.csv")
