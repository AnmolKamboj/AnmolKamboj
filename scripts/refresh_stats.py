#!/usr/bin/env python3
"""Pull public GitHub totals into assets/stats.json, then rebuild the header."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

from build_header import build
from config import USERNAME

ROOT = Path(__file__).resolve().parents[1]
STATS_PATH = ROOT / "assets" / "stats.json"


def _headers() -> dict[str, str]:
    token = os.environ.get("ACCESS_TOKEN") or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_stats() -> dict[str, int]:
    user = requests.get(f"https://api.github.com/users/{USERNAME}", headers=_headers(), timeout=30)
    user.raise_for_status()
    profile = user.json()

    repos = 0
    stars = 0
    page = 1
    while True:
        resp = requests.get(
            f"https://api.github.com/users/{USERNAME}/repos",
            headers=_headers(),
            params={"per_page": 100, "page": page, "type": "owner"},
            timeout=30,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        repos += len(batch)
        stars += sum(item.get("stargazers_count", 0) for item in batch)
        page += 1
        if page > 10:
            break

    commits = 0
    token = os.environ.get("ACCESS_TOKEN") or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        created = datetime.fromisoformat(profile["created_at"].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        year = created.year
        while year <= now.year:
            query = """
            query($login: String!, $from: DateTime!, $to: DateTime!) {
              user(login: $login) {
                contributionsCollection(from: $from, to: $to) {
                  totalCommitContributions
                  restrictedContributionsCount
                }
              }
            }
            """
            start = datetime(year, 1, 1, tzinfo=timezone.utc)
            end = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
            payload = {
                "query": query,
                "variables": {
                    "login": USERNAME,
                    "from": start.isoformat(),
                    "to": end.isoformat(),
                },
            }
            gql = requests.post(
                "https://api.github.com/graphql",
                headers=_headers(),
                json=payload,
                timeout=30,
            )
            if gql.ok:
                block = gql.json()["data"]["user"]["contributionsCollection"]
                commits += block["totalCommitContributions"] + block["restrictedContributionsCount"]
            year += 1

    return {
        "repos": repos,
        "stars": stars,
        "followers": int(profile.get("followers") or 0),
        "contributed": repos,
        "commits": commits,
    }


def main() -> None:
    try:
        stats = fetch_stats()
    except Exception as exc:  # keep the header buildable offline
        print(f"stats fetch skipped: {exc}")
        if STATS_PATH.exists():
            build()
            return
        stats = {"repos": 0, "stars": 0, "followers": 0, "contributed": 0, "commits": 0}

    STATS_PATH.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    print("wrote", STATS_PATH, stats)
    build()


if __name__ == "__main__":
    main()
