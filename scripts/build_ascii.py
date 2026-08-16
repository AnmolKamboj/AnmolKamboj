#!/usr/bin/env python3
"""21st.dev-style binary ASCII portrait. Rasterized for GitHub READMEs."""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "source-portrait.png"
FONT = ASSETS / "fonts" / "JetBrainsMono-Regular.ttf"

TARGET_W = 840
CELL = 8
CHARSET = "01"


def overlay_blend(base: Image.Image, color: tuple[int, int, int], opacity: float) -> Image.Image:
    tint = Image.new("RGB", base.size, color)
    return Image.blend(base.convert("RGB"), tint, opacity)


def apply_adjustments(img: Image.Image) -> Image.Image:
    # Recipe sliders are extreme; keep the photo readable and let glyphs do the crush.
    img = ImageEnhance.Brightness(img).enhance(0.72)
    img = ImageEnhance.Contrast(img).enhance(1.35)
    img = ImageEnhance.Color(img).enhance(1.0)
    img = overlay_blend(img, (0, 0, 0), 0.28)
    return img


def vignette(img: Image.Image, intensity: float) -> Image.Image:
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    pad = int(min(w, h) * 0.08)
    d.ellipse([pad, pad, w - pad, h - pad], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(int(min(w, h) * 0.18)))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.blend(img, Image.composite(img, dark, mask), intensity)


def scanlines(img: Image.Image, intensity: float) -> Image.Image:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    alpha = int(90 * intensity)
    for y in range(0, img.size[1], 3):
        d.line([(0, y), (img.size[0], y)], fill=(0, 0, 0, alpha))
    out = img.convert("RGBA")
    out.alpha_composite(overlay)
    return out.convert("RGB")


def chromatic(img: Image.Image, intensity: float) -> Image.Image:
    shift = max(1, int(6 * intensity))
    r, g, b = img.split()
    r = ImageChops_offset(r, shift, 0)
    b = ImageChops_offset(b, -shift, 0)
    return Image.merge("RGB", (r, g, b))


def ImageChops_offset(channel: Image.Image, x: int, y: int) -> Image.Image:
    return channel.transform(channel.size, Image.Transform.AFFINE, (1, 0, -x, 0, 1, -y))


def bloom(img: Image.Image, intensity: float) -> Image.Image:
    bright = img.point(lambda p: min(255, int(p * 1.25)) if p > 140 else 0)
    glow = bright.filter(ImageFilter.GaussianBlur(6 + int(10 * intensity)))
    return Image.blend(img, ImageChops_add(img, glow), intensity * 0.55)


def ImageChops_add(a: Image.Image, b: Image.Image) -> Image.Image:
    return Image.blend(a, b, 0.5)


def film_grain(img: Image.Image, intensity: float, rng: random.Random) -> Image.Image:
    grain = Image.new("RGB", img.size)
    px = grain.load()
    amp = int(40 * intensity)
    w, h = img.size
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            n = rng.randint(-amp, amp)
            px[x, y] = (n + 128, n + 128, n + 128)
    grain = grain.filter(ImageFilter.GaussianBlur(0.6))
    return Image.blend(img, grain, intensity * 0.18)


def glitch(img: Image.Image, intensity: float, rng: random.Random) -> Image.Image:
    out = img.copy()
    w, h = img.size
    slices = 4 + int(8 * intensity)
    for _ in range(slices):
        y = rng.randint(0, h - 8)
        hh = rng.randint(2, 10)
        dx = rng.randint(-int(24 * intensity) - 2, int(24 * intensity) + 2)
        band = out.crop((0, y, w, min(h, y + hh)))
        out.paste(band, (dx, y))
    return out


def sample_cells(src: Image.Image) -> list[tuple[int, int, tuple[int, int, int], float]]:
    w, h = src.size
    cells = []
    for y in range(0, h, CELL):
        for x in range(0, w, CELL):
            box = (x, y, min(w, x + CELL), min(h, y + CELL))
            tile = src.crop(box)
            color = tile.resize((1, 1), Image.Resampling.BOX).getpixel((0, 0))
            if isinstance(color, int):
                color = (color, color, color)
            lum = (0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]) / 255.0
            cells.append((x, y, color[:3], lum))
    return cells


def render_frame(photo: Image.Image, cells, rng: random.Random, flicker: float) -> Image.Image:
    bg = photo.filter(ImageFilter.GaussianBlur(10))
    bg = ImageEnhance.Brightness(bg).enhance(0.38)
    canvas = bg.copy()
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(str(FONT), CELL)

    for x, y, color, lum in cells:
        if rng.random() < flicker * 0.06:
            continue
        ch = CHARSET[0] if lum < 0.45 else CHARSET[1]
        if rng.random() < flicker * 0.15:
            ch = "1" if ch == "0" else "0"
        # Keep the photo in the glyph color so the face still reads.
        boost = 0.55 + lum * 0.9
        glyph = (
            min(255, int(color[0] * boost + 30)),
            min(255, int(color[1] * boost + 24)),
            min(255, int(color[2] * boost + 18)),
        )
        draw.text((x, y - 1), ch, font=font, fill=glyph)

    img = apply_adjustments(canvas)
    img = chromatic(img, 0.40)
    img = bloom(img, 0.60)
    img = scanlines(img, 0.28)
    img = vignette(img, 0.59)
    img = film_grain(img, 0.40, rng)
    img = glitch(img, 0.20, rng)
    return img


def build() -> Path:
    photo = Image.open(SOURCE).convert("RGB")
    # Crop toward the face/shoulders so the subject fills the frame.
    w, h = photo.size
    side = min(w, int(h * 0.82))
    left = max(0, (w - side) // 2)
    top = int(h * 0.04)
    photo = photo.crop((left, top, min(w, left + side), min(h, top + int(side * 1.15))))
    ratio = TARGET_W / photo.size[0]
    photo = photo.resize((TARGET_W, int(photo.size[1] * ratio)), Image.Resampling.LANCZOS)
    cells = sample_cells(photo)

    frames = []
    for i in range(6):
        rng = random.Random(21 + i * 17)
        frames.append(render_frame(photo, cells, rng, flicker=0.35 + i * 0.02))

    rgb = frames
    sample = rgb[0].quantize(colors=48, method=Image.Quantize.MEDIANCUT)
    indexed = [frame.quantize(palette=sample) for frame in rgb]
    out = ASSETS / "ascii-portrait.gif"
    indexed[0].save(
        out,
        save_all=True,
        append_images=indexed[1:],
        duration=90,
        loop=0,
        optimize=True,
        disposal=2,
    )
    still = ASSETS / "ascii-portrait.png"
    frames[0].save(still, "PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB) and {still}")
    return out


if __name__ == "__main__":
    build()
