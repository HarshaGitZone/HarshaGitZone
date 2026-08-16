from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "source-photo.jpg"
OUTPUT = ROOT / "source-prepped.png"


def remove_background():
    print("→ Loading image...")

    with open(SOURCE, "rb") as f:
        input_data = f.read()

    print("→ Removing background...")
    output_data = remove(input_data)

    temp_path = ROOT / "source-no-bg.png"

    with open(temp_path, "wb") as f:
        f.write(output_data)

    return temp_path


def prepare_image(input_path):
    print("→ Preparing image...")

    image = Image.open(input_path).convert("RGBA")

    # Convert to numpy
    rgba = np.array(image)

    # Separate RGB and alpha
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]

    # Find the bounding box of the person
    mask = alpha > 10

    if not np.any(mask):
        raise RuntimeError("Could not detect the subject.")

    ys, xs = np.where(mask)

    x1 = max(0, xs.min() - 30)
    y1 = max(0, ys.min() - 30)
    x2 = min(rgb.shape[1], xs.max() + 30)
    y2 = min(rgb.shape[0], ys.max() + 30)

    cropped_rgb = rgb[y1:y2, x1:x2]
    cropped_alpha = alpha[y1:y2, x1:x2]

    # Convert to grayscale
    gray = cv2.cvtColor(cropped_rgb, cv2.COLOR_RGB2GRAY)

    # Put the subject on a white background
    white = np.full_like(gray, 255)

    foreground = cropped_alpha.astype(np.float32) / 255.0

    composited = (
        gray.astype(np.float32) * foreground
        + white.astype(np.float32) * (1 - foreground)
    )

    composited = composited.astype(np.uint8)

    # Increase local contrast
    clahe = cv2.createCLAHE(
        clipLimit=2.5,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(composited)

    # Slightly improve contrast
    enhanced = cv2.normalize(
        enhanced,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

    # Save
    Image.fromarray(enhanced).save(OUTPUT)

    print(f"✓ Saved: {OUTPUT}")


if __name__ == "__main__":
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Could not find {SOURCE}"
        )

    temp = remove_background()
    prepare_image(temp)

    print()
    print("✓ Photo preparation complete!")