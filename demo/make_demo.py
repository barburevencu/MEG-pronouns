"""Fill pronouns_demo.html's localizer part: a 32-trial sequence and the
pictures, embedded as JPEG data URLs so the demo stays a single file.

The sequence follows the localizer's rules (localizer/make_localizer.py): words
and pictures alternate, starting with a word; 4 matches, 2 word -> picture and
2 picture -> word, never two in a row; every word and every picture at most once.

Usage: python3 make_demo.py   (rewrites the block between the GENERATED markers)
"""
import base64
import io
import json
import random
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "localizer"))
from make_localizer import read_concepts  # noqa: E402

SEED = 7
N_TRIALS, N_MATCHES = 32, 4
IMAGE_PX = 360
DEMO = HERE / "pronouns_demo.html"
BEGIN, END = "// BEGIN GENERATED (make_demo.py)", "// END GENERATED"


def sequence(rng):
    """Concept numbers (1-32) of the 32 trials and the match positions (1-based)."""
    while True:
        evens = rng.sample(range(2, N_TRIALS + 1, 2), N_MATCHES // 2)  # word -> picture
        odds = rng.sample(range(3, N_TRIALS + 1, 2), N_MATCHES // 2)   # picture -> word
        pos = sorted(evens + odds)
        if any(b - a < 2 for a, b in zip(pos, pos[1:])):
            continue
        seq = [None] * (N_TRIALS + 1)
        targets = rng.sample(range(1, 33), N_MATCHES)
        for p, k in zip(pos, targets):
            seq[p - 1] = seq[p] = k
        used = {"word": set(), "image": set()}
        for t in range(1, N_TRIALS + 1):
            if seq[t] is not None:
                used["word" if t % 2 else "image"].add(seq[t])
        ok = True
        for t in range(1, N_TRIALS + 1):
            if seq[t] is not None:
                continue
            mod = "word" if t % 2 else "image"
            banned = used[mod] | {seq[t - 1]} | ({seq[t + 1]} if t < N_TRIALS and seq[t + 1] else set())
            choices = [k for k in range(1, 33) if k not in banned]
            if not choices:
                ok = False
                break
            seq[t] = rng.choice(choices)
            used[mod].add(seq[t])
        if ok:
            return seq[1:], set(pos)


def data_url(path):
    img = Image.open(path).convert("RGB").resize((IMAGE_PX, IMAGE_PX), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=82, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def main():
    concepts = read_concepts()
    seq, matches = sequence(random.Random(SEED))
    trials = [{"modality": "word" if t % 2 else "image", "item": concepts[k - 1]["item"],
               "match": t in matches} for t, k in enumerate(seq, 1)]
    shown = {concepts[k - 1]["item"] for t, k in enumerate(seq, 1) if t % 2 == 0}
    examples = ["marin", "nonne"]  # the instruction screens show these two
    images = {c["item"]: data_url(ROOT / "localizer" / "images" / c["image"])
              for c in concepts if c["item"] in shown or c["item"] in examples}
    nouns = [c["item"] for c in concepts]

    block = "\n".join([
        BEGIN,
        "const LOC_TRIALS = " + json.dumps(trials, ensure_ascii=False) + ";",
        "const NOUNS = " + json.dumps(nouns, ensure_ascii=False) + ";",
        "const IMAGES = " + json.dumps(images) + ";",
        END,
    ])
    html = DEMO.read_text(encoding="utf-8")
    a, b = html.index(BEGIN), html.index(END) + len(END)
    DEMO.write_text(html[:a] + block + html[b:], encoding="utf-8")
    print(f"{DEMO.name}: {len(trials)} localizer trials, matches at {sorted(matches)}, "
          f"{len(images)} pictures, {DEMO.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
