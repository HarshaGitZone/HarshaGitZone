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

    import re

    # ------------------------------------------------------
    # Build a date -> contribution count map
    #
    # GitHub currently puts the accessible contribution
    # descriptions inside the parent <tr>, rather than
    # directly on each contribution <td>.
    # ------------------------------------------------------

    contribution_counts = {}

    rows = soup.select(
        "tr"
    )

    for row in rows:

        text = row.get_text(
            " ",
            strip=True
        )

        if not text:
            continue

        # Examples:
        #
        # 1 contribution on October 19th.
        # 6 contributions on December 21st.
        # 200 contributions on August 9th.
        #
        matches = re.findall(
            r"([\d,]+)\s+contributions?\s+on\s+"
            r"([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)",
            text,
            re.IGNORECASE
        )

        for count_text, month, day in matches:

            count = int(
                count_text.replace(",", "")
            )

            month_number = datetime.strptime(
                month,
                "%B"
            ).month

            key = (
                f"{month_number:02d}-"
                f"{int(day):02d}"
            )

            contribution_counts[key] = count

    print(
        f"  Extracted {len(contribution_counts)} "
        "contribution counts"
    )

    # ------------------------------------------------------
    # Extract the actual calendar cells
    # ------------------------------------------------------

    cells = soup.select(
        ".ContributionCalendar-day"
    )

    print(
        f"  Found {len(cells)} contribution cells"
    )

    days = []

    for cell in cells:

        date = cell.get(
            "data-date"
        )

        if not date:
            continue

        # --------------------------------------------------
        # Contribution level
        # --------------------------------------------------

        level = cell.get(
            "data-level",
            "0"
        )

        try:
            level = int(level)
        except (
            TypeError,
            ValueError
        ):
            level = 0

        # --------------------------------------------------
        # Contribution count
        # --------------------------------------------------

        try:
            parsed_date = datetime.strptime(
                date,
                "%Y-%m-%d"
            )

            key = (
                f"{parsed_date.month:02d}-"
                f"{parsed_date.day:02d}"
            )

            count = contribution_counts.get(
                key,
                0
            )

        except ValueError:
            count = 0

        days.append(
            {
                "date": date,
                "count": count,
                "level": level,
            }
        )

    # ------------------------------------------------------
    # Remove duplicate dates
    # ------------------------------------------------------

    unique_days = {}

    for day in days:
        unique_days[day["date"]] = day

    days = list(
        unique_days.values()
    )

    # ------------------------------------------------------
    # Sort chronologically
    # ------------------------------------------------------

    days.sort(
        key=lambda day: day["date"]
    )

    # ------------------------------------------------------
    # Debug summary
    # ------------------------------------------------------

    non_zero = [
        day
        for day in days
        if day["count"] > 0
    ]

    print(
        f"  Days with contributions: "
        f"{len(non_zero)}"
    )

    if non_zero:
        print(
            f"  Sample: {non_zero[:5]}"
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