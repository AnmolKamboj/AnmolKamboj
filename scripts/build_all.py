#!/usr/bin/env python3
"""Build the visuals that ship in the profile README."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from build_ascii import build as build_ascii
from build_chess import build as build_chess
from config import USERNAME

ROOT = Path(__file__).resolve().parents[1]


def try_official_space_shooter() -> bool:
    exe = shutil.which("gh-space-shooter") or str(ROOT / ".venv" / "Scripts" / "gh-space-shooter.exe")
    if not Path(exe).exists() and not shutil.which("gh-space-shooter"):
        return False
    out = ROOT / "assets" / "space-shooter.gif"
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    cmd = [exe, USERNAME, "--output", str(out), "--strategy", "random", "--fps", "30"]
    print("running", " ".join(cmd))
    result = subprocess.run(cmd, check=False, env=env)
    return result.returncode == 0 and out.exists() and out.stat().st_size > 2000


def main() -> None:
    build_ascii()
    build_chess()
    if not try_official_space_shooter():
        print("official gh-space-shooter failed; keep the last GIF if present")
    print("done")


if __name__ == "__main__":
    sys.exit(main())
