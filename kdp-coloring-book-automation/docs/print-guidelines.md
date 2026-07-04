# Print Guidelines (Finalized Specs)

**Source:** KDP Paperback Submission Guidelines + finalized bleed decision (July 2, 2026).
These values are encoded in [`../image_pipeline/specs.py`](../image_pipeline/specs.py).

| Format | Trim size | Bleed rule | Bleed PDF size | Resolution |
|--------|-----------|------------|----------------|------------|
| Print (adult/kids/wellness) | 8.5" × 8.5" | Full-bleed if art comes within 1/8" (0.125") of trim edge | 8.625" × 8.75" | 300 DPI |
| Ebook / print-at-home | 8.5" × 11" | Non-bleed (standard) | n/a | 300 DPI |

## Bleed math

- Bleed adds **0.125" on the outer width** (8.5 → 8.625) and **0.125" top + bottom on height**
  (8.5 → 8.75). This is why the square bleed PDF is **8.625" × 8.75"**.
- At 300 DPI that is **2588 × 2625 px** (non-bleed square = 2550 × 2550 px).

## Margins

- Non-bleed outer margin: **≥ 0.25"** (6.4 mm).
- Gutter margin: follows KDP's page-count table (increases with page count).

## Priority order for production

**Adult women gift/sarcastic → Kids → General wellness.**
