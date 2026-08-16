#!/usr/bin/env python3
"""Build the visuals that ship in the profile README."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from build_chess import build as build_chess
from build_header import build as build_header
from build_stack import build as build_stack
from config import USERNAME
from refresh_stats import fetch_stats, STATS_PATH
import json

ROOT = Path(__file__).resolve().parents[1]


def refresh() -> None:
    try:
        stats = fetch_stats()
        STATS_PATH.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
        print("stats", stats)
    except Exception as exc:
        print("stats fetch skipped:", exc)


def try_official_space_shooter() -> bool:
    exe = ROOT / ".venv" / "Scripts" / "gh-space-shooter.exe"
    if not exe.exists():
        exe = shutil.which("gh-space-shooter")
        if not exe:
            return False
    out = ROOT / "assets" / "space-shooter.gif"
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    cmd = [str(exe), USERNAME, "--output", str(out), "--strategy", "random", "--fps", "30"]
    print("running", " ".join(cmd))
    result = subprocess.run(cmd, check=False, env=env)
    return result.returncode == 0 and out.exists() and out.stat().st_size > 2000


def main() -> None:
    refresh()
    build_header()
    build_stack()
    build_chess()
    print("done")


if __name__ == "__main__":
    sys.exit(main())
