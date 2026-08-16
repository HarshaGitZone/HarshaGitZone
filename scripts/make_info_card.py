from pathlib import Path
import html


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "profile" / "info-card.svg"


# ============================================================
# YOUR PROFILE DATA
# ============================================================

NAME = "Harsha Vardhan"
USERNAME = "HarshaGitZone"

ROLE = "Full-Stack Developer"
EDUCATION = "B.Tech IT • VNR VJIET '26"
LOCATION = "Hyderabad, India"

STACK = "React • Node.js • Express • MongoDB"
LANGUAGES = "C++ • Java • JavaScript • Python • SQL"

CURRENTLY = "Building & learning"

PROJECTS = [
    "DeepFabric",
    "NoteFabric",
    "FinFlow",
    "GeoNexusAI",
]


# ============================================================
# CARD SETTINGS
# ============================================================

WIDTH = 470
HEIGHT = 370

BACKGROUND = "#0d1117"
BORDER = "#30363d"

PRIMARY = "#e6edf3"
SECONDARY = "#8b949e"
ACCENT = "#2dd4bf"
GREEN = "#39d353"

FONT = "Courier New, monospace"


def esc(value):
    return html.escape(value)


def text(x, y, value, size=14, fill=PRIMARY, weight="normal"):
    return f'''
<text
    x="{x}"
    y="{y}"
    font-family="{FONT}"
    font-size="{size}px"
    font-weight="{weight}"
    fill="{fill}"
>{esc(value)}</text>
'''


def create_svg():

    parts = []

    parts.append(
        f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}">
'''
    )

    # ========================================================
    # ANIMATION
    # ========================================================

    parts.append(
        '''
<style>

@keyframes cardReveal {
    from {
        opacity: 0;
        transform: translateX(15px);
    }

    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.card-line {
    animation-name: cardReveal;
    animation-duration: 0.45s;
    animation-timing-function: ease-out;
    animation-fill-mode: both;
}

@keyframes cursorBlink {
    0%, 45% {
        opacity: 1;
    }

    46%, 100% {
        opacity: 0;
    }
}

.cursor {
    animation: cursorBlink 0.8s infinite;
}

</style>
'''
    )

    # ========================================================
    # CARD
    # ========================================================

    parts.append(
        f'''
<rect
    x="1"
    y="1"
    width="{WIDTH - 2}"
    height="{HEIGHT - 2}"
    rx="12"
    fill="{BACKGROUND}"
    stroke="{BORDER}"
    stroke-width="2"/>
'''
    )

    # ========================================================
    # TERMINAL HEADER
    # ========================================================

    parts.append(
        '''
<circle cx="22" cy="22" r="5" fill="#ff5f56"/>
<circle cx="40" cy="22" r="5" fill="#ffbd2e"/>
<circle cx="58" cy="22" r="5" fill="#27c93f"/>
'''
    )

    parts.append(
        text(
            80,
            27,
            "HarshaGitZone ~ profile",
            12,
            SECONDARY
        )
    )

    # Divider
    parts.append(
        f'''
<line
    x1="18"
    y1="45"
    x2="{WIDTH - 18}"
    y2="45"
    stroke="{BORDER}"
    stroke-width="1"/>
'''
    )

    # ========================================================
    # NAME
    # ========================================================

    parts.append(
        f'''
<g class="card-line" style="animation-delay:0.10s">
'''
    )

    parts.append(
        text(
            22,
            75,
            NAME,
            22,
            PRIMARY,
            "bold"
        )
    )

    parts.append(
        text(
            22,
            96,
            f"@{USERNAME}",
            12,
            ACCENT
        )
    )

    parts.append("</g>")

    # ========================================================
    # PROFILE INFORMATION
    # ========================================================

    rows = [
        ("ROLE", ROLE),
        ("EDU", EDUCATION),
        ("LOCATION", LOCATION),
        ("STACK", STACK),
        ("LANG", LANGUAGES),
        ("STATUS", CURRENTLY),
    ]

    start_y = 125

    for i, (label, value) in enumerate(rows):

        y = start_y + i * 32

        delay = 0.20 + i * 0.07

        parts.append(
            f'''
<g
    class="card-line"
    style="animation-delay:{delay:.2f}s">
'''
        )

        parts.append(
            text(
                22,
                y,
                label,
                11,
                SECONDARY,
                "bold"
            )
        )

        parts.append(
            text(
                105,
                y,
                value,
                12,
                PRIMARY
            )
        )

        parts.append("</g>")

    # ========================================================
    # PROJECTS
    # ========================================================

    project_y = 325

    parts.append(
        '''
<g
    class="card-line"
    style="animation-delay:0.75s">
'''
    )

    parts.append(
        text(
            22,
            project_y,
            "PROJECTS",
            11,
            SECONDARY,
            "bold"
        )
    )

    parts.append("</g>")

    # Projects displayed horizontally
    project_text = " • ".join(PROJECTS)

    parts.append(
        f'''
<g
    class="card-line"
    style="animation-delay:0.82s">
'''
    )

    parts.append(
        text(
            105,
            project_y,
            project_text,
            11,
            ACCENT
        )
    )

    parts.append("</g>")

    # ========================================================
    # TERMINAL CURSOR
    # ========================================================

    parts.append(
        f'''
<rect
    class="cursor"
    x="{WIDTH - 30}"
    y="{HEIGHT - 28}"
    width="7"
    height="13"
    fill="{GREEN}"/>
'''
    )

    parts.append("</svg>")

    return "".join(parts)


def main():

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    print("→ Creating profile info card...")

    svg = create_svg()

    OUTPUT.write_text(
        svg,
        encoding="utf-8"
    )

    print()
    print("✓ Info card created!")
    print(f"✓ Output: {OUTPUT}")
    print()


if __name__ == "__main__":
    main()