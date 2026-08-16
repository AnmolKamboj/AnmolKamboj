#!/usr/bin/env python3
"""Build every committed visual asset."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from build_chess import build as build_chess
from build_header import build as build_header
from build_space_shooter import build as build_space
from build_wordmark import build as build_wordmark
from config import USERNAME
from refresh_stats import main as refresh_stats

ROOT = Path(__file__).resolve().parents[1]


def try_official_space_shooter() -> bool:
    exe = shutil.which("gh-space-shooter")
    if not exe:
        return False
    out = ROOT / "assets" / "space-shooter.gif"
    cmd = [exe, USERNAME, "--output", str(out), "--strategy", "random", "--fps", "30"]
    print("running", " ".join(cmd))
    result = subprocess.run(cmd, check=False)
    return result.returncode == 0 and out.exists() and out.stat().st_size > 2000


def main() -> None:
    refresh_stats()
    build_wordmark()
    build_header()
    build_chess()
    if not try_official_space_shooter():
        print("official gh-space-shooter unavailable, using themed generator")
        build_space()
    print("done")


if __name__ == "__main__":
    sys.exit(main())
