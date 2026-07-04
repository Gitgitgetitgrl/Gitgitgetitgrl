# KDP Coloring-Book Production Automation

A gated, human-approved pipeline that turns a coloring-book concept into **print-ready files +
validated metadata** for Amazon KDP. Chain of command: **Owner (NgocETurnal) → Gen
(Project Manager Agent) → Dalton (Team Manager) → three production levels** (1 research,
2 production, 3 upload staging). The agents draft, generate, check, and assemble —
**nothing publishes without human approval.**

> **Separate from ROM.** This project is independent of the `offline-emergency-library/` (ROM)
> project — no shared code. They can share the *same mini-PC* as isolated tools; see
> [`docs/hosting-and-setup.md`](docs/hosting-and-setup.md). It could also be split into its own
> GitHub repository later; it's kept here for now to stay within the current repo.

## Pipeline

```
Concept → Metadata Draft → Image Gen (Gen) → Bleed split → Interior PDFs
        → Handoff packet → QA / Compliance → CSV validation → Human Approval → Upload
```

## Quick start

```bash
bash scripts/setup.sh          # venv + deps (Gen may run this to bootstrap)
source .venv/bin/activate

# dry-run the whole image pipeline with no API/GPU:
python image_pipeline/generate_art.py work/demo/raw --pages 6 --prompt "demo page"
python image_pipeline/apply_bleed.py work/demo/raw work/demo/split
python image_pipeline/build_interior_pdf.py work/demo/split/non_bleed \
    work/demo/interior.pdf --format print_square_nonbleed

# validate metadata + run tests:
python validation/validate_csv.py templates/META_DRAFT.csv
pytest validation/test_validate.py -q
```

## Layout

| Path | What it is |
|------|-----------|
| `docs/` | Parts 1–3.5, print guidelines, operation handbook, hosting/setup |
| `ads/` | **Ada, the Ads Campaign Agent**: persona/system prompt, ads knowledge base + dated trend notes, campaign tracker template, weekly review tool |
| `apps_script/kdp_master_automation.gs` | Google Sheets automation (dropdowns, error log, alerts, checkpoints, self-tests) |
| `validation/` | Pre-upload 4-layer CSV validator + `rules.yaml` + tests |
| `image_pipeline/` | Art generation adapter, bleed rule, interior-PDF builder, handoff packet |
| `templates/` | META_DRAFT / META_APPROVED / LISTS CSV templates (exact headers/values) |
| `schemas/` | JSON Schema for the handoff packet |
| `manual/` | Operator manual (built to PDF) |
| `scripts/` | `setup.sh`, `build_manual_pdf.sh` |

## Documentation

- [`docs/01-team-roles-and-workflow.md`](docs/01-team-roles-and-workflow.md) — roles, levels, gated pipeline
- [`docs/02-metadata-tracking-system.md`](docs/02-metadata-tracking-system.md) — Google Sheets + Apps Script
- [`docs/03-image-generation.md`](docs/03-image-generation.md) — image pipeline + backends
- [`docs/03.5-preupload-validation.md`](docs/03.5-preupload-validation.md) — the 4-layer validator
- [`docs/print-guidelines.md`](docs/print-guidelines.md) — trim/bleed/DPI/margins
- [`docs/operation-handbook.md`](docs/operation-handbook.md) — end-to-end flow
- [`docs/06-infrastructure-roadmap.md`](docs/06-infrastructure-roadmap.md) — the Complete Manual's foundation (Cloud Run, alerting, KDP Agent CLI, FastEmbed) and how this build layers on it
- [`docs/hosting-and-setup.md`](docs/hosting-and-setup.md) — running KDP + ROM on one mini-PC

Build the manual PDF: `bash scripts/build_manual_pdf.sh` → `manual/KDP-Operation-Manual.pdf`.

## Guardrails

- **Human approval before any upload** — no auto-publish.
- **Every handoff carries a checksum** (`write_handoff_packet.py` + JSON schema).
- **META_APPROVED is read-only after approval.**

## Note on image generation

The default `placeholder` backend runs with no API/GPU so you can test the flow. For real art,
use a **cloud** image API (smooth on the AOOSTAR mini-PC's iGPU) or a **local** diffusion model
(needs a real/eGPU GPU). Switching backends doesn't change the rest of the pipeline.

## License

Code and docs here are licensed under the [Apache License 2.0](LICENSE) (see [`NOTICE`](NOTICE)).
This covers the automation code only — **not** the books, art, or metadata you produce, and it
does not bypass Amazon KDP's content review or policies.
