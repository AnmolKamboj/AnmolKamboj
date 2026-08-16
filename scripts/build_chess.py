#!/usr/bin/env python3
"""Animated Opera Game in the midnight-brass visual system."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config import PALETTE

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"

# Morphy vs. Duke of Brunswick / Count Isouard, Paris Opera, 1858
# Encoded as from-to squares. Castling and the final mate are explicit.
OPERA = [
    ("e2", "e4"),
    ("e7", "e5"),
    ("g1", "f3"),
    ("d7", "d6"),
    ("d2", "d4"),
    ("c8", "g4"),
    ("d4", "e5"),
    ("g4", "f3"),
    ("d1", "f3"),
    ("d6", "e5"),
    ("f1", "c4"),
    ("g8", "f6"),
    ("f3", "b3"),
    ("d8", "e7"),
    ("b1", "c3"),
    ("c7", "c6"),
    ("c1", "g5"),
    ("b7", "b5"),
    ("c3", "b5"),
    ("c6", "b5"),
    ("c4", "b5"),
    ("b8", "d7"),
    ("e1", "c1"),  # O-O-O, rook handled in apply_move
    ("a8", "d8"),
    ("d1", "d7"),
    ("d8", "d7"),
    ("h1", "d1"),
    ("e7", "e6"),
    ("b5", "d7"),
    ("f6", "d7"),
    ("b3", "b8"),
    ("d7", "b8"),
    ("d1", "d8"),
]

START = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p"] * 8,
    ["."] * 8,
    ["."] * 8,
    ["."] * 8,
    ["."] * 8,
    ["P"] * 8,
    ["R", "N", "B", "Q", "K", "B", "N", "R"],
]


def sq(name: str) -> tuple[int, int]:
    return ord(name[0]) - 97, 8 - int(name[1])


def clone(board: list[list[str]]) -> list[list[str]]:
    return [row[:] for row in board]


def apply_move(board: list[list[str]], src: str, dst: str) -> list[list[str]]:
    next_board = clone(board)
    c0, r0 = sq(src)
    c1, r1 = sq(dst)
    piece = next_board[r0][c0]
    next_board[r0][c0] = "."
    next_board[r1][c1] = piece
    if src == "e1" and dst == "c1" and piece == "K":
        next_board[7][0] = "."
        next_board[7][3] = "R"
    if src == "e1" and dst == "g1" and piece == "K":
        next_board[7][7] = "."
        next_board[7][5] = "R"
    return next_board


def ease(t: float) -> float:
    return 0.5 - 0.5 * math.cos(math.pi * t)


def piece_color(kind: str) -> tuple[int, int, int]:
    return PALETTE["piece_light"] if kind.isupper() else PALETTE["piece_dark"]


def draw_piece(draw: ImageDraw.ImageDraw, kind: str, cx: float, cy: float, size: float, alpha: int = 255) -> None:
    color = (*piece_color(kind), alpha)
    outline = (*PALETTE["ink"], min(255, alpha + 20))
    s = size
    k = kind.lower()

    def poly(pts, fill=color):
        draw.polygon([(cx + x, cy + y) for x, y in pts], fill=fill)

    if k == "p":
        draw.ellipse([cx - s * 0.16, cy - s * 0.30, cx + s * 0.16, cy + 0.02], fill=color, outline=outline)
        poly([(-s * 0.22, s * 0.32), (s * 0.22, s * 0.32), (s * 0.12, s * 0.02), (-s * 0.12, s * 0.02)])
    elif k == "r":
        poly(
            [
                (-s * 0.24, -s * 0.30),
                (-s * 0.10, -s * 0.30),
                (-s * 0.10, -s * 0.18),
                (s * 0.10, -s * 0.18),
                (s * 0.10, -s * 0.30),
                (s * 0.24, -s * 0.30),
                (s * 0.24, s * 0.32),
                (-s * 0.24, s * 0.32),
            ]
        )
    elif k == "n":
        poly(
            [
                (-s * 0.20, s * 0.32),
                (s * 0.22, s * 0.32),
                (s * 0.16, -s * 0.04),
                (s * 0.26, -s * 0.10),
                (s * 0.08, -s * 0.32),
                (-s * 0.06, -s * 0.18),
                (-s * 0.22, -s * 0.08),
                (-s * 0.16, s * 0.04),
            ]
        )
    elif k == "b":
        poly([(0, -s * 0.34), (s * 0.20, s * 0.10), (s * 0.14, s * 0.32), (-s * 0.14, s * 0.32), (-s * 0.20, s * 0.10)])
        draw.line([(cx, cy - s * 0.18), (cx, cy + s * 0.08)], fill=outline, width=2)
    elif k == "q":
        poly(
            [
                (-s * 0.26, s * 0.32),
                (s * 0.26, s * 0.32),
                (s * 0.18, s * 0.04),
                (s * 0.28, -s * 0.22),
                (s * 0.08, -s * 0.06),
                (0, -s * 0.34),
                (-s * 0.08, -s * 0.06),
                (-s * 0.28, -s * 0.22),
                (-s * 0.18, s * 0.04),
            ]
        )
    elif k == "k":
        poly([(-s * 0.22, s * 0.32), (s * 0.22, s * 0.32), (s * 0.16, -s * 0.02), (-s * 0.16, -s * 0.02)])
        draw.rectangle([cx - s * 0.05, cy - s * 0.32, cx + s * 0.05, cy - s * 0.02], fill=color)
        draw.rectangle([cx - s * 0.16, cy - s * 0.22, cx + s * 0.16, cy - s * 0.12], fill=color)


def cell_center(col: int, row: int, origin: int, cell: int) -> tuple[float, float]:
    return origin + col * cell + cell / 2, origin + row * cell + cell / 2


def render_frame_rgb(
    board: list[list[str]],
    moving: tuple[str, str, str] | None,
    t: float,
    captured_fade: tuple[str, tuple[int, int], float] | None,
    last: tuple[str, str] | None,
    caption: str,
    mate: bool,
) -> Image.Image:
    W, H = 760, 470
    cell = 46
    origin = 32
    img = Image.new("RGBA", (W, H), (*PALETTE["bg"], 255))
    d = ImageDraw.Draw(img)
    regular = ImageFont.truetype(str(FONTS / "JetBrainsMono-Regular.ttf"), 16)
    bold = ImageFont.truetype(str(FONTS / "JetBrainsMono-Bold.ttf"), 22)
    small = ImageFont.truetype(str(FONTS / "JetBrainsMono-Regular.ttf"), 13)

    d.text((46, 16), "TACTICAL LAYER  //  OPERA GAME, 1858", font=bold, fill=PALETTE["brass"])
    d.text((46, 42), "Morphy  vs  Duke of Brunswick & Count Isouard", font=small, fill=PALETTE["muted"])

    last_cells = set()
    if last:
        last_cells.add(sq(last[0]))
        last_cells.add(sq(last[1]))

    for r in range(8):
        for c in range(8):
            x0 = origin + c * cell
            y0 = origin + r * cell
            dark = (c + r) % 2 == 1
            fill = PALETTE["square_dark"] if dark else PALETTE["square_light"]
            if (c, r) in last_cells:
                fill = (58, 48, 22) if dark else (86, 70, 28)
            d.rectangle([x0, y0, x0 + cell, y0 + cell], fill=fill)

    files = "abcdefgh"
    for i in range(8):
        d.text((origin + i * cell + 24, origin + 8 * cell + 8), files[i], font=small, fill=PALETTE["dim"])
        d.text((18, origin + i * cell + 22), str(8 - i), font=small, fill=PALETTE["dim"])

    moving_from = sq(moving[1]) if moving else None

    for r in range(8):
        for c in range(8):
            kind = board[r][c]
            if kind == ".":
                continue
            if moving and (c, r) == moving_from:
                continue
            if captured_fade and (c, r) == captured_fade[1] and t < 1:
                continue
            cx, cy = cell_center(c, r, origin, cell)
            draw_piece(d, kind, cx, cy, cell * 0.86)

    if captured_fade and t < 1:
        kind, (c, r), _ = captured_fade
        cx, cy = cell_center(c, r, origin, cell)
        draw_piece(d, kind, cx, cy, cell * 0.86, alpha=int(255 * (1 - t)))

    if moving:
        kind, src, dst = moving
        c0, r0 = sq(src)
        c1, r1 = sq(dst)
        e = ease(t)
        x0, y0 = cell_center(c0, r0, origin, cell)
        x1, y1 = cell_center(c1, r1, origin, cell)
        draw_piece(d, kind, x0 + (x1 - x0) * e, y0 + (y1 - y0) * e, cell * 0.86)

    panel_x = 448
    d.rounded_rectangle([panel_x, 58, 736, 430], radius=10, outline=PALETTE["line"], width=1)
    d.text((panel_x + 18, 78), "WHY THIS GAME", font=small, fill=PALETTE["cyan"])
    story = [
        "Paris Opera, 1858.",
        "Morphy gives material",
        "away, then mates on",
        "the back rank.",
        "",
        "Quiet until the last",
        "move. Same instinct I",
        "want in agent systems",
        "and cloud security.",
    ]
    y = 104
    for line in story:
        d.text((panel_x + 18, y), line, font=regular, fill=PALETTE["text"] if line else PALETTE["dim"])
        y += 18

    d.text((panel_x + 18, 378), caption, font=bold, fill=PALETTE["brass"] if not mate else PALETTE["rose"])
    if mate:
        d.text((panel_x + 18, 404), "CHECKMATE", font=bold, fill=PALETTE["rose"])

    return img


def ply_caption(index: int, src: str, dst: str) -> str:
    move_no = index // 2 + 1
    tag = "W" if index % 2 == 0 else "B"
    return f"{move_no:>2}.  {tag}  {src} → {dst}"


def quantize(frames: list[Image.Image]) -> list[Image.Image]:
    rgb = [frame.convert("RGB") for frame in frames]
    sample = rgb[0].quantize(colors=24, method=Image.Quantize.MEDIANCUT)
    return [frame.quantize(palette=sample) for frame in rgb]


def build() -> Path:
    frames: list[Image.Image] = []
    board = clone(START)
    last = None
    frames_per = 2

    base = render_frame_rgb(board, None, 1, None, last, "1.  opening position", False)
    frames.extend([base] * 3)

    for i, (src, dst) in enumerate(OPERA):
        c1, r1 = sq(dst)
        captured = board[r1][c1] if board[r1][c1] != "." else None
        moving_kind = board[sq(src)[1]][sq(src)[0]]
        fade = (captured, (c1, r1), 1.0) if captured else None
        caption = ply_caption(i, src, dst)
        mate = i == len(OPERA) - 1
        for step in range(frames_per):
            t = (step + 1) / frames_per
            frames.append(render_frame_rgb(board, (moving_kind, src, dst), t, fade, last, caption, False))
        board = apply_move(board, src, dst)
        last = (src, dst)
        still = render_frame_rgb(board, None, 1, None, last, caption, mate)
        frames.extend([still] * (5 if mate else 1))

    indexed = quantize(frames)
    out = ASSETS / "chess.gif"
    indexed[0].save(
        out,
        save_all=True,
        append_images=indexed[1:],
        duration=85,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB, {len(indexed)} frames)")
    return out


if __name__ == "__main__":
    build()
