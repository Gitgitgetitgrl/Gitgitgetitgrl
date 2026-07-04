# 03 — Image Generation (Part 3)

Produce print-ready coloring-page art at correct trim, bleed, and resolution, then hand off
to QA with a verifiable checksum. Implemented by the scripts in
[`../image_pipeline/`](../image_pipeline).

## Inputs required

- Approved book concept.
- Tracking row in the Part 2 sheet with a `task_id`.
- Finalized trim/bleed spec (see [`print-guidelines.md`](print-guidelines.md)).

## Process

1. **Gen** receives the concept packet and generates raw art per page —
   `generate_art.py` (backend: `placeholder` | `cloud` | `local`).
2. Applies the **1/8" bleed rule** automatically — `apply_bleed.py` splits pages into
   `non_bleed/` and `bleed/`.
3. Assembles print-ready interior PDFs at the correct page size — `build_interior_pdf.py`.
4. Writes a **completion/handoff packet** (file count, checksums, status) —
   `write_handoff_packet.py`.
5. Files move to **Cleanup**, then **QA** — no direct jump to Metadata.
6. **Human-approval gate** before the batch is marked "ready for upload prep."

**Owner:** Image Generation Agent (Gen), supervised by the Content/Image team leader (Level 2),
who reports to Dalton.

## Image-generation backends (choose by hardware)

`generate_art.py --backend`:

- **placeholder** (default) — blank framed pages, no API/GPU needed; use it to run and test
  the whole pipeline.
- **cloud** — hosted image API. The smooth path on the AOOSTAR mini-PC (its iGPU is too weak
  for local diffusion). Needs internet + `IMAGE_API_KEY`.
- **local** — local diffusion model (Stable Diffusion / Flux); practical only with a real
  GPU (e.g. an OCuLink eGPU). Fully offline art.

Switching backends does not change any downstream step.

## Artifacts

| Artifact | Format | Purpose |
|----------|--------|---------|
| Raw interior pages (non-bleed) | PNG/TIFF, 300 DPI | Ebook (8.5x11) and non-bleed print pages |
| Raw interior pages (full-bleed) | PNG/TIFF, 300 DPI, +0.125" | Print pages within 1/8" of trim |
| Print-ready interior PDF (square, non-bleed) | PDF, 8.5"x8.5" | KDP paperback, non-bleed pages |
| Print-ready interior PDF (square, bleed) | PDF, 8.625"x8.75" | KDP paperback, bleed pages |
| Ebook interior PDF | PDF, 8.5"x11", non-bleed | Digital / print-at-home |
| Handoff packet (JSON) | JSON | File count, checksums, bleed split, status |
| QA checklist output | CSV/sheet row | Flags for re-render or approval |

## Checklist — before handoff to QA

- [ ] Correct trim confirmed: 8.5"x8.5" print, 8.5"x11" ebook
- [ ] Every page checked against the 1/8" rule (bleed vs non-bleed)
- [ ] Bleed pages sized correctly (8.625"x8.75")
- [ ] All pages at 300 DPI minimum
- [ ] Non-bleed outer margins ≥ 0.25", gutter per KDP page-count table
- [ ] File naming/folder structure matches the Part 2 tracking sheet
- [ ] Handoff packet written with checksum and status
- [ ] Human-approval gate passed before status flips to "ready"

## Example run

```bash
python image_pipeline/generate_art.py work/book-42/raw --pages 50 \
    --prompt "cute farm animals, bold clean outlines, no shading" --backend placeholder
python image_pipeline/apply_bleed.py work/book-42/raw work/book-42/split
python image_pipeline/build_interior_pdf.py work/book-42/split/non_bleed \
    work/book-42/interiors/interior_nonbleed.pdf --format print_square_nonbleed
python image_pipeline/write_handoff_packet.py work/book-42/interiors/interior_nonbleed.pdf \
    work/book-42/handoff_qa.json --task-id book-42 --book-slug cute-farm-animals-ages-4-8 \
    --stage QA --from-team Interior_Creation --to-team QA
```
