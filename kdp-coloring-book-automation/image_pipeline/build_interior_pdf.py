#!/usr/bin/env python3
"""Assemble a folder of same-format page images into a print-ready interior PDF.

The output PDF's physical page size is derived from pixel size / 300 DPI, so it
lands at exactly the KDP trim/bleed dimensions:
  - print_square_nonbleed -> 8.5" x 8.5"
  - print_square_bleed    -> 8.625" x 8.75"
  - ebook                 -> 8.5" x 11"

Usage:
    python build_interior_pdf.py PAGES_DIR OUT.pdf --format print_square_nonbleed
"""
from __future__ import annotations

import argparse
import os
import sys

from PIL import Image

from specs import DPI, FORMATS

IMG_EXTS = (".png", ".tif", ".tiff", ".jpg", ".jpeg")


def load_pages(pages_dir: str, fmt) -> list[Image.Image]:
    files = [f for f in sorted(os.listdir(pages_dir))
             if f.lower().endswith(IMG_EXTS)]
    if not files:
        raise SystemExit(f"No page images found in {pages_dir}")
    target = (fmt.px(fmt.pdf_w_in), fmt.px(fmt.pdf_h_in))
    pages = []
    for f in files:
        img = Image.open(os.path.join(pages_dir, f)).convert("RGB")
        if img.size != target:
            raise SystemExit(
                f"{f} is {img.size}px but format '{fmt.name}' expects {target}px "
                f"({fmt.pdf_w_in}x{fmt.pdf_h_in} in @ {DPI} DPI). "
                f"Run apply_bleed.py first or pick the right --format.")
        pages.append(img)
    return pages


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build print-ready interior PDF")
    ap.add_argument("pages_dir")
    ap.add_argument("out_pdf")
    ap.add_argument("--format", choices=list(FORMATS), required=True)
    args = ap.parse_args(argv)

    fmt = FORMATS[args.format]
    pages = load_pages(args.pages_dir, fmt)

    os.makedirs(os.path.dirname(os.path.abspath(args.out_pdf)), exist_ok=True)
    first, rest = pages[0], pages[1:]
    first.save(args.out_pdf, "PDF", resolution=float(DPI),
               save_all=True, append_images=rest)

    print(f"Wrote {args.out_pdf}: {len(pages)} page(s) at "
          f"{fmt.pdf_w_in}x{fmt.pdf_h_in} in ({fmt.name}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
