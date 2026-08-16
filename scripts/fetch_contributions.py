from pathlib import Path
import json
from datetime import datetime

import requests
from bs4 import BeautifulSoup


USERNAME = "HarshaGitZone"

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "contributions.json"

URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_page():
    print(f"→ Fetching contributions for {USERNAME}...")

    response = requests.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=20,
    )

    response.raise_for_status()

    return response.text


def parse_contributions(html):
    print("→ Parsing contribution calendar...")

    soup = BeautifulSoup(html, "html.parser")

    days = []

    for cell in soup.select(
        "td.ContributionCalendar-day"
    ):

        date = cell.get("data-date")
        level = cell.get("data-level")

        if not date:
            continue

        # Fallback
        if level is None:
            level = "0"

        count = 0

        # GitHub stores accessible text in the cell.
        text = cell.get_text(
            " ",
            strip=True
        )

        if text:
            # Try to extract contribution count.
            import re

            match = re.search(
                r"(\d[\d,]*) contribution",
                text
            )

            if match:
                count = int(
                    match.group(1).replace(",", "")
                )

        days.append(
            {
                "date": date,
                "count": count,
                "level": int(level),
            }
        )

    return days


def calculate_stats(days):

    if not days:
        return {
            "total": 0,
            "best_day": None,
            "current_streak": 0,
            "longest_streak": 0,
        }

    total = sum(
        day["count"]
        for day in days
    )

    best = max(
        days,
        key=lambda day: day["count"]
    )

    # Sort chronologically
    sorted_days = sorted(
        days,
        key=lambda day: day["date"]
    )

    longest = 0
    current = 0

    streak = 0

    for day in sorted_days:

        if day["count"] > 0:
            streak += 1
            longest = max(
                longest,
                streak
            )
        else:
            streak = 0

    # Current streak
    for day in reversed(sorted_days):

        if day["count"] > 0:
            current += 1
        else:
            break

    return {
        "total": total,
        "best_day": best,
        "current_streak": current,
        "longest_streak": longest,
    }


def main():

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    html = fetch_page()

    days = parse_contributions(html)

    if not days:
        raise RuntimeError(
            "No contribution data found. "
            "GitHub may have changed its HTML structure."
        )

    stats = calculate_stats(days)

    result = {
        "username": USERNAME,
        "generated_at": datetime.utcnow().isoformat(),
        "days": days,
        "stats": stats,
    }

    OUTPUT.write_text(
        json.dumps(
            result,
            indent=2
        ),
        encoding="utf-8"
    )

    print()
    print("✓ Contribution data saved!")
    print(f"  Days: {len(days)}")
    print(f"  Total: {stats['total']}")
    print(f"  Current streak: {stats['current_streak']}")
    print(f"  Longest streak: {stats['longest_streak']}")
    print(f"  Output: {OUTPUT}")
    print()


if __name__ == "__main__":
    main()