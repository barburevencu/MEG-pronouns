"""Generate the localizer sequences for all subjects, and the pictures it shows.

The localizer is a one-back task on the 32 nouns of stimuli.csv: words and
pictures alternate (word, picture, word, ...), and the participant presses when
the current stimulus is the same concept as the previous one (a match).

Per subject:
    block 0 (training): 64 trials, every word and every picture once, 4 matches.
    blocks 1 and 2: 512 trials, every word and every picture 8 times, 32
        matches. Every concept is matched once per block: half of the concepts
        word -> picture in block 1 and picture -> word in block 2, the other
        half the other way round.

Match positions are random, never two in a row. Non-match trials take their
item at random among those left, with only the task's own restriction: a
non-match is never the previous stimulus's concept.

Also writes images/<noun>.png: the pictures of ../pictures, shrunk to 512 px.

Trigger codes: word of concept k = k (1-32), picture of concept k = 32 + k.

Usage: python3 make_localizer.py [N_SUBJECTS]
"""
import csv
import random
import sys
import unicodedata
from pathlib import Path

from PIL import Image

SEED = 2026
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
N_SUBJECTS = int(sys.argv[1]) if len(sys.argv) > 1 else 30
IMAGE_SIZE = 512
BLOCKS = {0: (1, 4), 1: (8, 32), 2: (8, 32)}  # block: (repetitions of each stimulus, matches)


def ascii_name(noun):
    return "".join(c for c in unicodedata.normalize("NFD", noun) if unicodedata.category(c) != "Mn")


def read_concepts():
    """The 32 concepts, people then places, in stimuli.csv order."""
    with open(ROOT / "counterbalancing" / "stimuli.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header = rows[0]
    people, places = header.index("people"), header.index("places")
    concepts = []
    for category, col in (("person", people), ("place", places)):
        for r in rows[1:]:
            # The gender column follows each noun column.
            concepts.append({"item": r[col], "category": category, "gender": r[col + 1]})
    for k, c in enumerate(concepts, 1):
        c["concept"] = k
        c["image"] = ascii_name(c["item"]) + ".png"
    return concepts


def match_positions(n_trials, n_matches, rng, parities=None):
    """Random 1-based positions of the matches, never adjacent and never trial 1.
    parities: optional (n_even, n_odd); an even position is a picture."""
    while True:
        if parities:
            evens = rng.sample(range(2, n_trials + 1, 2), parities[0])
            odds = rng.sample(range(3, n_trials + 1, 2), parities[1])
            pos = sorted(evens + odds)
        else:
            pos = sorted(rng.sample(range(2, n_trials + 1), n_matches))
        if all(b - a > 1 for a, b in zip(pos, pos[1:])):
            return pos


def block_sequence(reps, n_matches, rng, word_to_picture=None):
    """One block: a list of (modality, concept, match). word_to_picture is the
    set of concepts matched word -> picture (the rest picture -> word); without
    it (training), the matched concepts and directions are random."""
    n_trials = 64 * reps
    while True:
        if word_to_picture is None:
            pos = match_positions(n_trials, n_matches, rng)
            targets = rng.sample(range(1, 33), n_matches)
        else:
            w2p = sorted(word_to_picture)
            p2w = sorted(set(range(1, 33)) - word_to_picture)
            pos = match_positions(n_trials, n_matches, rng, (len(w2p), len(p2w)))
            rng.shuffle(w2p)
            rng.shuffle(p2w)
            targets = [w2p.pop() if p % 2 == 0 else p2w.pop() for p in pos]

        seq = [None] * (n_trials + 1)  # 1-based concepts
        left = {"word": [], "image": []}
        for k in range(1, 33):
            left["word"] += [k] * reps
            left["image"] += [k] * reps
        modality = lambda t: "word" if t % 2 == 1 else "image"
        for p, k in zip(pos, targets):
            seq[p - 1] = seq[p] = k
            left[modality(p - 1)].remove(k)
            left[modality(p)].remove(k)

        ok = True
        for t in range(1, n_trials + 1):
            if seq[t] is not None:
                continue
            pool = left[modality(t)]
            # Not the previous concept (it would be a match), and not the
            # concept of a match pair starting right after.
            banned = {seq[t - 1]} if t > 1 else set()
            if t < n_trials and seq[t + 1] is not None:
                banned.add(seq[t + 1])
            choices = [i for i, k in enumerate(pool) if k not in banned]
            if not choices:
                ok = False
                break
            seq[t] = pool.pop(rng.choice(choices))
        if ok:
            matched = set(pos)
            return [(modality(t), seq[t], int(t in matched)) for t in range(1, n_trials + 1)]


def check(seq, reps, n_matches):
    counts = {}
    for t, (mod, k, match) in enumerate(seq, 1):
        assert mod == ("word" if t % 2 == 1 else "image")
        counts[mod, k] = counts.get((mod, k), 0) + 1
        assert match == int(t > 1 and seq[t - 2][1] == k)
        if match:
            assert not seq[t - 2][2], "two matches in a row"
    assert set(counts.values()) == {reps} and len(counts) == 64
    assert sum(m for _, _, m in seq) == n_matches


def main():
    concepts = read_concepts()

    (HERE / "images").mkdir(exist_ok=True)
    for c in concepts:
        img = Image.open(ROOT / "pictures" / c["image"]).convert("RGB")
        img.resize((IMAGE_SIZE, IMAGE_SIZE), Image.LANCZOS).save(HERE / "images" / c["image"], optimize=True)

    rows = []
    for subject in range(1, N_SUBJECTS + 1):
        rng = random.Random(SEED * 1000 + subject)
        half = set(rng.sample(range(1, 33), 16))
        directions = {0: None, 1: half, 2: set(range(1, 33)) - half}
        for block, (reps, n_matches) in BLOCKS.items():
            seq = block_sequence(reps, n_matches, rng, directions[block])
            check(seq, reps, n_matches)
            for t, (mod, k, match) in enumerate(seq, 1):
                c = concepts[k - 1]
                rows.append({
                    "subject_id": subject, "block": block, "trial_number": t,
                    "modality": mod, "item": c["item"], "image": c["image"],
                    "concept": k, "category": c["category"], "gender": c["gender"],
                    "match": match, "code": k if mod == "word" else 32 + k,
                })

    out = HERE / "localizer.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out} ({len(rows)} rows, {N_SUBJECTS} subjects) and {len(concepts)} images")


if __name__ == "__main__":
    main()
