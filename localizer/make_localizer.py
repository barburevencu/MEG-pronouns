"""Generate the localizer sequences for all subjects, and the pictures it shows.

The localizer is an animal-detection task: words and pictures of the 32 nouns
of stimuli.csv (16 people, 16 places) and of 16 animals (animals.csv), each
on for 300 ms with 500 ms of fixation after it; the participant presses when
they see an animal, word or picture (about 11% of the trials).

The stimuli come in mini-blocks of one modality, words and pictures
alternating. A mini-block holds every person and place of its modality the
same number of times (in random order, each one once in each half of the
mini-block) plus a few animals. The same concept never comes twice in a row,
not even across mini-blocks (a word, then its picture).

Per subject:
    block 0 (training): 2 mini-blocks of 36 trials: 32 + 4 animals. 8 animals
        appear, 4 as words and 4 others as pictures.
    blocks 1 and 2: 8 mini-blocks of 72 trials: 64 (each person/place twice)
        + 8 animals; 576 trials. Each animal word and each animal picture
        appears twice per block, once in the modality's first two
        mini-blocks and once in its last two.
The first mini-block of training and block 1 is words for odd subjects,
pictures for even subjects; block 2 starts with the other modality.

Animals: never in the first 5 trials of a block nor in its last trial, and at
least 6 other trials between two animals of a block (also across mini-blocks).

Also writes images/<noun>.png: the pictures of ../pictures, shrunk to 512 px.
An animal without a picture in ../pictures gets a placeholder: its name on a
grey square.

Trigger codes: word of person/place k = k (1-32), its picture = 32 + k;
word of animal a = 64 + a (65-80), its picture = 80 + a (81-96). Concepts:
people 1-16, places 17-32, animals 33-48.

Usage: python3 make_localizer.py [N_SUBJECTS]
"""
import csv
import random
import sys
import unicodedata
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SEED = 2026
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
N_SUBJECTS = int(sys.argv[1]) if len(sys.argv) > 1 else 30
IMAGE_SIZE = 512
# block: (mini-blocks, repetitions of each person/place per mini-block, animals per mini-block)
BLOCKS = {0: (2, 1, 4), 1: (8, 2, 8), 2: (8, 2, 8)}
FIRST_ANIMAL = 6  # earliest trial of a block that can be an animal
ANIMAL_GAP = 7    # minimum distance between two animals' trial numbers


def ascii_name(noun):
    return "".join(c for c in unicodedata.normalize("NFD", noun) if unicodedata.category(c) != "Mn")


def read_concepts():
    """The 32 nouns, people then places, in stimuli.csv order, then the 16
    animals of animals.csv."""
    with open(ROOT / "counterbalancing" / "stimuli.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header = rows[0]
    people, places = header.index("people"), header.index("places")
    concepts = []
    for category, col in (("person", people), ("place", places)):
        for r in rows[1:]:
            # The gender column follows each noun column.
            concepts.append({"item": r[col], "category": category, "gender": r[col + 1]})
    with open(HERE / "animals.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            concepts.append({"item": r["animals"], "category": "animal", "gender": r["gender"]})
    assert len(concepts) == 48
    for k, c in enumerate(concepts, 1):
        c["concept"] = k
        c["image"] = ascii_name(c["item"]) + ".png"
    return concepts


def code(concept, modality):
    if concept <= 32:
        return concept if modality == "word" else 32 + concept
    return 32 + concept if modality == "word" else 48 + concept


def fillers(reps, prev, rng):
    """The people and places of one mini-block: reps random orders of the 32,
    one after the other, with no concept twice in a row (prev: the concept
    just before the mini-block, or None)."""
    seq = []
    for _ in range(reps):
        while True:
            order = rng.sample(range(1, 33), 32)
            if order[0] != (seq[-1] if seq else prev):
                break
        seq += order
    return seq


def animal_positions(n, k, lo, rng):
    """k sorted 0-based positions in a mini-block of n trials, the first at lo
    or later, ANIMAL_GAP or more apart. Uniform over such sets: q_i = p_i -
    (ANIMAL_GAP - 1) * i are k distinct values in [lo, n - (ANIMAL_GAP - 1) * (k - 1))."""
    q = sorted(rng.sample(range(lo, n - (ANIMAL_GAP - 1) * (k - 1)), k))
    return [x + (ANIMAL_GAP - 1) * i for i, x in enumerate(q)]


def block_sequence(block, first_modality, rng):
    """One block: a list of (mini-block, modality, concept)."""
    n_mini, reps, n_animals = BLOCKS[block]
    modalities = [first_modality, {"word": "image", "image": "word"}[first_modality]]
    # Animals of each modality's mini-blocks, in order.
    animals = {}
    if block == 0:
        drawn = rng.sample(range(33, 49), 8)
        animals = {modalities[0]: drawn[:4], modalities[1]: drawn[4:]}
    else:
        for m in modalities:
            animals[m] = rng.sample(range(33, 49), 16) + rng.sample(range(33, 49), 16)

    seq = []
    last = None  # trial index (0-based, in the block) of the latest animal
    for mini in range(n_mini):
        modality = modalities[mini % 2]
        n = 32 * reps + n_animals
        start = len(seq)
        lo = FIRST_ANIMAL - 1 if last is None else max(0, last + ANIMAL_GAP - start)
        # Not the block's last trial: its response window would outlast the block.
        pos = set(animal_positions(n - (mini == n_mini - 1), n_animals, lo, rng))
        mine = iter(animals[modality][(mini // 2) * n_animals:(mini // 2 + 1) * n_animals])
        rest = iter(fillers(reps, seq[-1][2] if seq and 0 not in pos else None, rng))
        for i in range(n):
            seq.append((mini + 1, modality, next(mine) if i in pos else next(rest)))
        last = start + max(pos)
    return seq


def check(seq, block, first_modality):
    n_mini, reps, n_animals = BLOCKS[block]
    n = 32 * reps + n_animals
    assert len(seq) == n_mini * n
    animal_trials = [t for t, (_, _, k) in enumerate(seq, 1) if k > 32]
    assert animal_trials[0] >= FIRST_ANIMAL and animal_trials[-1] < len(seq)
    assert all(b - a >= ANIMAL_GAP for a, b in zip(animal_trials, animal_trials[1:]))
    animal_counts = {}
    for mini in range(n_mini):
        part = seq[mini * n:(mini + 1) * n]
        modality = part[0][1]
        assert modality == (first_modality if mini % 2 == 0 else {"word": "image", "image": "word"}[first_modality])
        assert all(m == mini + 1 and mod == modality for m, mod, _ in part)
        counts = {}
        for _, _, k in part:
            counts[k] = counts.get(k, 0) + 1
        assert all(counts[k] == reps for k in range(1, 33))
        assert sum(n for k, n in counts.items() if k > 32) == n_animals
        for k, c in counts.items():
            if k > 32:
                animal_counts[modality, k] = animal_counts.get((modality, k), 0) + c
    assert all(a[2] != b[2] for a, b in zip(seq, seq[1:]))
    if block == 0:
        assert set(animal_counts.values()) == {1} and len({k for _, k in animal_counts}) == 8
    else:
        assert set(animal_counts.values()) == {2} and len(animal_counts) == 32


def placeholder(name, path):
    """A grey square with the animal's name, until its picture exists."""
    img = Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE), (90, 90, 90))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Arial.ttf", 56)
    except OSError:
        font = ImageFont.load_default()
    d.text((IMAGE_SIZE / 2, IMAGE_SIZE / 2), f"[{name}]", font=font, fill="white", anchor="mm")
    img.save(path, optimize=True)


def main():
    concepts = read_concepts()

    (HERE / "images").mkdir(exist_ok=True)
    placeholders = []
    for c in concepts:
        src, dst = ROOT / "pictures" / c["image"], HERE / "images" / c["image"]
        if src.exists():
            img = Image.open(src).convert("RGB")
            img.resize((IMAGE_SIZE, IMAGE_SIZE), Image.LANCZOS).save(dst, optimize=True)
        else:
            assert c["category"] == "animal", f"no picture {src}"
            placeholder(c["item"], dst)
            placeholders.append(c["item"])

    rows = []
    for subject in range(1, N_SUBJECTS + 1):
        rng = random.Random(SEED * 1000 + subject)
        first = "word" if subject % 2 else "image"
        other = {"word": "image", "image": "word"}[first]
        for block, first_modality in ((0, first), (1, first), (2, other)):
            seq = block_sequence(block, first_modality, rng)
            check(seq, block, first_modality)
            for t, (mini, mod, k) in enumerate(seq, 1):
                c = concepts[k - 1]
                rows.append({
                    "subject_id": subject, "block": block, "trial_number": t, "miniblock": mini,
                    "modality": mod, "item": c["item"], "image": c["image"],
                    "concept": k, "category": c["category"], "gender": c["gender"],
                    "target": int(k > 32), "code": code(k, mod),
                })

    out = HERE / "localizer.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out} ({len(rows)} rows, {N_SUBJECTS} subjects) and {len(concepts)} images"
          + (f", {len(placeholders)} of them placeholders" if placeholders else ""))


if __name__ == "__main__":
    main()
