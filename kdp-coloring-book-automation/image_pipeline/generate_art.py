#!/usr/bin/env python3
"""Image-generation ADAPTER for 'Gen' (the Image Generation Agent).

One interface, swappable backends — decided by the hardware you run on:

  placeholder  (default) generates blank line-art page frames locally with no
               dependencies beyond Pillow. Lets the whole pipeline run/test with
               no API key or GPU. Use it to validate the flow end to end.
  cloud        calls a hosted image API (smooth path on the AOOSTAR mini-PC's
               iGPU, which is too weak for local diffusion). Needs internet +
               an API key. Implement `_backend_cloud` for your chosen provider.
  local        runs a local diffusion model (Stable Diffusion / Flux) on a GPU.
               Only practical with a real/eGPU GPU (e.g. via OCuLink). Implement
               `_backend_local`.

Switching backends never changes the rest of the pipeline (apply_bleed ->
build_interior_pdf -> write_handoff_packet stay identical).

Usage:
    python generate_art.py OUT_DIR --pages 8 --backend placeholder \
        --prompt "cute farm animals, bold clean outlines, no shading"
"""
from __future__ import annotations

import argparse
import os

from PIL import Image, ImageDraw

from specs import DPI, PRINT_SQUARE_NONBLEED


def _backend_placeholder(out_dir: str, pages: int, prompt: str, fmt) -> list[str]:
    """Generate blank framed pages at trim size — a stand-in for real art."""
    w, h = fmt.px(fmt.pdf_w_in), fmt.px(fmt.pdf_h_in)
    margin = round(0.5 * DPI)
    made = []
    for i in range(1, pages + 1):
        img = Image.new("RGB", (w, h), "white")
        d = ImageDraw.Draw(img)
        d.rectangle([margin, margin, w - margin, h - margin], outline="black", width=4)
        d.text((margin + 20, margin + 20), f"[placeholder page {i}]\n{prompt}",
               fill="black")
        path = os.path.join(out_dir, f"page_{i:03d}.png")
        img.save(path, dpi=(DPI, DPI))
        made.append(path)
    return made


def _backend_cloud(out_dir: str, pages: int, prompt: str, fmt) -> list[str]:
    """Call a hosted image API. Implement for your provider.

    Fill in an HTTP call to your chosen text-to-image endpoint, save each
    returned page to out_dir at trim size / 300 DPI, and return the paths.
    Keep the API key in an env var (e.g. IMAGE_API_KEY) — never commit it.
    """
    raise NotImplementedError(
        "cloud backend not configured. Add your image API call in "
        "_backend_cloud() and set IMAGE_API_KEY. Until then use "
        "--backend placeholder to exercise the pipeline.")


def _backend_local(out_dir: str, pages: int, prompt: str, fmt) -> list[str]:
    """Run a local diffusion model (needs a capable GPU, e.g. via OCuLink eGPU)."""
    raise NotImplementedError(
        "local backend not configured. Wire up a local diffusion pipeline "
        "(Stable Diffusion / Flux) here; practical only with a real GPU.")


BACKENDS = {
    "placeholder": _backend_placeholder,
    "cloud": _backend_cloud,
    "local": _backend_local,
}


def generate(out_dir: str, pages: int, prompt: str, backend: str = "placeholder",
             fmt=PRINT_SQUARE_NONBLEED) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    return BACKENDS[backend](out_dir, pages, prompt, fmt)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Generate raw coloring-page art")
    ap.add_argument("out_dir")
    ap.add_argument("--pages", type=int, default=8)
    ap.add_argument("--prompt", default="coloring page, bold clean outlines")
    ap.add_argument("--backend", choices=list(BACKENDS), default="placeholder")
    args = ap.parse_args(argv)

    made = generate(args.out_dir, args.pages, args.prompt, args.backend)
    print(f"Generated {len(made)} page(s) via '{args.backend}' -> {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
