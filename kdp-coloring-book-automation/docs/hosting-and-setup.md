# Hosting & Setup — Running KDP (and ROM) on one AOOSTAR MACO 6850H

You own an **AOOSTAR MACO 6850H** (Ryzen 7 6850H, Radeon 680M iGPU, 24GB soldered LPDDR5,
**3× M.2 slots, no SSD yet**, dual USB4 + OCuLink). This doc is the recommended way to run
**both** projects on that one box, kept fully separate.

> The two projects share the *machine*, never the *code*. ROM lives in
> `offline-emergency-library/`; KDP lives here in `kdp-coloring-book-automation/`.

## 1. Storage (you must add SSDs — it ships with none)

Use the 3 M.2 slots to keep the projects on physically separate drives (clean isolation,
easy backup):

| Slot | Drive | Holds |
|------|-------|-------|
| 1 | 500GB–1TB NVMe | OS + apps |
| 2 | 2TB NVMe | **ROM** content (`content/` — full library + media) |
| 3 | 1–2TB NVMe | **KDP** data/scratch (raw art, PDFs, book assets) |

## 2. Software isolation

- **ROM** runs as its existing Docker Compose stack (offline; its own Wi-Fi AP).
- **KDP** runs as a plain Python venv + local scripts, plus cloud services (Google Sheets,
  KDP, and — if used — a cloud image API). No shared services or ports with ROM.

## 3. Image generation on this box

The 680M iGPU is fine for the KDP **automation** (validation, PDF assembly, tracking) but
weak for local diffusion. Pick a tier:

1. **Cloud API** *(recommended, smooth)* — `generate_art.py --backend cloud`. Needs internet.
2. **Local on iGPU** — `--backend local`, low volume only; slow.
3. **OCuLink eGPU** *(future upgrade)* — attach an external GPU via the 64Gbps OCuLink port
   for fast, fully-offline local diffusion (up to ~RTX 4070 Ti class).

The pipeline is backend-agnostic, so you can start on cloud and move to an eGPU later with no
code changes.

## 4. Runtime guidance (24GB RAM ceiling, soldered — not upgradeable)

- **Run one heavy workload at a time.** Don't run ROM's LLM and a large KDP image/PDF job
  simultaneously — 24GB is comfortable for either alone, tight for both at once.
- In practice they're used at different times: ROM is an **offline** emergency tool; KDP is an
  **online** production tool. Contention is unlikely.

## 5. Networking reality

- **ROM = offline** by design (works grid-down).
- **KDP = needs internet** by nature (Google Sheets, KDP upload, cloud image API). This is
  expected — KDP is not an offline system.

## 6. First-time KDP setup on the box

```bash
cd kdp-coloring-book-automation
bash scripts/setup.sh          # venv + dependencies (Gen can run this too)
source .venv/bin/activate
pytest validation/test_validate.py -q     # confirm healthy
```
