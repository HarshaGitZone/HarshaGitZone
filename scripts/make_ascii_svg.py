from pathlib import Path
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parent.parent

SOURCE = ROOT / "source-prepped.png"
OUTPUT = ROOT / "profile" / "ascii.svg"

# Bright → dark
RAMP = " .`:-=+*cs#%@"

# Portrait size
ASCII_WIDTH = 82

# Character dimensions
FONT_SIZE = 9
CHAR_WIDTH = 5.4
LINE_HEIGHT = 10

# Animation
ROW_DELAY = 0.035
ANIMATION_DURATION = 0.45


def image_to_ascii(image):
    """Convert grayscale image to ASCII."""

    width, height = image.size

    # Compensate for monospace character proportions.
    aspect_ratio = 0.50

    new_height = int(
        height / width * ASCII_WIDTH * aspect_ratio
    )

    image = image.resize(
        (ASCII_WIDTH, new_height)
    )

    image = ImageOps.grayscale(image)

    pixels = image.load()

    lines = []

    for y in range(new_height):
        line = ""

        for x in range(ASCII_WIDTH):
            brightness = pixels[x, y]

            index = int(
                (255 - brightness)
                / 255
                * (len(RAMP) - 1)
            )

            line += RAMP[index]

        lines.append(line.rstrip())

    return lines


def escape_xml(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def create_svg(lines):

    rows = len(lines)

    svg_width = int(
        ASCII_WIDTH * CHAR_WIDTH
    )

    svg_height = int(
        rows * LINE_HEIGHT + 20
    )

    parts = []

    # SVG header
    parts.append(
        f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{svg_width}"
height="{svg_height}"
viewBox="0 0 {svg_width} {svg_height}">
'''
    )

    # CSS animation.
    #
    # Important:
    # The text has a visible default state.
    # Therefore, if an SVG renderer does not support
    # the animation, the portrait still appears.
    parts.append(
        '''
<style>
@keyframes asciiReveal {
    from {
        opacity: 0;
        transform: translateX(-10px);
    }

    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.ascii-row {
    animation-name: asciiReveal;
    animation-duration: 0.45s;
    animation-timing-function: ease-out;
    animation-fill-mode: both;
}
</style>
'''
    )

    # Transparent background.
    parts.append(
        '''
<rect
    width="100%"
    height="100%"
    fill="transparent"/>
'''
    )

    # ASCII rows
    for i, line in enumerate(lines):

        y = i * LINE_HEIGHT + FONT_SIZE

        delay = i * ROW_DELAY

        escaped = escape_xml(line)

        parts.append(
            f'''
<text
    class="ascii-row"
    x="0"
    y="{y}"
    font-family="Courier New, monospace"
    font-size="{FONT_SIZE}px"
    font-weight="600"
    fill="#0f766e"
    xml:space="preserve"
    style="animation-delay: {delay:.3f}s"
>{escaped}</text>
'''
        )

    # Small terminal cursor.
    cursor_y = rows * LINE_HEIGHT - FONT_SIZE

    cursor_delay = (
        rows * ROW_DELAY
        + ANIMATION_DURATION
    )

    parts.append(
        f'''
<rect
    x="0"
    y="{cursor_y}"
    width="5"
    height="{FONT_SIZE + 2}"
    fill="#0f766e"
    opacity="0">
    <animate
        attributeName="opacity"
        values="0;1;0"
        dur="0.7s"
        begin="{cursor_delay:.2f}s"
        repeatCount="3"
    />
</rect>
'''
    )

    parts.append("</svg>")

    return "".join(parts)


def main():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Could not find: {SOURCE}"
        )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    print("→ Loading prepared image...")

    image = Image.open(SOURCE)

    print("→ Converting image to ASCII...")

    lines = image_to_ascii(image)

    print(
        f"→ Generated {len(lines)} ASCII rows"
    )

    print("→ Creating animated SVG...")

    svg = create_svg(lines)

    OUTPUT.write_text(
        svg,
        encoding="utf-8"
    )

    print()
    print("✓ ASCII portrait created!")
    print(f"✓ Output: {OUTPUT}")
    print()


if __name__ == "__main__":
    main()