from pathlib import Path
import json
from datetime import datetime


ROOT = Path(__file__).resolve().parent.parent

DATA = ROOT / "data" / "contributions.json"
OUTPUT = ROOT / "profile" / "contrib-heatmap.svg"


# ============================================================
# SETTINGS
# ============================================================

CELL_SIZE = 13
CELL_GAP = 3

LABEL_WIDTH = 32
TOP_SPACE = 24
BOTTOM_SPACE = 55

WIDTH = 820

FONT = "Arial, sans-serif"

# GitHub-inspired palette
PALETTE = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
]


def load_data():

    if not DATA.exists():
        raise FileNotFoundError(
            f"Could not find {DATA}"
        )

    with open(
        DATA,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def group_into_weeks(days):

    # Convert date strings into datetime objects
    parsed = []

    for day in days:

        date = datetime.strptime(
            day["date"],
            "%Y-%m-%d"
        )

        parsed.append(
            {
                **day,
                "date_obj": date
            }
        )

    parsed.sort(
        key=lambda x: x["date_obj"]
    )

    # GitHub calendar starts on Sunday.
    #
    # Add empty cells before the first Sunday.
    if parsed:

        first = parsed[0]["date_obj"]

        padding = first.weekday()

        # Python:
        # Monday = 0
        # Sunday = 6
        #
        # Convert to Sunday-first index.
        sunday_index = (
            first.weekday() + 1
        ) % 7

        parsed = (
            [
                None
            ] * sunday_index
            + parsed
        )

    weeks = []

    for i in range(
        0,
        len(parsed),
        7
    ):

        week = parsed[
            i:i + 7
        ]

        while len(week) < 7:
            week.append(None)

        weeks.append(week)

    return weeks


def get_level(day):

    if day is None:
        return 0

    level = day.get(
        "level",
        0
    )

    return max(
        0,
        min(
            4,
            int(level)
        )
    )


def esc(value):

    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def create_svg(data):

    days = data["days"]
    stats = data["stats"]

    weeks = group_into_weeks(days)

    # Keep the most recent 53 weeks.
    weeks = weeks[-53:]

    grid_width = (
        len(weeks)
        * (CELL_SIZE + CELL_GAP)
    )

    svg_width = max(
        WIDTH,
        LABEL_WIDTH + grid_width + 15
    )

    svg_height = (
        TOP_SPACE
        + 7 * (CELL_SIZE + CELL_GAP)
        + BOTTOM_SPACE
    )

    parts = []

    # ========================================================
    # SVG HEADER
    # ========================================================

    parts.append(
        f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{svg_width}"
height="{svg_height}"
viewBox="0 0 {svg_width} {svg_height}">
'''
    )

    # ========================================================
    # ANIMATION
    # ========================================================

    parts.append(
        '''
<style>

@keyframes revealCell {

    from {
        opacity: 0;
        transform: translateY(-8px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.cell {
    animation-name: revealCell;
    animation-duration: 0.45s;
    animation-timing-function: ease-out;
    animation-fill-mode: both;
}

</style>
'''
    )

    # ========================================================
    # TITLE
    # ========================================================

    parts.append(
        '''
<text
    x="0"
    y="14"
    font-family="Arial, sans-serif"
    font-size="11"
    font-weight="600"
    fill="#8b949e">
    CONTRIBUTIONS
</text>
'''
    )

    # ========================================================
    # DAY LABELS
    # ========================================================

    labels = [
        ("Mon", 1),
        ("Wed", 3),
        ("Fri", 5),
    ]

    for label, row in labels:

        y = (
            TOP_SPACE
            + row * (CELL_SIZE + CELL_GAP)
            + 10
        )

        parts.append(
            f'''
<text
    x="0"
    y="{y}"
    font-family="{FONT}"
    font-size="9"
    fill="#8b949e">
    {label}
</text>
'''
        )

    # ========================================================
    # CELLS
    # ========================================================

    animation_index = 0

    for week_index, week in enumerate(weeks):

        x = (
            LABEL_WIDTH
            + week_index
            * (CELL_SIZE + CELL_GAP)
        )

        for day_index, day in enumerate(week):

            y = (
                TOP_SPACE
                + day_index
                * (CELL_SIZE + CELL_GAP)
            )

            level = get_level(day)

            fill = PALETTE[level]

            delay = (
                animation_index
                * 0.008
            )

            if day is not None:

                date = day["date"]
                count = day["count"]

                tooltip = (
                    f"{count} contributions "
                    f"on {date}"
                )

            else:

                tooltip = ""

            parts.append(
                f'''
<g
    class="cell"
    style="animation-delay:{delay:.3f}s">
    <rect
        x="{x}"
        y="{y}"
        width="{CELL_SIZE}"
        height="{CELL_SIZE}"
        rx="3"
        fill="{fill}">
        <title>{esc(tooltip)}</title>
    </rect>
</g>
'''
            )

            animation_index += 1

    # ========================================================
    # LEGEND
    # ========================================================

    legend_y = (
        TOP_SPACE
        + 7 * (CELL_SIZE + CELL_GAP)
        + 17
    )

    parts.append(
        f'''
<text
    x="{LABEL_WIDTH}"
    y="{legend_y}"
    font-family="{FONT}"
    font-size="9"
    fill="#8b949e">
    Less
</text>
'''
    )

    for i, color in enumerate(PALETTE):

        x = (
            LABEL_WIDTH
            + 30
            + i * 18
        )

        parts.append(
            f'''
<rect
    x="{x}"
    y="{legend_y - 9}"
    width="12"
    height="12"
    rx="3"
    fill="{color}"/>
'''
        )

    parts.append(
        f'''
<text
    x="{LABEL_WIDTH + 30 + len(PALETTE) * 18 + 5}"
    y="{legend_y}"
    font-family="{FONT}"
    font-size="9"
    fill="#8b949e">
    More
</text>
'''
    )

    # ========================================================
    # STATS
    # ========================================================

    stats_y = legend_y + 25

    total = stats.get(
        "total",
        0
    )

    current = stats.get(
        "current_streak",
        0
    )

    longest = stats.get(
        "longest_streak",
        0
    )

    summary = (
        f"{total:,} contributions"
        f"  •  {current} day streak"
        f"  •  {longest} day best streak"
    )

    parts.append(
        f'''
<text
    x="0"
    y="{stats_y}"
    font-family="{FONT}"
    font-size="10"
    fill="#8b949e">
    {esc(summary)}
</text>
'''
    )

    parts.append("</svg>")

    return "".join(parts)


def main():

    print(
        "→ Loading contribution data..."
    )

    data = load_data()

    print(
        "→ Rendering contribution heatmap..."
    )

    svg = create_svg(data)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT.write_text(
        svg,
        encoding="utf-8"
    )

    print()
    print("✓ Contribution heatmap created!")
    print(f"✓ Output: {OUTPUT}")
    print()


if __name__ == "__main__":
    main()