"""Write triggers.csv: every MEG trigger code, the event it marks, what is on
screen from that moment, and when it happens within a trial.

Word codes are 16 * role + cell, where cell packs the trial's condition:
    bit 0 congruent, bit 1 canonical order, bit 2 pronoun feminine, bit 3 agent feminine.
Times are ms from the trial's fixation onset (code 160 + trial_number).
"""
import csv
from pathlib import Path

WORD_ON, WORD_SOA = 200, 500
FIX = 1000                     # initial fixation and inter-sentence break
RESPONSE_WINDOW = 3000
FEEDBACK = 500

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
RESP_OPEN = S2_START + 2 * WORD_SOA + WORD_ON  # 6200


def word_onset(sentence, position):
    start = FIX if sentence == 1 else S2_START
    return start + (position - 1) * WORD_SOA


rows = []


def add(code, event, on_screen, onset, duration, **cond):
    rows.append({"code": code, "event": event, "on_screen": on_screen,
                 "onset_ms": onset, "duration_ms": duration, **cond})


for t in range(1, 33):
    add(160 + t, f"trial_start (trial_number={t})", "fixation dot (light grey)", 0, FIX)

for role, (name, sentence, pos_can, pos_non) in ROLES.items():
    for cell in range(16):
        congruent, canonical = cell & 1, cell >> 1 & 1
        pron_f, agent_f = cell >> 2 & 1, cell >> 3 & 1
        pos = pos_can if canonical else pos_non
        add(16 * role + cell, f"word: {name}",
            f"'{EXAMPLE[name][0 if canonical else 1]}' then fixation at +{WORD_ON} ms",
            word_onset(sentence, pos), f"{WORD_ON} + {WORD_SOA - WORD_ON} fixation",
            role=name, sentence=sentence, position=pos, cell=cell,
            congruent=congruent, canonical_order=canonical,
            pronoun_gender="f" if pron_f else "m", agent_gender="f" if agent_f else "m")

add(None, "inter_sentence_break", "fixation dot (light grey)", FIX + 6 * WORD_SOA,
    f"{FIX} (after the last word's {WORD_SOA - WORD_ON} ms fixation)")
add(None, "response_window_opens", "fixation dot (light grey)", RESP_OPEN,
    f"until response, max {RESPONSE_WINDOW}")
# Button presses are recorded by the MEG on their own STI lines; the PC marks
# only the feedback onset (first frame after the press, or the timeout).
add(211, "feedback: correct", "fixation dot turns green", f"{RESP_OPEN} + RT", FEEDBACK)
add(212, "feedback: incorrect", "fixation dot turns red", f"{RESP_OPEN} + RT", FEEDBACK)
add(213, "feedback: timeout (no response)", "fixation dot turns dark grey",
    RESP_OPEN + RESPONSE_WINDOW, FEEDBACK)
for b in range(1, 6):
    add(200 + b, f"pause/instruction screen before block {b}",
        ("instructions" if b == 1 else "pause text") + "; the operator's SPACE starts the block",
        "", "until SPACE")
add(255, "end of experiment", "end screen", "", 5000)

rows.sort(key=lambda r: (r["code"] is None, r["code"] or 0))
fields = ["code", "event", "on_screen", "onset_ms", "duration_ms", "role", "sentence",
          "position", "cell", "congruent", "canonical_order", "pronoun_gender", "agent_gender"]
with open(Path(__file__).resolve().parent / "triggers.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
codes = [r["code"] for r in rows if r["code"] is not None]
assert len(codes) == len(set(codes)) and all(1 <= c <= 255 for c in codes)
print(f"Wrote {len(codes)} codes to triggers.csv")
