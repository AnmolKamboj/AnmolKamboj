#!/usr/bin/env python3
"""Wide wordmark banner used at the top of the README."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config import FOCUS, FULL_NAME, PALETTE, TITLE

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"

W, H = 1400, 160
SCALE = 2


def build() -> Path:
    img = Image.new("RGBA", (W * SCALE, H * SCALE), (*PALETTE["bg"], 255))
    d = ImageDraw.Draw(img)
    bold = ImageFont.truetype(str(FONTS / "JetBrainsMono-Bold.ttf"), 92)
    regular = ImageFont.truetype(str(FONTS / "JetBrainsMono-Regular.ttf"), 28)

    name = FULL_NAME.upper()
    bbox = d.textbbox((0, 0), name, font=bold)
    tw = bbox[2] - bbox[0]
    d.text(((W * SCALE - tw) / 2, 48), name, font=bold, fill=PALETTE["brass"])

    sub = f"{TITLE}  //  {FOCUS}"
    sb = d.textbbox((0, 0), sub, font=regular)
    d.text(((W * SCALE - (sb[2] - sb[0])) / 2, 168), sub, font=regular, fill=PALETTE["muted"])

    # brass rules
    gap = 36
    y = 210
    left = (W * SCALE - (sb[2] - sb[0])) / 2 - 80
    right = (W * SCALE + (sb[2] - sb[0])) / 2 + 80
    d.line([(left, y), (left + 48, y)], fill=PALETTE["brass"], width=3)
    d.line([(right - 48, y), (right, y)], fill=PALETTE["brass"], width=3)

    out = ASSETS / "wordmark.png"
    img.save(out, "PNG", optimize=True)
    print(f"wrote {out}")
    return out


if __name__ == "__main__":
    build()
