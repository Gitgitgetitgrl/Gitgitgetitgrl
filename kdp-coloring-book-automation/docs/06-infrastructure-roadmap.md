# 06 — Infrastructure Roadmap (from the KDP Project Complete Manual)

The owner's **KDP Project Complete Build & Migration Manual** (28 pp., compiled July 2026)
defines a four-phase infrastructure foundation. Its audit explicitly notes that *"the
specific coloring-page generation and Amazon KDP upload automation logic is a separate
build to be layered on top of this foundation"* — **that separate build is this repo folder.**

This doc summarizes the foundation so the two builds stay aligned.

## The four phases (already designed/built per the manual)

### Phase 1 — Apps Script → external APIs (Cloud Run)
- **Strangler pattern**: isolate pure functions in Apps Script, define API boundaries, replace
  internal calls with HTTP one path at a time.
- Keep in Apps Script: triggers, menus, sheet-bound event code (delegating immediately).
- Extract: rule engines, data normalization, PDF generation, AI prompt orchestration,
  long-running workflows.
- Auth: `ScriptApp.getIdentityToken()` → Cloud Run identity-token auth (`openid`,
  `script.external_request` scopes).
- Response contract: `success / data / errors / traceId / version`.

> This repo's `apps_script/kdp_master_automation.gs` follows the "keep it thin" rule — as
> logic grows, extract it to an API per this pattern rather than growing the script.

### Phase 2 — Alerting & observability (Cloud Monitoring / Logging)
- Alert policies for API error rates, worker failures, Cloud Run Job failures (console +
  Terraform variants).
- Logs Explorer filters, e.g. `resource.type="cloud_run_revision" ... severity>=ERROR`.
- Advanced: logging sink → Pub/Sub → webhook formatter for enriched alerts.

### Phase 3 — The KDP Agent CLI (`kdp`)
Local-first agentic CLI (Typer + Rich) that works **with or without** an LLM API key:

| Command | Purpose |
|---------|---------|
| `kdp chat` | Chat with Gen (Project Manager persona) |
| `kdp dalton` | Send tasks/messages to Dalton; inbox, threads, reply-as-dalton |
| `kdp plan` / `kdp deploy` | Terraform plan/validate; trigger GitHub Actions applies |
| `kdp debug` | Cloud Run / Job error logs |
| `kdp index` / `kdp search` | Semantic search over the repo (local vector store) |
| `kdp dashboard` | FastAPI web dashboard (SQLite message bus, live polling) |
| `kdp status` | Project + agent status snapshot |

- Gen ↔ Dalton communicate via a shared **SQLite message bus** (auditable, replayable) —
  mirrors the escalation chain (Dalton → Gen → NgocETurnal).
- Dashboard polls JSON endpoints (3s/2.5s/4s) rather than WebSockets; pauses when the tab
  is hidden.
- Known fixed bug: Starlette `TemplateResponse(request, "template.html", {...})` argument
  order — verified live across all routes.

### Phase 4 — FastEmbed migration (offline embeddings)
- Replaced sentence-transformers + PyTorch with **FastEmbed (ONNX) + LanceDB**:
  image ~18GB → ~800MB, identical quality for this use.
- Model: `BAAI/bge-small-en-v1.5` (384-dim). Env: `DATA_DIR`, `FASTEMBED_CACHE_DIR`,
  `FASTEMBED_MODEL`, `FASTEMBED_DIM=384` (model + dim must change together).
- Build-time model caching; verified offline with `docker run --network none`.

## How this repo folder layers on top

| Foundation (manual) | This build |
|---------------------|-----------|
| Org chain: Owner → Gen → Dalton → Levels 1/2/3 | [`01-team-roles-and-workflow.md`](01-team-roles-and-workflow.md) (with the owner's L1↔L2 swap) |
| Sheets + Apps Script tracking | `apps_script/` + `templates/` + [`02-metadata-tracking-system.md`](02-metadata-tracking-system.md) |
| "Separate build": page generation & upload prep | `image_pipeline/` + `validation/` (this repo's core) |
| Message-bus handoffs | `schemas/handoff_packet.schema.json` (file-based equivalent; adopt the SQLite bus when the CLI lands here) |
| Human approval gate at the top | Enforced in every doc + the validator's final gate |

## Hardware note

The manual's stack (CLI, SQLite bus, FastAPI dashboard, FastEmbed/ONNX embeddings) is
CPU-first and lightweight — it runs comfortably on the AOOSTAR MACO 6850H alongside this
pipeline (see [`hosting-and-setup.md`](hosting-and-setup.md)). Only local *image
generation* needs GPU help (cloud API now, OCuLink eGPU later).
