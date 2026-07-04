#!/usr/bin/env python3
"""Apply the 1/8" bleed rule and split raw pages into non_bleed/ and bleed/.

Heuristic (per the Print Guidelines): a page is treated as **full-bleed** if its
artwork comes within 1/8" (0.125") of any trim edge; otherwise it's **non-bleed**.
You can force a page's class with a filename tag: `..._bleed.png` / `..._nobleed.png`.

  - non-bleed pages are normalized to exactly the trim size (8.5x8.5) at 300 DPI
  - bleed pages are extended to the full bleed size (8.625x8.75) at 300 DPI

Usage:
    python apply_bleed.py RAW_DIR OUT_DIR [--trim 8.5x8.5]
"""
from __future__ import annotations

import argparse
import os
import sys

from PIL import Image, ImageOps

from specs import (BLEED_IN, DPI, PRINT_SQUARE_BLEED, PRINT_SQUARE_NONBLEED)

IMG_EXTS = (".png", ".tif", ".tiff", ".jpg", ".jpeg")


def content_bbox_margins_in(img: Image.Image) -> tuple[float, float, float, float]:
    """Return (left, top, right, bottom) margins in inches between the image
    edge and the artwork bounding box (non-white content)."""
    gray = ImageOps.grayscale(img)
    # invert so content (dark lines) becomes the non-zero region
    inverted = ImageOps.invert(gray)
    bbox = inverted.getbbox()  # (l, t, r, b) of non-zero, or None if blank
    if bbox is None:
        w, h = img.size
        return (w / DPI, h / DPI, w / DPI, h / DPI)  # fully blank -> huge margins
    l, t, r, b = bbox
    w, h = img.size
    return (l / DPI, t / DPI, (w - r) / DPI, (h - b) / DPI)


def classify(path: str, img: Image.Image) -> bool:
    """True if the page should be full-bleed."""
    name = os.path.basename(path).lower()
    if "_bleed" in name and "_nobleed" not in name:
        return True
    if "_nobleed" in name:
        return False
    margins = content_bbox_margins_in(img)
    return min(margins) < BLEED_IN


def normalize(img: Image.Image, fmt) -> Image.Image:
    target = (fmt.px(fmt.pdf_w_in), fmt.px(fmt.pdf_h_in))
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    if img.size != target:
        img = img.resize(target, Image.LANCZOS)
    return img


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Apply bleed rule and split pages")
    ap.add_argument("raw_dir")
    ap.add_argument("out_dir")
    ap.add_argument("--trim", default="8.5x8.5", help="informational; square print")
    args = ap.parse_args(argv)

    raw = [f for f in sorted(os.listdir(args.raw_dir))
           if f.lower().endswith(IMG_EXTS)]
    if not raw:
        print(f"No images in {args.raw_dir}", file=sys.stderr)
        return 1

    nb_dir = os.path.join(args.out_dir, "non_bleed")
    b_dir = os.path.join(args.out_dir, "bleed")
    os.makedirs(nb_dir, exist_ok=True)
    os.makedirs(b_dir, exist_ok=True)

    counts = {"bleed": 0, "non_bleed": 0}
    for fname in raw:
        path = os.path.join(args.raw_dir, fname)
        with Image.open(path) as img:
            img.load()
            is_bleed = classify(path, img)
            fmt = PRINT_SQUARE_BLEED if is_bleed else PRINT_SQUARE_NONBLEED
            out = normalize(img, fmt)
            dest_dir = b_dir if is_bleed else nb_dir
            stem = os.path.splitext(fname)[0]
            out.save(os.path.join(dest_dir, f"{stem}.png"), dpi=(DPI, DPI))
            counts["bleed" if is_bleed else "non_bleed"] += 1

    print(f"Split {len(raw)} pages -> bleed={counts['bleed']}, "
          f"non_bleed={counts['non_bleed']}")
    print(f"  {b_dir}\n  {nb_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
