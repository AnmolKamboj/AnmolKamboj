#!/usr/bin/env python3
"""A terminal window for the stack. Four panes, one prompt, no badge wall."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONT_R = ASSETS / "fonts" / "JetBrainsMono-Regular.ttf"
FONT_B = ASSETS / "fonts" / "JetBrainsMono-Bold.ttf"

BG = (13, 17, 23)
PANEL = (17, 22, 30)
TITLE = (22, 27, 36)
ORANGE = (255, 166, 87)
BLUE = (165, 214, 255)
GREEN = (63, 185, 80)
GRAY = (110, 118, 129)
WHITE = (230, 237, 243)
RULE = (48, 54, 61)
RED = (248, 81, 73)
YELLOW = (227, 179, 65)

PANES = [
    {
        "path": "~/stack/interface",
        "why": "the part people touch",
        "files": [
            ("react", "the view"),
            ("next.js", "app router"),
            ("typescript", "catches it here"),
            ("tailwind", "fewer CSS regrets"),
            ("html + css", "still the substrate"),
        ],
    },
    {
        "path": "~/stack/systems",
        "why": "what happens after the click",
        "files": [
            ("python", "agents, APIs, glue"),
            ("go", "when the path has to stay thin"),
            ("sql", "the data has to live somewhere"),
            ("flask", "boring on purpose"),
            ("rest", "the contract"),
        ],
    },
    {
        "path": "~/stack/cloud",
        "why": "how it leaves the laptop",
        "files": [
            ("aws", "ec2, s3, iam, dynamodb"),
            ("docker", "same image every time"),
            ("ci/cd", "no more 'works on mine'"),
            ("gcp", "when the job is already there"),
        ],
    },
    {
        "path": "~/stack/agents",
        "why": "when a dashboard is not the product",
        "files": [
            ("tool calling", "the model moves if I let it"),
            ("orchestration", "multi-step, still inspectable"),
            ("llm glue", "context in, a trail out"),
        ],
    },
]


def rounded(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def build() -> Path:
    W, H = 1000, 620
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    regular = ImageFont.truetype(str(FONT_R), 14)
    bold = ImageFont.truetype(str(FONT_B), 14)
    small = ImageFont.truetype(str(FONT_R), 12)
    tiny = ImageFont.truetype(str(FONT_R), 11)

    # Window chrome
    rounded(d, (16, 16, W - 16, H - 16), 12, PANEL)
    d.rectangle((16, 16, W - 16, 52), fill=TITLE)
    d.ellipse((32, 28, 44, 40), fill=RED)
    d.ellipse((52, 28, 64, 40), fill=YELLOW)
    d.ellipse((72, 28, 84, 40), fill=GREEN)
    d.text((104, 26), "anmol@ops  —  ~/stack  —  zsh", font=bold, fill=WHITE)
    d.line([(16, 52), (W - 16, 52)], fill=RULE, width=1)

    d.text((36, 66), "last login: from Boca Raton", font=tiny, fill=GRAY)
    d.text((36, 86), "$", font=bold, fill=ORANGE)
    d.text((54, 86), "ls --classify ~/stack && cat why.md", font=regular, fill=WHITE)

    # Four panes
    inset = 36
    gap = 16
    top = 118
    pane_w = (W - inset * 2 - gap) // 2
    pane_h = 200
    positions = [
        (inset, top),
        (inset + pane_w + gap, top),
        (inset, top + pane_h + gap),
        (inset + pane_w + gap, top + pane_h + gap),
    ]

    for pane, (px, py) in zip(PANES, positions):
        d.rounded_rectangle((px, py, px + pane_w, py + pane_h), radius=8, fill=BG)
        d.rectangle((px, py, px + pane_w, py + 28), fill=TITLE)
        d.text((px + 12, py + 7), pane["path"], font=bold, fill=GREEN)
        d.text((px + 12, py + 36), "# " + pane["why"], font=tiny, fill=GRAY)

        y = py + 56
        for name, note in pane["files"]:
            d.text((px + 16, y), name, font=regular, fill=BLUE)
            nx = d.textbbox((0, 0), name, font=regular)
            d.text((px + 16 + (nx[2] - nx[0]) + 14, y + 1), note, font=small, fill=GRAY)
            y += 22

    # Footer prompt
    fy = H - 58
    d.line([(36, fy - 10), (W - 36, fy - 10)], fill=RULE, width=1)
    d.text((36, fy), "anmol@ops", font=bold, fill=GREEN)
    d.text((128, fy), ":~/stack", font=regular, fill=BLUE)
    d.text((216, fy), "$", font=bold, fill=ORANGE)
    d.rectangle((234, fy + 2, 244, fy + 16), fill=ORANGE)

    out = ASSETS / "stack.png"
    img.save(out, "PNG", optimize=True)
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    build()
