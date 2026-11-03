"""Fill pronouns_demo.html's generated part: the localizer's 72-trial sequence
and pictures, and the MEG program's instruction screens (key 0 in the demo's
menu), with their pictures embedded as data URLs so the demo stays a single file.

The sequence is a localizer training block (localizer/make_localizer.py): a
mini-block of 36 words, then one of 36 pictures, each with the 32 people and
places once and 4 animals, with the 5 s screen announcing pictures between them.

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
sys.path.insert(0, str(ROOT / "instructions"))
from make_localizer import block_sequence, check, read_concepts  # noqa: E402
from make_preview import FONT, SECTIONS, fill  # noqa: E402

SEED = 7
IMAGE_PX = 360
DEMO = HERE / "pronouns_demo.html"
BEGIN, END = "// BEGIN GENERATED (make_demo.py)", "// END GENERATED"


def data_url(path):
    img = Image.open(path).convert("RGB").resize((IMAGE_PX, IMAGE_PX), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=82, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def picture_url(path, height):
    """An instruction picture (a drawn response pad), scaled to height px."""
    img = Image.open(path).convert("RGB")
    img = img.resize((round(img.width * height / img.height), height), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def meg_screens():
    """Every instruction screen of the MEG program, in session order, as the
    program shows it (subject mapping: natural = right), and their pictures."""
    specs = json.loads((ROOT / "instructions" / "screens.json").read_text(encoding="utf-8"))
    screens, pictures = [], {}
    for key, title, mapping in SECTIONS:
        for sc in specs[key]:
            img = sc.get("image")
            if img == "pad_congruent":
                img = f"pad_congruent_{mapping or 'right'}"
            if img and img not in pictures:
                pictures[img] = picture_url(ROOT / "instructions" / f"{img}.png", 540)
            screens.append({"title": title, "text": fill(sc["text"], mapping or "right"), "image": img or ""})
    return screens, pictures


def main():
    concepts = read_concepts()
    seq = block_sequence(0, "word", random.Random(SEED))
    check(seq, 0, "word")
    trials = [{"miniblock": mini, "modality": mod, "item": concepts[k - 1]["item"], "target": k > 32}
              for mini, mod, k in seq]
    shown = {concepts[k - 1]["item"] for _, mod, k in seq if mod == "image"}
    images = {c["item"]: data_url(ROOT / "localizer" / "images" / c["image"])
              for c in concepts if c["item"] in shown}
    nouns = [c["item"] for c in concepts]
    screens, pictures = meg_screens()

    block = "\n".join([
        BEGIN,
        "const LOC_TRIALS = " + json.dumps(trials, ensure_ascii=False) + ";",
        "const NOUNS = " + json.dumps(nouns, ensure_ascii=False) + ";",
        "const IMAGES = " + json.dumps(images) + ";",
        "const MEG_SCREENS = " + json.dumps(screens, ensure_ascii=False) + ";",
        "const MEG_PICTURES = " + json.dumps(pictures) + ";",
        # The program's font (goxpyriment's Inconsolata), so text wraps as on the MEG screen.
        'const INCONSOLATA = "data:font/ttf;base64,' + base64.b64encode(FONT.read_bytes()).decode() + '";',
        END,
    ])
    html = DEMO.read_text(encoding="utf-8")
    a, b = html.index(BEGIN), html.index(END) + len(END)
    DEMO.write_text(html[:a] + block + html[b:], encoding="utf-8")
    animals = [t for t, (_, _, k) in enumerate(seq, 1) if k > 32]
    print(f"{DEMO.name}: {len(trials)} localizer trials, animals at {animals}, "
          f"{len(images)} pictures, {len(screens)} instruction screens, {DEMO.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
