#!/usr/bin/env python3
"""Header: 21st.dev Custom ASCII (left) + senamakel neofetch card (right).

The ASCII pipeline follows the exported 21st.dev recipe exactly:
characters / binary / cellSize 3 / bg original+blur 12 / brightness -100 /
contrast -100 on the photo layer only so the 01 glyphs stay visible /
tint #000 overlay 50% / pfx vignette 59, scanLines 28, chromatic 40,
bloom 60, filmGrain 40, glitch 20 / flicker animation.
"""

from __future__ import annotations

import json
import random
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from config import EMAIL, USERNAME, BIRTHDAY

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "source-portrait.png"
FONT_R = ASSETS / "fonts" / "JetBrainsMono-Regular.ttf"
FONT_B = ASSETS / "fonts" / "JetBrainsMono-Bold.ttf"
STATS_PATH = ASSETS / "stats.json"

# --- 21st.dev recipe (do not "improve" these) ---
CELL = 3
CHARSET = "01"
BG_BLUR = 12
BG_OPACITY = 1.0
TINT = (0, 0, 0)
TINT_OPACITY = 0.50
BRIGHTNESS = -100
CONTRAST = -100
SATURATION = 100
GRAYSCALE = 0
PFX = {
    "vignette": 0.59,
    "scanLines": 0.28,
    "chromatic": 0.40,
    "bloom": 0.60,
    "filmGrain": 0.40,
    "glitch": 0.20,
}

# Compact header. Portrait is a side panel, not a full-page cover.
PORTRAIT_W = 268
PORTRAIT_H = 348
CARD_W = 700
CARD_H = 520
PAD = 18
GAP = 22
W = PAD + PORTRAIT_W + GAP + CARD_W + PAD
H = PAD + CARD_H + PAD

ORANGE = (255, 166, 87)
BLUE = (165, 214, 255)
GRAY = (110, 118, 129)
WHITE = (230, 237, 243)
RULE = (48, 54, 61)
BG = (13, 17, 23)


def age_label() -> str:
    today = date.today()
    years = today.year - BIRTHDAY.year
    months = today.month - BIRTHDAY.month
    if today.day < BIRTHDAY.day:
        months -= 1
    if months < 0:
        years -= 1
        months += 12
    return f"{years} years, {months} months"


def load_stats() -> dict[str, str]:
    raw = {"repos": 0, "commits": 0, "stars": 0, "followers": 0, "contributed": 0}
    if STATS_PATH.exists():
        raw.update(json.loads(STATS_PATH.read_text(encoding="utf-8")))
    return {k: f"{int(v):,}" for k, v in raw.items()}


def slider_factor(value: int) -> float:
    """21st.dev sliders are -100..100. 0 = unchanged, -100 = off."""
    return max(0.0, (value + 100) / 100.0)


def overlay_blend(base: Image.Image, color: tuple[int, int, int], opacity: float) -> Image.Image:
    # CSS overlay, then mix with the source at tintOpacity.
    # Recipe tint is #000000, so the per-channel math collapses cleanly.
    channels = []
    for ch, tint in zip(base.convert("RGB").split(), color):
        def mix(p, t=tint, o=opacity):
            over = (2 * p * t) // 255 if p < 128 else 255 - (2 * (255 - p) * (255 - t)) // 255
            return int(p * (1.0 - o) + over * o)

        channels.append(ch.point(mix))
    return Image.merge("RGB", channels)


def offset_channel(channel: Image.Image, x: int, y: int) -> Image.Image:
    return channel.transform(channel.size, Image.Transform.AFFINE, (1, 0, -x, 0, 1, -y))


def apply_color_adjustments(img: Image.Image) -> Image.Image:
    img = ImageEnhance.Brightness(img).enhance(slider_factor(BRIGHTNESS))
    img = ImageEnhance.Contrast(img).enhance(slider_factor(CONTRAST))
    sat = SATURATION / 100.0
    img = ImageEnhance.Color(img).enhance(sat)
    if GRAYSCALE:
        img = ImageEnhance.Color(img).enhance(max(0.0, 1.0 - GRAYSCALE / 100.0))
    return overlay_blend(img, TINT, TINT_OPACITY)


def vignette(img: Image.Image, intensity: float) -> Image.Image:
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    pad = int(min(w, h) * 0.05)
    d.ellipse([pad, pad, w - pad, h - pad], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(int(min(w, h) * 0.18)))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.blend(img, Image.composite(img, dark, mask), intensity)


def scanlines(img: Image.Image, intensity: float) -> Image.Image:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    alpha = int(140 * intensity)
    for y in range(0, img.size[1], 2):
        d.line([(0, y), (img.size[0], y)], fill=(0, 0, 0, alpha))
    out = img.convert("RGBA")
    out.alpha_composite(overlay)
    return out.convert("RGB")


def chromatic(img: Image.Image, intensity: float) -> Image.Image:
    shift = max(1, int(5 * intensity))
    r, g, b = img.split()
    return Image.merge("RGB", (offset_channel(r, shift, 0), g, offset_channel(b, -shift, 0)))


def bloom(img: Image.Image, intensity: float) -> Image.Image:
    bright = img.point(lambda p: 255 if p > 70 else 0)
    glow = bright.filter(ImageFilter.GaussianBlur(4 + int(10 * intensity)))
    return Image.blend(img, glow, intensity * 0.32)


def film_grain(img: Image.Image, intensity: float, rng: random.Random) -> Image.Image:
    noise = Image.effect_noise(img.size, 24 + int(36 * intensity)).convert("RGB")
    return Image.blend(img, noise, intensity * 0.14)


def glitch(img: Image.Image, intensity: float, rng: random.Random) -> Image.Image:
    out = img.copy()
    w, h = img.size
    for _ in range(2 + int(5 * intensity)):
        y = rng.randint(0, max(1, h - 5))
        hh = rng.randint(1, 5)
        dx = rng.randint(-int(16 * intensity) - 1, int(16 * intensity) + 1)
        band = out.crop((0, y, w, min(h, y + hh)))
        out.paste(band, (dx, y))
    return out


def prepare_photo() -> Image.Image:
    photo = Image.open(SOURCE).convert("RGB")
    w, h = photo.size
    side = min(w, int(h * 0.74))
    left = max(0, (w - side) // 2 + int(w * 0.02))
    top = int(h * 0.02)
    photo = photo.crop((left, top, min(w, left + side), min(h, top + int(side * 1.28))))
    return photo.resize((PORTRAIT_W, PORTRAIT_H), Image.Resampling.LANCZOS)


def render_ascii(photo: Image.Image, rng: random.Random) -> Image.Image:
    # 1. Background: original photo, blurred, then recipe color crush.
    #    Brightness/contrast -100 would wipe glyphs if applied after draw,
    #    so they hit the photo layer only. That is how the 21st.dev look
    #    keeps a black field with colored 01 on top.
    bg = photo.filter(ImageFilter.GaussianBlur(BG_BLUR))
    if BG_OPACITY < 1:
        empty = Image.new("RGB", photo.size, (0, 0, 0))
        bg = Image.blend(empty, bg, BG_OPACITY)
    bg = apply_color_adjustments(bg)

    canvas = bg.copy()
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(str(FONT_R), CELL + 2)
    w, h = photo.size

    # coverage 0 = do not thin the grid (0% skip). density/edgeEmphasis are 0.
    for y in range(0, h, CELL):
        for x in range(0, w, CELL):
            tile = photo.crop((x, y, min(w, x + CELL), min(h, y + CELL)))
            color = tile.resize((1, 1), Image.Resampling.BOX).getpixel((0, 0))
            lum = (0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]) / 255.0
            ch = CHARSET[0] if lum < 0.5 else CHARSET[1]
            # animStyle flicker, animIntensity 0: almost still, a few cells flip
            if rng.random() < 0.012:
                ch = "1" if ch == "0" else "0"
            draw.text((x, y - 1), ch, font=font, fill=color)

    img = chromatic(canvas, PFX["chromatic"])
    img = bloom(img, PFX["bloom"])
    img = scanlines(img, PFX["scanLines"])
    img = vignette(img, PFX["vignette"])
    img = film_grain(img, PFX["filmGrain"], rng)
    img = glitch(img, PFX["glitch"], rng)
    return img


def dotted_row(draw, font, x, y, key, value, width):
    draw.text((x, y), key, font=font, fill=ORANGE)
    kb = draw.textbbox((0, 0), key, font=font)
    vb = draw.textbbox((0, 0), value, font=font)
    value_x = x + width - (vb[2] - vb[0])
    start = x + (kb[2] - kb[0]) + 8
    cx = start
    while cx < value_x - 8:
        draw.text((cx, y), ".", font=font, fill=GRAY)
        cx += 7
    draw.text((value_x, y), value, font=font, fill=BLUE)


def section(draw, font, x, y, width, title):
    draw.text((x, y), title, font=font, fill=GRAY)
    draw.line([(x, y + 20), (x + width, y + 20)], fill=RULE, width=1)


def render_card() -> Image.Image:
    card = Image.new("RGB", (CARD_W, CARD_H), BG)
    d = ImageDraw.Draw(card)
    regular = ImageFont.truetype(str(FONT_R), 15)
    bold = ImageFont.truetype(str(FONT_B), 15)
    stats = load_stats()
    x, width = 6, CARD_W - 18

    d.text((x, 4), f"{USERNAME.lower()}@ops", font=bold, fill=WHITE)
    d.line([(x, 26), (x + width, 26)], fill=RULE, width=1)

    rows = [
        ("OS", "Windows, AWS"),
        ("Uptime", age_label()),
        ("Host", "Software engineer first, chess menace second"),
        ("Kernel", "CS · FAU · 3.90"),
        ("i18n", "Hindi, English"),
        ("Variant", "right-handed. bats left. yes, it is a problem"),
        ("Scheduler", "agents by day, Lichess when the build finishes"),
        ("Runlevel", "Boca Raton. peak hours after 22:00"),
    ]
    y = 38
    for key, value in rows:
        dotted_row(d, regular, x, y, key, value, width)
        y += 20

    y += 8
    section(d, regular, x, y, width, "AFK")
    y += 28
    dotted_row(d, regular, x, y, "Hobbies", "chess, Witcher 3, RDR2", width)
    y += 20
    dotted_row(d, regular, x, y, "Lived", "Dehradun, Florida", width)

    y += 26
    section(d, regular, x, y, width, "Contact")
    y += 28
    dotted_row(d, regular, x, y, "X", "@Anm0lKamb0j", width)
    y += 20
    dotted_row(d, regular, x, y, "Instagram", "@anm0l_kamb0j", width)
    y += 20
    dotted_row(d, regular, x, y, "LinkedIn", "in/anm0lkamb0j", width)
    y += 20
    dotted_row(d, regular, x, y, "Email", EMAIL, width)

    y += 26
    section(d, regular, x, y, width, "GitHub Stats")
    y += 28
    dotted_row(d, regular, x, y, "Repos", stats["repos"], width)
    y += 20
    dotted_row(d, regular, x, y, "Contributed", stats["contributed"], width)
    y += 20
    dotted_row(d, regular, x, y, "Stars", stats["stars"], width)
    y += 20
    dotted_row(d, regular, x, y, "Commits", stats["commits"], width)
    y += 20
    dotted_row(d, regular, x, y, "Followers", stats["followers"], width)
    return card


def build() -> Path:
    photo = prepare_photo()
    card = render_card()
    frames = []
    for i in range(6):
        rng = random.Random(21 + i * 13)
        ascii_panel = render_ascii(photo, rng)
        canvas = Image.new("RGB", (W, H), BG)
        # Portrait sits in the upper-left. It does not stretch to card height.
        portrait_y = PAD + max(0, (CARD_H - PORTRAIT_H) // 2)
        canvas.paste(ascii_panel, (PAD, portrait_y))
        canvas.paste(card, (PAD + PORTRAIT_W + GAP, PAD))
        frames.append(canvas)

    still = ASSETS / "header.png"
    frames[0].save(still, "PNG", optimize=True)
    sample = frames[0].quantize(colors=56, method=Image.Quantize.MEDIANCUT)
    indexed = [frame.quantize(palette=sample) for frame in frames]
    gif = ASSETS / "header.gif"
    indexed[0].save(
        gif,
        save_all=True,
        append_images=indexed[1:],
        duration=90,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"wrote {still} and {gif} ({gif.stat().st_size / 1024:.0f} KB)")
    return gif


if __name__ == "__main__":
    build()
