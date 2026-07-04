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

## Margins (official KDP page-count table)

| Page count | Inside (gutter) | Outside (no bleed) | Outside (with bleed) |
|-----------|-----------------|--------------------|-----------------------|
| 24–150   | 0.375" (9.6 mm) | ≥ 0.25" (6.4 mm) | ≥ 0.375" (9.6 mm) |
| 151–300  | 0.5" (12.7 mm)  | ≥ 0.25" | ≥ 0.375" |
| 301–500  | 0.625" (15.9 mm)| ≥ 0.25" | ≥ 0.375" |
| 501–700  | 0.75" (19.1 mm) | ≥ 0.25" | ≥ 0.375" |
| 701–828  | 0.875" (22.3 mm)| ≥ 0.25" | ≥ 0.375" |

## Additional official KDP rules (from the Paperback Submission Guidelines)

- **Page count:** minimum 24; maximum 828 (rounded up to an even number).
- **Files:** ≤ 650MB; fonts/images embedded; layers flattened; no crop marks, bookmarks,
  comments, watermarks, or emoji in file names. Bleed interiors **must** be PDF.
- **Images:** ≥ 300 DPI (recommend ≤ 600 DPI to keep files manageable).
- **Line width:** ≥ 0.75 pt (0.01") for any chart/graphic lines — relevant for coloring line art.
- **Cover:** one continuous image; 0.125" bleed all sides; keep content ≥ 0.25" from edges.
  Cover width = bleed + back + spine + front + bleed; cover height = bleed + trim height + bleed.
- **Spine:** white paper = pages × 0.002252"; cream = × 0.0025". Spine **text** only on
  books over 79 pages (allow 0.0625" variance at fold lines).
- **Barcode:** optional — KDP auto-places one if you don't supply it.
- **Title creation limit:** 10 new titles per book format per week (request an exception for more).

## Priority order for production

**Priority is dynamic and follows sales data** — Level 1 (Research & Planning) reviews
market trends and re-ranks; the owner approves changes.

- **Current order (July 2026, per Amazon market trends):** Kids → Adult women
  gift/sarcastic → General wellness. *(Kids books are outselling generic adult titles.)*
- Previous order (July 2): Adult gift/sarcastic → Kids → Wellness — superseded.
