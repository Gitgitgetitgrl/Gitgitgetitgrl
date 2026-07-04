#!/usr/bin/env python3
"""Ada's weekly campaign review tool.

Reads the AD_CAMPAIGNS.csv tracker and produces the weekly review report:
  - campaigns overdue for review
  - ACoS over target (refine/pause candidates)
  - discovery (auto) campaigns past 14 days (harvest search terms -> manual)
  - spend with no sales (relevance check)
  - stale trend knowledge (newest trend note older than 30 days)

Ada analyzes; humans execute in the Amazon Ads console. This tool never talks to
Amazon — it reviews your tracker so nothing slips.

Usage:
    python ads/campaign_review.py                          # uses the template
    python ads/campaign_review.py path/to/AD_CAMPAIGNS.csv
    python ads/campaign_review.py --today 2026-07-20       # override "today" (testing)
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV = os.path.join(HERE, "templates", "AD_CAMPAIGNS.csv")
TREND_DIR = os.path.join(HERE, "knowledge", "trend-notes")

DISCOVERY_DAYS = 14          # auto-campaign harvest point
STALE_TREND_DAYS = 30        # Ada's stale-knowledge flag


def parse_date(s: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(s.strip())
    except (ValueError, AttributeError):
        return None


def parse_float(s: str) -> float | None:
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def newest_trend_note() -> tuple[str, dt.date] | None:
    notes = sorted(glob.glob(os.path.join(TREND_DIR, "*.md")))
    for path in reversed(notes):
        base = os.path.basename(path)
        d = parse_date(base[:10])
        if d:
            return base, d
    return None


def review(rows: list[dict], today: dt.date) -> list[str]:
    findings: list[str] = []
    for r in rows:
        cid = r.get("campaign_id", "?")
        name = r.get("campaign_name", "")
        state = (r.get("state") or "").strip().lower()

        nrd = parse_date(r.get("next_review_date", ""))
        if state == "enabled" and nrd and nrd < today:
            findings.append(f"[OVERDUE] {cid} ({name}): review was due {nrd}")

        target = parse_float(r.get("acos_target_pct"))
        actual = parse_float(r.get("acos_actual_pct"))
        if state == "enabled" and target and actual and actual > target:
            findings.append(
                f"[ACOS] {cid} ({name}): actual {actual:.0f}% > target {target:.0f}% "
                f"— refine keywords/bids or pause losers")

        start = parse_date(r.get("start_date", ""))
        if (state == "enabled" and (r.get("targeting") or "").strip() == "auto"
                and start and (today - start).days >= DISCOVERY_DAYS):
            findings.append(
                f"[HARVEST] {cid} ({name}): auto campaign running "
                f"{(today - start).days}d — harvest search terms/ASINs into manual campaigns")

        spend = parse_float(r.get("spend_usd"))
        sales = parse_float(r.get("sales_usd"))
        if state == "enabled" and spend and spend > 0 and (sales or 0) == 0:
            findings.append(
                f"[NO-SALES] {cid} ({name}): ${spend:.2f} spent, $0 sales — "
                f"check relevance and negative keywords")
    return findings


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Ada's weekly ads review")
    ap.add_argument("csv", nargs="?", default=DEFAULT_CSV)
    ap.add_argument("--today", default=None, help="YYYY-MM-DD (testing override)")
    args = ap.parse_args(argv)

    today = parse_date(args.today) if args.today else dt.date.today()
    if today is None:
        print("ERROR: --today must be YYYY-MM-DD", file=sys.stderr)
        return 2

    if not os.path.isfile(args.csv):
        print(f"ERROR: tracker not found: {args.csv}", file=sys.stderr)
        return 2
    with open(args.csv, newline="") as f:
        rows = list(csv.DictReader(f))

    print(f"=== Ada weekly review — {today} — {len(rows)} campaign(s) ===")

    note = newest_trend_note()
    if note is None:
        print("[KNOWLEDGE] no dated trend notes found — ask Level 1 for research")
    else:
        base, d = note
        age = (today - d).days
        marker = "STALE" if age > STALE_TREND_DAYS else "ok"
        print(f"[KNOWLEDGE:{marker}] newest trend note: {base} ({age}d old)")
        if age > STALE_TREND_DAYS:
            print("  -> request a refresh from Level 1 before major strategy changes")

    findings = review(rows, today)
    if not findings:
        print("No action items. Keep the weekly cadence.")
    else:
        for f in findings:
            print(f)
        print(f"--- {len(findings)} action item(s). Prepare console instructions and, "
              f"for budget changes, request owner approval via Dalton -> Gen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
