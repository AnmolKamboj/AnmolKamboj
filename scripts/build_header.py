#!/usr/bin/env python3
"""Render the public dossier header as a retina PNG."""

from __future__ import annotations

import json
import math
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from config import BIRTHDAY, FOCUS, FULL_NAME, HANDLE, LOCATION, PALETTE, TITLE, USERNAME

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"
STATS_PATH = ASSETS / "stats.json"

W, H = 1400, 500
SCALE = 2


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def age_label(today: date | None = None) -> str:
    today = today or date.today()
    years = today.year - BIRTHDAY.year
    months = today.month - BIRTHDAY.month
    if today.day < BIRTHDAY.day:
        months -= 1
    if months < 0:
        years -= 1
        months += 12
    y = f"{years} year" + ("" if years == 1 else "s")
    m = f"{months} month" + ("" if months == 1 else "s")
    return f"{y}, {m}"


def load_stats() -> dict[str, str]:
    defaults = {
        "repos": "—",
        "commits": "—",
        "stars": "—",
        "followers": "—",
        "contributed": "—",
    }
    if STATS_PATH.exists():
        raw = json.loads(STATS_PATH.read_text(encoding="utf-8"))
        for key in defaults:
            value = raw.get(key)
            if isinstance(value, int):
                defaults[key] = f"{value:,}"
            elif value not in (None, ""):
                defaults[key] = str(value)
    return defaults


def rounded(draw: ImageDraw.ImageDraw, box, radius: int, **kwargs) -> None:
    draw.rounded_rectangle(box, radius=radius, **kwargs)


def draw_grid(base: Image.Image) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(overlay)
    step = 28
    for x in range(0, base.size[0], step):
        g.line([(x, 0), (x, base.size[1])], fill=(*PALETTE["grid"], 70), width=1)
    for y in range(0, base.size[1], step):
        g.line([(0, y), (base.size[0], y)], fill=(*PALETTE["grid"], 70), width=1)
    # faint brass scan
    for y in range(40, base.size[1], 140):
        g.line([(0, y), (base.size[0], y)], fill=(*PALETTE["brass"], 18), width=2)
    base.alpha_composite(overlay)


def hud_corners(draw: ImageDraw.ImageDraw, box, length=28, width=2, color=None) -> None:
    color = color or PALETTE["brass"]
    x0, y0, x1, y1 = box
    # TL
    draw.line([(x0, y0 + length), (x0, y0), (x0 + length, y0)], fill=color, width=width)
    # TR
    draw.line([(x1 - length, y0), (x1, y0), (x1, y0 + length)], fill=color, width=width)
    # BL
    draw.line([(x0, y1 - length), (x0, y1), (x0 + length, y1)], fill=color, width=width)
    # BR
    draw.line([(x1 - length, y1), (x1, y1), (x1, y1 - length)], fill=color, width=width)


def draw_seal(canvas: Image.Image, cx: int, cy: int, r: int) -> None:
    seal = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(seal)

    # glow
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([cx - r - 30, cy - r - 30, cx + r + 30, cy + r + 30], fill=(*PALETTE["brass"], 40))
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18)))

    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=PALETTE["brass"], width=3)
    d.ellipse([cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10], outline=PALETTE["cyan_dim"], width=1)

    # dashed outer ticks
    for i in range(36):
        ang = math.radians(i * 10)
        inner = r + 8
        outer = r + (16 if i % 3 == 0 else 12)
        d.line(
            [
                (cx + inner * math.cos(ang), cy + inner * math.sin(ang)),
                (cx + outer * math.cos(ang), cy + outer * math.sin(ang)),
            ],
            fill=PALETTE["brass"] if i % 3 == 0 else PALETTE["line"],
            width=2,
        )

    # hex
    hex_r = r - 36
    pts = [
        (cx + hex_r * math.cos(math.radians(a)), cy + hex_r * math.sin(math.radians(a)))
        for a in range(0, 360, 60)
    ]
    d.polygon(pts, outline=PALETTE["cyan"], width=2)

    bold = font("JetBrainsMono-Bold.ttf", 72)
    regular = font("JetBrainsMono-Regular.ttf", 16)
    ak = "AK"
    bbox = d.textbbox((0, 0), ak, font=bold)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((cx - tw / 2, cy - th / 2 - 10), ak, font=bold, fill=PALETTE["brass"])
    label = "FIELD OPS"
    lb = d.textbbox((0, 0), label, font=regular)
    d.text((cx - (lb[2] - lb[0]) / 2, cy + 38), label, font=regular, fill=PALETTE["cyan"])

    canvas.alpha_composite(seal)


def dotted_row(draw, x, y, key, value, key_font, val_font, width=620) -> None:
    draw.text((x, y), key, font=key_font, fill=PALETTE["brass"])
    kb = draw.textbbox((0, 0), key, font=key_font)
    vb = draw.textbbox((0, 0), value, font=val_font)
    vw = vb[2] - vb[0]
    value_x = x + width - vw
    start = x + (kb[2] - kb[0]) + 14
    end = value_x - 12
    cx = start
    while cx < end:
        draw.ellipse([cx, y + 12, cx + 2, y + 14], fill=PALETTE["line"])
        cx += 8
    draw.text((value_x, y), value, font=val_font, fill=PALETTE["text"])


def build() -> Path:
    img = Image.new("RGBA", (W * SCALE, H * SCALE), (*PALETTE["bg"], 255))
    draw_grid(img)
    d = ImageDraw.Draw(img)

    # scale helper: we draw in 2x pixels
    def S(n: int) -> int:
        return n * SCALE

    margin = S(22)
    rounded(d, [margin, margin, S(W) - margin, S(H) - margin], S(18), fill=(*PALETTE["panel"], 235))
    hud_corners(d, [margin + S(8), margin + S(8), S(W) - margin - S(8), S(H) - margin - S(8)], length=S(26), width=S(2))

    mono12 = font("JetBrainsMono-Regular.ttf", S(13))
    mono14 = font("JetBrainsMono-Regular.ttf", S(15))
    mono16 = font("JetBrainsMono-Regular.ttf", S(17))
    bold18 = font("JetBrainsMono-Bold.ttf", S(20))
    bold28 = font("JetBrainsMono-Bold.ttf", S(32))
    bold42 = font("JetBrainsMono-Bold.ttf", S(46))

    # top bar
    d.text((S(48), S(40)), f"{USERNAME.upper()} / PUBLIC DOSSIER", font=mono12, fill=PALETTE["dim"])
    d.text((S(1040), S(40)), "STATUS", font=mono12, fill=PALETTE["dim"])
    d.ellipse([S(1110), S(42), S(1124), S(56)], fill=PALETTE["cyan"])
    d.text((S(1134), S(40)), "AVAILABLE", font=mono12, fill=PALETTE["cyan"])

    d.text((S(48), S(72)), FULL_NAME.upper(), font=bold42, fill=PALETTE["text"])
    d.text((S(48), S(128)), f"{TITLE}  ·  {FOCUS}", font=mono16, fill=PALETTE["brass"])

    draw_seal(img, S(210), S(310), S(118))

    rows = [
        ("handle", HANDLE),
        ("role", f"{TITLE} · Agentic systems"),
        ("loc", LOCATION),
        ("kernel", "MS CS · FAU · 3.90"),
        ("origin", "Saharanpur → Delhi → Florida"),
        ("uptime", age_label()),
        ("now", "Jarvis · Penti.AI"),
        ("stack", "Python · Go · AWS · Agents"),
    ]
    y = S(168)
    for key, value in rows:
        dotted_row(d, S(400), y, key, value, mono14, mono14, width=S(880))
        y += S(28)

    stats = load_stats()
    boxes = [
        ("REPOS", stats["repos"]),
        ("COMMITS", stats["commits"]),
        ("STARS", stats["stars"]),
        ("FOLLOWERS", stats["followers"]),
        ("CONTRIB", stats["contributed"]),
    ]
    bx, by, bw, bh = S(48), S(430), S(248), S(42)
    for i, (label, value) in enumerate(boxes):
        x0 = bx + i * (bw + S(12))
        rounded(d, [x0, by, x0 + bw, by + bh], S(8), outline=PALETTE["line"], width=S(1))
        d.text((x0 + S(14), by + S(12)), label, font=mono12, fill=PALETTE["dim"])
        vb = d.textbbox((0, 0), value, font=bold18)
        d.text((x0 + bw - (vb[2] - vb[0]) - S(14), by + S(10)), value, font=bold18, fill=PALETTE["brass"])

    out = ASSETS / "header.png"
    img.save(out, "PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB)")
    return out


if __name__ == "__main__":
    build()
