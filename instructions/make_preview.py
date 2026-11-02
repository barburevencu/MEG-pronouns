"""Render preview.html, which shows every instruction screen of screens.json
as the MEG program will (black screen, Inconsolata text, picture under the
text), in the order of the session.

Usage: python3 make_preview.py
"""
import base64
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FONT = Path(subprocess.run(["go", "list", "-m", "-f", "{{.Dir}}", "github.com/chrplr/goxpyriment"],
                           cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()) \
    / "assets_embed" / "Inconsolata.ttf"


def data_url(path):
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


# The screen lists in session order: (name in screens.json, title, response
# mapping filled in, or None). Also used by demo/make_demo.py.
SECTIONS = [
    ("main_intro_two_parts", "Main task (first part): opening screens", None),
    ("main_intro_alone", "… or, when no localizer follows", None),
    ("main_intro", "Main task instructions (natural = right for every subject)", "right"),
    ("main_before_training", "Then, before the training block", "right"),
    ("main_after_training", "Before main block 1 (after training)", "right"),
    ("main_ready", "… or, without training (-block 1), right after the instructions", "right"),
    ("main_pause", "Pause before main blocks 2-6", "right"),
    ("localizer_intro_after_main", "Localizer (second part): first screen, after the main task", None),
    ("localizer_intro_alone", "… or, when the main task was skipped", None),
    ("localizer_intro", "Localizer instructions, before the first localizer block", None),
    ("localizer_before_training", "Then, before the training block", None),
    ("localizer_after_training", "Before localizer block 1 (after training)", None),
    ("localizer_pause", "Before localizer block 2", None),
    ("localizer_next_words", "Between localizer mini-blocks, 10 s, the counter going 10 to 1: before words", None),
    ("localizer_next_images", "… or before pictures", None),
    ("localizer_end", "End, after a localizer block", None),
    ("end", "… or, when no localizer ran", None),
]

TOTAL_BLOCKS = 6  # as main.go's nBlocks, for {total} in the pause screens


def fill(text, mapping):
    """The text as the program shows it, for subject mapping "left"/"right"."""
    natural = {"left": "gauche", "right": "droite"}[mapping]
    odd = {"left": "droite", "right": "gauche"}[mapping]
    return text.format(done=1, total=TOTAL_BLOCKS, natural=natural, odd=odd, seconds=10, percent=85)


def main():
    screens = json.loads((HERE / "screens.json").read_text(encoding="utf-8"))

    def screen(s, mapping):
        text = fill(s["text"], mapping)
        body = '<div class="txt">' + "".join(f"<p>{p}</p>" for p in text.split("\n\n")) + "</div>"
        img = s.get("image")
        if img:
            if img == "pad_congruent":
                img = f"pad_congruent_{mapping}"
            body += f'<img class="pad" src="{data_url(HERE / (img + ".png"))}">'
        return f'<div class="screen">{body}</div>'

    font = data_url(FONT).replace("image/png", "font/ttf")
    parts = []
    n = 0
    for key, title, mapping in SECTIONS:
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
.screen {{ position: relative; width: 480px; height: 270px; background: #000; color: #fff; display: flex; flex-direction: column;
          align-items: center; justify-content: center; text-align: center; padding: 0 28px; box-sizing: border-box;
          font: 13px/1.35 Inconsolata, monospace; }}
.screen .txt {{ max-width: 55%; text-align: left; }}  /* lines left-aligned, block centred */
.screen p {{ margin: 0 0 8px; }}
.screen img.pad {{ height: 140px; margin-top: 6px; }}
</style></head><body>
<h1>Instruction screens of the MEG session</h1>
<p class="note">Each black box is one full screen, scaled down (text in the program's font, Inconsolata;
lines at most 55% of the screen width).
The participant advances with the right green button; only the operator's SPACE leaves the last
screen before each block and starts it.</p>
{''.join(parts)}
</body></html>"""
    (HERE / "preview.html").write_text(html, encoding="utf-8")
    print(f"preview.html: {n} screens")


if __name__ == "__main__":
    main()
