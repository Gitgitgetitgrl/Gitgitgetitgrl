# Operation Handbook — End-to-End Flow

Executive summary tying Parts 1–3.5 into one operational flow. Sequencing rule:
**Part 1 (roles) → Part 2 (tracking) → Part 3 (image gen) → Part 3.5 (validation) →
QA/Compliance → Listing → Approval → Upload.**

## The flow

1. **Trend/Product Strategy** (Part 1) — pick concept and priority tier
   (adult sarcastic/gift → kids → wellness).
2. **Project setup** — if starting from nothing, **Gen bootstraps the project**:
   `scripts/setup.sh`, create the book work folders, initialize the tracking sheet from
   `templates/`. (See "Gen can set up the project" in
   [`01-team-roles-and-workflow.md`](01-team-roles-and-workflow.md).)
3. **Metadata Draft** (Part 2) — log the task in META_DRAFT, get a `task_id`.
4. **Image Generation** (Part 3) — Gen produces art per the finalized spec, applies the bleed
   rule, hands off with a checksum packet.
5. **Image Cleanup + QA** (Part 3) — fixes and validates against the checklist.
6. **Pre-Upload CSV Validation** (Part 3.5) — 4-layer validation before metadata is approved.
7. **Compliance + File QA** (Part 1 roles) — final compliance pass.
8. **Listing Assembly** (Part 1 roles) — compile the final KDP listing packet.
9. **Human Approval** — mandatory gate, **no auto-publish**.
10. **Upload** — via Upload Agent or manual KDP submission, using the approved packet only.
11. **Post-launch tracking** — logged back into CHANGELOG/ARCHIVE tabs.

## One-command sanity run (placeholder art, no API/GPU)

```bash
bash scripts/setup.sh
source .venv/bin/activate
python image_pipeline/generate_art.py work/demo/raw --pages 6 --prompt "demo coloring page"
python image_pipeline/apply_bleed.py work/demo/raw work/demo/split
python image_pipeline/build_interior_pdf.py work/demo/split/non_bleed \
    work/demo/interior.pdf --format print_square_nonbleed
python validation/validate_csv.py templates/META_DRAFT.csv
pytest validation/test_validate.py -q
```

If all of that passes, the pipeline is healthy and ready for a real concept + backend.

## Guardrails (do not remove)

- **Human approval before any upload** — nothing publishes automatically.
- **Handoff packets are append-only and checksum-verified** — don't skip `write_handoff_packet.py`.
- **META_APPROVED is read-only after approval** — changes go through a new draft + re-approval.
