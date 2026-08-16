#!/usr/bin/env python3
"""A real-looking chessboard animation. Opera Game, plus captions about actually playing."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
PIECES = ASSETS / "pieces"
FONTS = ASSETS / "fonts"

# Morphy vs Duke of Brunswick / Count Isouard, Paris 1858
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
    ("e1", "c1"),
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

QUIPS = [
    "Opening. I would already be checking the eval bar.",
    "e4 e5. Honest chess. I respect it and I still play the London sometimes.",
    "Knight out. In my games this is where I forget a pawn is hanging.",
    "Philidor. Solid. Also the line I play when I am scared.",
    "Center break. This is the part I love.",
    "Bishop pins the knight. I have fallen for this in 3+0 more times than I will admit.",
    "Takes. Takes. The opera crowd is still finding their seats.",
    "Bishop takes knight. I would have spent two minutes here.",
    "Queen recaptures. Clean.",
    "Pawn takes back. Still equal-ish. I would already be down a tempo in blitz.",
    "Bishop to c4. Aimed at f7. I know this feeling from the other side.",
    "Knight develops. Good. I usually move the same piece twice instead.",
    "Queen to b3. Double attack. The kind of move I see one ply too late.",
    "Queen to e7. Defending. I have played this and still lost the pawn.",
    "Another knight. Development. My coaches in my head are clapping.",
    "c6. Stops the knight, or so it looks.",
    "Bishop to g5. Pin. I hate pins. I also set them constantly.",
    "b5. Aggressive. This is where I would get excited and miss the tactic.",
    "Knight takes. Morphy just gives the piece away. I would panic.",
    "Pawn takes back. Looks winning if you stop calculating here. I stop calculating here.",
    "Bishop takes, check. The king is not having a good night.",
    "Knight blocks. Reasonable. Still doomed.",
    "Queenside castle. Rook slides over like it planned this all along.",
    "Rook to d8. Trying to hold the file. I have been here. It does not hold.",
    "Rook takes knight. The exchange sacrifice I would never play in a real game.",
    "Rook takes back. Feels safe. Is not safe.",
    "Other rook joins. This is the part I rewind on YouTube.",
    "Queen to e6. Looks like it covers everything.",
    "Bishop takes, check. It does not cover everything.",
    "Knight takes. Material is weird. The king is worse.",
    "Queen to b8. Check. I would have stared at this for a minute and still missed it.",
    "Knight takes the queen. Free queen? Free queen.",
    "Rook to d8. Mate. I love this game. I have never finished a game this clean.",
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

FILES = {
    "K": "wK.png",
    "Q": "wQ.png",
    "R": "wR.png",
    "B": "wB.png",
    "N": "wN.png",
    "P": "wP.png",
    "k": "bK.png",
    "q": "bQ.png",
    "r": "bR.png",
    "b": "bB.png",
    "n": "bN.png",
    "p": "bP.png",
}

LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (246, 246, 105)
BOARD_BG = (48, 46, 43)
PANEL_BG = (32, 30, 28)
TEXT = (240, 230, 210)
MUTED = (180, 168, 150)
ACCENT = (129, 182, 76)


def sq(name: str) -> tuple[int, int]:
    return ord(name[0]) - 97, 8 - int(name[1])


def clone(board):
    return [row[:] for row in board]


def apply_move(board, src, dst):
    next_board = clone(board)
    c0, r0 = sq(src)
    c1, r1 = sq(dst)
    piece = next_board[r0][c0]
    next_board[r0][c0] = "."
    next_board[r1][c1] = piece
    if src == "e1" and dst == "c1" and piece == "K":
        next_board[7][0] = "."
        next_board[7][3] = "R"
    return next_board


def ease(t: float) -> float:
    return 0.5 - 0.5 * math.cos(math.pi * t)


def load_pieces(size: int) -> dict[str, Image.Image]:
    out = {}
    for kind, name in FILES.items():
        img = Image.open(PIECES / name).convert("RGBA")
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        out[kind] = img
    return out


def paste_piece(canvas: Image.Image, sprites: dict[str, Image.Image], kind: str, cx: float, cy: float, alpha: int = 255):
    sprite = sprites[kind]
    if alpha < 255:
        sprite = sprite.copy()
        sprite.putalpha(sprite.getchannel("A").point(lambda a: int(a * alpha / 255)))
    canvas.alpha_composite(sprite, (int(cx - sprite.size[0] / 2), int(cy - sprite.size[1] / 2)))


def render(board, sprites, moving, t, last, caption, mate) -> Image.Image:
    cell = 46
    origin = 24
    board_px = cell * 8
    W, H = 760, 460
    img = Image.new("RGBA", (W, H), BOARD_BG + (255,))
    d = ImageDraw.Draw(img)
    regular = ImageFont.truetype(str(FONTS / "JetBrainsMono-Regular.ttf"), 15)
    bold = ImageFont.truetype(str(FONTS / "JetBrainsMono-Bold.ttf"), 18)
    small = ImageFont.truetype(str(FONTS / "JetBrainsMono-Regular.ttf"), 12)

    d.text((28, 12), "I actually play this game. Morphy just plays it better.", font=bold, fill=TEXT)

    last_cells = set()
    if last:
        last_cells.add(sq(last[0]))
        last_cells.add(sq(last[1]))

    for r in range(8):
        for c in range(8):
            x0 = origin + c * cell
            y0 = 40 + r * cell
            fill = DARK if (c + r) % 2 else LIGHT
            if (c, r) in last_cells:
                fill = HIGHLIGHT
            d.rectangle([x0, y0, x0 + cell, y0 + cell], fill=fill)

    for i in range(8):
        d.text((origin + i * cell + 22, 40 + board_px + 4), "abcdefgh"[i], font=small, fill=MUTED)
        d.text((10, 40 + i * cell + 20), str(8 - i), font=small, fill=MUTED)

    moving_from = sq(moving[1]) if moving else None

    for r in range(8):
        for c in range(8):
            kind = board[r][c]
            if kind == ".":
                continue
            if moving and (c, r) == moving_from:
                continue
            cx = origin + c * cell + cell / 2
            cy = 40 + r * cell + cell / 2
            paste_piece(img, sprites, kind, cx, cy)

    if moving:
        kind, src, dst = moving
        c0, r0 = sq(src)
        c1, r1 = sq(dst)
        e = ease(t)
        x0 = origin + c0 * cell + cell / 2
        y0 = 40 + r0 * cell + cell / 2
        x1 = origin + c1 * cell + cell / 2
        y1 = 40 + r1 * cell + cell / 2
        paste_piece(img, sprites, kind, x0 + (x1 - x0) * e, y0 + (y1 - y0) * e)

    panel = [440, 36, 740, 440]
    d.rounded_rectangle(panel, radius=10, fill=PANEL_BG)
    d.text((456, 50), "WHY THIS IS HERE", font=small, fill=ACCENT)
    blurb = [
        "I play chess a lot. Blitz, rapid,",
        "sometimes a slow game I abandon",
        "when dinner happens.",
        "",
        "This is the Opera Game. Morphy",
        "gives a queen and still mates.",
        "I give a queen and open Lichess",
        "analysis so I can feel seen.",
        "",
        "Theatre kid who likes a good",
        "finish. Also a person who has",
        "premoved into mate more than once.",
    ]
    y = 72
    for line in blurb:
        d.text((456, y), line, font=regular, fill=TEXT if line else MUTED)
        y += 16

    wrapped = []
    words = caption.split()
    line = ""
    for word in words:
        trial = (line + " " + word).strip()
        if len(trial) > 34:
            wrapped.append(line)
            line = word
        else:
            line = trial
    if line:
        wrapped.append(line)
    d.multiline_text((456, 318), "\n".join(wrapped), font=regular, fill=ACCENT if not mate else (230, 80, 80), spacing=4)
    if mate:
        d.text((456, 410), "CHECKMATE. I would have resigned on move 12.", font=small, fill=(230, 80, 80))

    return img.convert("RGB")


def quantize(frames: list[Image.Image]) -> list[Image.Image]:
    sample = frames[0].quantize(colors=48, method=Image.Quantize.MEDIANCUT)
    return [frame.quantize(palette=sample) for frame in frames]


def build() -> Path:
    sprites = load_pieces(40)
    frames = []
    board = clone(START)
    last = None
    frames.append(render(board, sprites, None, 1, last, QUIPS[0], False))

    for i, (src, dst) in enumerate(OPERA):
        moving_kind = board[sq(src)[1]][sq(src)[0]]
        caption = QUIPS[min(i + 1, len(QUIPS) - 1)]
        mate = i == len(OPERA) - 1
        frames.append(render(board, sprites, (moving_kind, src, dst), 1.0, last, caption, False))
        board = apply_move(board, src, dst)
        last = (src, dst)
        frames.append(render(board, sprites, None, 1, last, caption, mate))
        if mate:
            frames.extend([frames[-1]] * 4)

    indexed = quantize(frames)
    out = ASSETS / "chess.gif"
    indexed[0].save(
        out,
        save_all=True,
        append_images=indexed[1:],
        duration=95,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB, {len(indexed)} frames)")
    return out


if __name__ == "__main__":
    build()
