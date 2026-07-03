# Contributing to ROM

Thanks for helping build the offline emergency library! This is a checklist-style guide to
get you set up and land a change cleanly. The project is deliberately **offline-first** and
**low-dependency** — keep those two principles in mind for everything you add.

## Ground rules (read once)

- **Offline at runtime, always.** Nothing the appliance does *while in use* may require the
  internet. Network access is allowed only in the `while online` setup/download scripts.
- **Cited, safety-aware answers.** Don't weaken Rom's source-citation or the medical-safety
  labelling (clinical vs. traditional/holistic, escalation-to-professional). See `rom/prompts.py`.
- **No bundled content.** The repo ships code + docs only. Never commit `.zim` files, videos,
  images, models, or personal data — `content/` is git-ignored for exactly this reason.
- **Personal-use content stays personal.** Don't add downloaders/links whose default behavior
  redistributes copyrighted material. See `docs/04-licensing-and-legal.md`.

---

## 1. One-time setup checklist

- [ ] Install **Docker** + the **compose** plugin (`docker compose version` works).
- [ ] Install **Python 3.11+** (`python3 --version`).
- [ ] Clone the repo and `cd offline-emergency-library`.
- [ ] Copy the env file: `cp .env.example .env` (tweak ports/model if needed).
- [ ] (For editing Rom's Python) create a local venv and install dev deps:
      ```bash
      python3 -m venv .venv && source .venv/bin/activate
      pip install -r rom/requirements.txt
      ```
- [ ] Confirm the stack builds: `docker compose config` (and `--profile media --profile radio config`).

## 2. Before you start a change

- [ ] Work on a branch off the latest default branch — don't commit straight to `main`.
- [ ] Pick the smallest area that solves the problem; one logical change per PR.
- [ ] If it touches Rom's behavior, re-read `rom/prompts.py` so you don't regress the safety rules.

## 3. Make the change — where things live

| You're changing… | Edit here |
|------------------|-----------|
| Rom's answers / retrieval / API | `rom/app.py`, `rom/common.py`, `rom/prompts.py` |
| Content indexing (new file types, chunking) | `rom/ingest.py` |
| Chat UI | `rom/static/index.html` |
| Services / ports / profiles | `docker-compose.yml`, `.env.example` |
| Setup / hotspot / downloads | `scripts/*.sh` |
| Docs, hardware, content, licensing | `docs/*.md` |
| Operator manual (rebuilds the PDF) | `docs/operation-manual.md` |

**Match the surrounding style.** Keep scripts POSIX-ish bash with `set -euo pipefail`; keep
Python dependency-light (the manual builder and helpers avoid extra pip installs on purpose).

## 4. Test checklist (do the ones your change touches)

- [ ] **Python compiles:** `python3 -m py_compile rom/*.py scripts/build_manual.py`
- [ ] **Shell parses:** `bash -n scripts/*.sh`
- [ ] **Compose validates:** `docker compose config` and
      `docker compose --profile media --profile radio config`
- [ ] **Stack runs** (if you have Docker): `./scripts/03-start.sh`, then check
      `curl -s localhost:8080/health | jq` shows `ollama`/`qdrant` ok.
- [ ] **Rom answers with citations** after `docker compose exec rom python ingest.py`
      (needs at least one file in `content/`).
- [ ] **Manual/PDF builds** if you touched the manual: `./scripts/04-build-manual-pdf.sh`.
- [ ] **New content source?** Add it to `docs/03-content-library-manifest.md` with a size +
      priority, and confirm `ingest.py` picks up the format.

## 5. Commit & PR checklist

- [ ] Commits are focused with a clear message (what + why).
- [ ] No secrets, no `.env`, no `content/` payloads, no large binaries in the diff.
- [ ] Docs updated for any user-facing change (README table, relevant `docs/*.md`).
- [ ] For a new optional service, gate it behind a **compose profile** so it doesn't run or
      draw power by default (see `jellyfin`/`openwebrx` as the pattern).
- [ ] Open the PR against the default branch; describe the change and how you tested it.

## 6. Adding a new content pack (common contribution)

- [ ] Add a download recipe to `scripts/02-download-content.sh` (resolve newest `.zim` from
      the mirror; keep it in a named `pack_*` function).
- [ ] Document it in `docs/03-content-library-manifest.md` (source, size, priority).
- [ ] Verify `ingest.py` indexes it and that `classify_collection()` tags it sensibly
      (add a keyword hint in `rom/common.py` if it's a new domain like `comms`/`geo`).
- [ ] If it's health-related, make sure clinical vs. holistic tagging still holds.

## 7. Adding a new optional service (like Jellyfin/OpenWebRX)

- [ ] Add the service to `docker-compose.yml` under a `profiles: ["name"]` block.
- [ ] Add its port to `.env.example` with a comment.
- [ ] Add a doc (or section) explaining setup, and a URL row to the README table.
- [ ] Note any host requirement (USB passthrough, GPU) and keep it commented-out by default.

---

Questions or a design you're unsure about? Open a draft PR early and ask — especially for
anything that changes Rom's safety behavior or adds a runtime network dependency.
