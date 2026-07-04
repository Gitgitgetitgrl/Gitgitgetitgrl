# 02 — Metadata Tracking System (Part 2)

Version-controlled metadata tracking in Google Sheets, with draft/approved separation and
automated validation. The Apps Script lives in
[`../apps_script/kdp_master_automation.gs`](../apps_script/kdp_master_automation.gs); the
column headers and dropdown values are mirrored as CSV templates in
[`../templates/`](../templates) so the local validator and the sheet stay in sync.

## Sheet tabs

| Tab | Purpose | Editable by |
|-----|---------|-------------|
| README | Instructions, rules, workflow notes | Dalton and owner |
| META_DRAFT | Working metadata for AI/human editing | Research/Metadata team |
| META_APPROVED | Final approved metadata for upload | Read-only after approval |
| CHANGELOG | Version history log | System (auto) |
| LISTS | Dropdown validation values | Admin only |
| ARCHIVE | Old approved versions | System (auto) |

## Columns

`META_DRAFT` and `META_APPROVED` share these headers (see `templates/META_DRAFT.csv`):

```
task_id, book_slug, title, subtitle, series, series_number, description,
keyword_1..keyword_7, category_1, category_2, trim_size, page_count, bleed,
paper_type, cover_file, interior_file, approval_status, version,
last_modified_by, last_modified_at, change_summary, cover_title, cover_subtitle
```

`ARCHIVE` uses the same trailing columns plus `archived_at, archive_reason`.

`LISTS` dropdown values (see `templates/LISTS.csv`) — finalized trims include **8.5x11**
(ebook, non-bleed) and **8.5x8.5** (print, mixed bleed).

## Workflow

1. AI drafts metadata in **META_DRAFT**.
2. Validator checks the row (local `validation/validate_csv.py` and/or the in-sheet Apps
   Script check).
3. Dalton reviews the diff.
4. Owner approves the final version.
5. Approved row copied into **META_APPROVED**.
6. Upload automation reads **only** META_APPROVED.

## Apps Script — consolidated features

`kdp_master_automation.gs` provides:

- LISTS-driven named range + dropdown refresh across metadata tabs.
- `ERROR_LOG` logging with daily archived retention (`ERROR_LOG_ARCHIVE`).
- Critical email alerts with a mail-quota check before sending.
- Checkpoint-based continuation using `PropertiesService` (safe batch resume).
- Watchdog monitoring and job-reset tools.
- Built-in test harness `runUnitTests()` for pure/helper logic.

### Installing the Apps Script

1. In your Google Sheet: **Extensions → Apps Script**.
2. Paste the contents of `apps_script/kdp_master_automation.gs`.
3. Save, then run `onOpen` once (authorize when prompted) to install the custom menu.
4. Use the **KDP Automation** menu → *Refresh dropdowns* / *Run self-tests*.
5. `runUnitTests()` validates the pure helpers (no sheet writes) — run it after any edit.
