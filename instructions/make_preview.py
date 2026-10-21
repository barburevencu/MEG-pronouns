"""Render the example pictures of the instructions and preview.html, which
shows every instruction screen of screens.json as the MEG program will (black
screen, Inconsolata text, picture under the text), for both response mappings.

Usage: python3 make_preview.py
"""
import base64
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FONT = Path(subprocess.run(["go", "list", "-m", "-f", "{{.Dir}}", "github.com/chrplr/goxpyriment"],
                           cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()) \
    / "assets_embed" / "Inconsolata.ttf"


def example(first, second, name):
    """word -> picture or picture -> word, on black, as one image."""
    font = ImageFont.truetype(str(FONT), 110)
    pic = 380
    im = Image.new("RGB", (1300, pic), "black")
    d = ImageDraw.Draw(im)
    x = 0
    for part in (first, "→", second):
        if part.startswith("pic:"):
            p = Image.open(ROOT / "localizer" / "images" / (part[4:] + ".png")).convert("RGB").resize((pic, pic))
            im.paste(p, (x, 0))
            x += pic
        elif part == "→":  # drawn: Inconsolata has no arrow glyph
            y, grey = pic / 2, (138, 138, 138)
            d.line((x, y, x + 100, y), fill=grey, width=8)
            d.polygon([(x + 112, y), (x + 80, y - 22), (x + 80, y + 22)], fill=grey)
            x += 112
        else:
            w = d.textlength(part, font=font)
            d.text((x, pic / 2), part, font=font, fill="white" if part != "→" else (138, 138, 138), anchor="lm")
            x += int(w)
        x += 70
    im.crop((0, 0, x - 70, pic)).save(HERE / f"{name}.png", optimize=True)


def data_url(path):
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def main():
    example("marin", "pic:marin", "example_word_picture")
    example("pic:nonne", "nonne", "example_picture_word")
    screens = json.loads((HERE / "screens.json").read_text(encoding="utf-8"))

    def screen(s, mapping):
        text = s["text"]
        natural = {"left": "gauche", "right": "droite"}[mapping]
        odd = {"left": "droite", "right": "gauche"}[mapping]
        text = text.format(done=1, total=5, natural=natural, odd=odd)
        body = "".join(f"<p>{p}</p>" for p in text.split("\n\n"))
        img = s.get("image")
        if img:
            if img == "pad_congruent":
                img = f"pad_congruent_{mapping}"
            cls = "pad" if img.startswith("pad") else "ex"
            body += f'<img class="{cls}" src="{data_url(HERE / (img + ".png"))}">'
        return f'<div class="screen">{body}</div>'

    sections = [
        ("localizer_intro", "Localizer: before the first localizer block", None),
        ("localizer_before_training", "Then, before the training block", None),
        ("localizer_after_training", "Before localizer block 1 (after training)", None),
        ("localizer_pause", "Before localizer block 2", None),
        ("main_intro_after_localizer", "Main task, first screen (after the localizer)", None),
        ("main_intro_alone", "… or, when the localizer was skipped", None),
        ("main_intro", "Main task instructions: odd subjects (natural = left)", "left"),
        ("main_intro", "Main task instructions: even subjects (natural = right)", "right"),
        ("main_pause", "Pause before main blocks 2-5 (odd subjects; even ones get the mirrored pad)", "left"),
        ("end", "End", None),
    ]
    font = data_url(FONT).replace("image/png", "font/ttf")
    parts = []
    n = 0
    for key, title, mapping in sections:
        cards = []
        for s in screens[key]:
            n += 1
            cards.append(f'<figure><figcaption>{n}</figcaption>{screen(s, mapping or "left")}</figure>')
        parts.append(f"<h2>{title}</h2><div class='row'>{''.join(cards)}</div>")

    html = f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><title>Instruction screens</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
@font-face {{ font-family: Inconsolata; src: url({font}); }}
body {{ background: #f4f4f4; color: #222; font: 15px/1.4 -apple-system, Helvetica, Arial, sans-serif; margin: 24px; }}
h1 {{ font-size: 20px; margin: 0 0 4px; }} h2 {{ font-size: 15px; margin: 28px 0 8px; color: #555; }}
.note {{ color: #666; max-width: 900px; }}
.row {{ display: flex; flex-wrap: wrap; gap: 14px; }}
figure {{ margin: 0; }} figcaption {{ font-size: 12px; color: #888; }}
.screen {{ width: 480px; height: 270px; background: #000; color: #fff; display: flex; flex-direction: column;
          align-items: center; justify-content: center; text-align: center; padding: 0 28px; box-sizing: border-box;
          font: 13px/1.35 Inconsolata, monospace; }}
.screen p {{ margin: 0 0 8px; max-width: 55%; }}
.screen img.pad {{ height: 140px; margin-top: 6px; }}
.screen img.ex {{ height: 95px; margin-top: 8px; }}
</style></head><body>
<h1>Instruction screens of the MEG session</h1>
<p class="note">Each black box is one full screen, scaled down (text in the program's font, Inconsolata;
lines at most 55% of the screen width).
The operator advances every screen with SPACE, as now; the last screen before each block starts it.</p>
{''.join(parts)}
</body></html>"""
    (HERE / "preview.html").write_text(html, encoding="utf-8")
    print(f"preview.html: {n} screens")


if __name__ == "__main__":
    main()
