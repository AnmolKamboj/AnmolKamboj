#!/usr/bin/env python3
"""Contribution-graph space shooter in the midnight-brass palette.

Quiet GitHub graphs get a generated constellation so the README still
looks like the arcade GIFs people are shipping. The optional Action can
later overwrite this file with gh-space-shooter once public activity exists.
"""

from __future__ import annotations

import random
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

from config import PALETTE, USERNAME

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"

W, H = 980, 380
WEEKS, DAYS = 37, 7


def fetch_grid() -> list[list[int]]:
    grid = [[0 for _ in range(WEEKS)] for _ in range(DAYS)]
    try:
        resp = requests.get(
            f"https://github-contributions-api.jogruber.de/v4/{USERNAME}",
            timeout=20,
        )
        resp.raise_for_status()
        days = resp.json().get("contributions", [])[-WEEKS * DAYS :]
        for i, item in enumerate(days):
            week, day = divmod(i, DAYS)
            if week < WEEKS:
                grid[day][week] = int(item.get("count") or 0)
    except Exception as exc:
        print(f"contribution fetch fallback: {exc}")
    return grid


def constellation(seed: str) -> list[list[int]]:
    rng = random.Random(seed)
    grid = [[0 for _ in range(WEEKS)] for _ in range(DAYS)]
    for w in range(WEEKS):
        wave = 2 + int(2 * abs((w % 12) - 6) / 6)
        for d in range(DAYS):
            roll = rng.random()
            if d in (0, 6) and roll < 0.55:
                continue
            if roll > 0.22:
                grid[d][w] = 1 + ((w + d + wave) % 4)
            if roll > 0.86:
                grid[d][w] = 6
    return grid


def ship(draw: ImageDraw.ImageDraw, x: float, y: float) -> None:
    draw.polygon(
        [(x, y - 15), (x + 11, y + 13), (x, y + 5), (x - 11, y + 13)],
        fill=PALETTE["brass"],
    )
    draw.polygon([(x - 3, y + 1), (x + 3, y + 1), (x, y - 8)], fill=PALETTE["cyan"])


def enemy(draw: ImageDraw.ImageDraw, x: float, y: float, hp: int) -> None:
    if hp >= 5:
        color = PALETTE["rose"]
    elif hp >= 3:
        color = PALETTE["cyan"]
    else:
        color = PALETTE["brass"]
    draw.rounded_rectangle([x - 6, y - 5, x + 6, y + 5], radius=2, fill=color)


def quantize(frames: list[Image.Image]) -> list[Image.Image]:
    rgb = [frame.convert("RGB") for frame in frames]
    sample = rgb[0].quantize(colors=32, method=Image.Quantize.MEDIANCUT)
    return [frame.quantize(palette=sample) for frame in rgb]


def build() -> Path:
    rng = random.Random(11)
    grid = fetch_grid()
    if sum(sum(row) for row in grid) < 12:
        grid = constellation(USERNAME)

    pad_x, pad_y = 40, 84
    gap_x = (W - pad_x * 2) / (WEEKS - 1)
    gap_y = 26
    positions = {
        (d, w): (pad_x + w * gap_x, pad_y + d * gap_y)
        for d in range(DAYS)
        for w in range(WEEKS)
    }
    alive = {(d, w) for d in range(DAYS) for w in range(WEEKS) if grid[d][w] > 0}

    font = ImageFont.truetype(str(FONTS / "JetBrainsMono-Bold.ttf"), 18)
    small = ImageFont.truetype(str(FONTS / "JetBrainsMono-Regular.ttf"), 13)
    frames: list[Image.Image] = []
    explosions: list[tuple[float, float, int]] = []
    ship_x = W / 2
    score = 0

    def paint(beam: tuple[float, float] | None = None) -> Image.Image:
        img = Image.new("RGBA", (W, H), (*PALETTE["bg"], 255))
        d = ImageDraw.Draw(img)
        d.text((36, 16), "CONTRIBUTION THEATER", font=font, fill=PALETTE["brass"])
        d.text((36, 40), f"@{USERNAME}   score {score:04d}   targets {len(alive):03d}", font=small, fill=PALETTE["muted"])
        for i in range(55):
            d.point((rng.randint(0, W - 1), rng.randint(64, H - 18)), fill=PALETTE["line"])
        for (d0, w0) in list(alive):
            x, y = positions[(d0, w0)]
            enemy(d, x, y, grid[d0][w0])
        if beam:
            d.line([(beam[0], H - 40), beam], fill=PALETTE["cyan"], width=2)
            d.ellipse([beam[0] - 5, beam[1] - 5, beam[0] + 5, beam[1] + 5], outline=PALETTE["brass"])
        for ex, ey, age in explosions:
            rad = 4 + age * 3
            d.ellipse([ex - rad, ey - rad, ex + rad, ey + rad], outline=PALETTE["rose"], width=1)
        ship(d, ship_x, H - 26)
        return img

    weeks = sorted({w for _d, w in alive})
    frames.append(paint())
    for w in weeks:
        col = [(d, w) for d in range(DAYS) if (d, w) in alive]
        if not col:
            continue
        tx = positions[col[0]][0]
        for _ in range(2):
            ship_x += (tx - ship_x) * 0.6
            frames.append(paint())
        top = positions[col[0]]
        frames.append(paint((top[0], top[1])))
        for d, ww in col:
            alive.remove((d, ww))
            score += grid[d][ww]
            explosions.append((*positions[(d, ww)], 0))
        explosions = [(x, y, a + 1) for x, y, a in explosions if a < 3]
        frames.append(paint())

    frames.extend([paint()] * 5)

    indexed = quantize(frames)
    out = ASSETS / "space-shooter.gif"
    indexed[0].save(
        out,
        save_all=True,
        append_images=indexed[1:],
        duration=60,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB, {len(indexed)} frames)")
    return out


if __name__ == "__main__":
    build()
