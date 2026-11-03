"""Draw the response-pad pictures used in the instructions, from
response_pad_reference.png (two pads, buttons blue / yellow / green / red from
the top): every button is faded except the green ones the task uses, which
are highlighted and labelled.

    pad_localizer.png         right green: "Animal"
    pad_congruent_left.png    left green "Plausible", right green "Absurde"
    pad_congruent_right.png   left green "Absurde", right green "Plausible"

The canvas is widened by MARGIN on each side, so that long labels fit.

Usage: python3 make_button_images.py [LABEL_FONT.ttf]   (default: Lato Bold)
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONT = sys.argv[1] if len(sys.argv) > 1 else \
    "/Library/Frameworks/R.framework/Versions/4.6/Resources/library/rmarkdown/rmd/h/bootstrap/css/fonts/LatoBold.ttf"

BG = (247, 247, 247)
PAD_WHITE = (255, 255, 255)
FADED = {"blue": (226, 234, 247), "yellow": (252, 247, 208), "green": (231, 246, 243), "red": (251, 230, 229)}
GREEN = (88, 190, 110)
INK = (17, 17, 17)
LINE = (51, 51, 51)
PAD_X = {"left": 547, "right": 1053}
BUTTON_Y = {"blue": 363, "yellow": 520, "green": 677, "red": 833}
R = 54
MARGIN = 150  # added on each side of the reference


def circle(d, x, y, r, **kw):
    d.ellipse((x - r, y - r, x + r, y + r), **kw)


def draw(labels):
    """labels: {"left"/"right": text or None}; text may contain a newline."""
    ref = Image.open(HERE / "response_pad_reference.png").convert("RGB")
    # Erase the reference's label and the line to its red button.
    d = ImageDraw.Draw(ref)
    d.rectangle((1100, 834, 1195, 846), fill=PAD_WHITE)
    d.rectangle((1196, 834, 1229, 846), fill=(230, 230, 230))
    d.rectangle((1230, 700, 1600, 960), fill=BG)
    im = Image.new("RGB", (ref.width + 2 * MARGIN, ref.height), BG)
    im.paste(ref, (MARGIN, 0))
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT, 72)
    for side, x in PAD_X.items():
        x += MARGIN
        for name, y in BUTTON_Y.items():
            circle(d, x, y, R + 4, fill=PAD_WHITE)
            if name == "green" and labels.get(side):
                circle(d, x, y, R, fill=GREEN, outline=(0, 0, 0), width=4)
            else:
                circle(d, x, y, R, fill=FADED[name])
    y = BUTTON_Y["green"]
    for side, text in labels.items():
        if not text:
            continue
        lines = text.split("\n")
        height = 105 * len(lines)
        if side == "right":
            bar, x_text, anchor = MARGIN + 1247, MARGIN + 1288, "la"
            d.line((MARGIN + PAD_X[side] + 17, y, bar, y), fill=LINE, width=4)
        else:
            bar, x_text, anchor = MARGIN + 353, MARGIN + 312, "ra"
            d.line((bar, y, MARGIN + PAD_X[side] - 17, y), fill=LINE, width=4)
        d.line((bar, y - height / 2 - 4, bar, y + height / 2 + 4), fill=LINE, width=4)
        for i, line in enumerate(lines):
            d.text((x_text, y - height / 2 + 105 * i + 8), line, font=font, fill=INK, anchor=anchor)
    return im


def main():
    out = {
        "pad_localizer.png": {"right": "Animal"},
        "pad_congruent_left.png": {"left": "Plausible", "right": "Absurde"},
        "pad_congruent_right.png": {"left": "Absurde", "right": "Plausible"},
    }
    for name, labels in out.items():
        draw(labels).save(HERE / name, optimize=True)
        print("wrote", name)


if __name__ == "__main__":
    main()
