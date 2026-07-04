#!/usr/bin/env python3
"""Pre-upload metadata CSV validator (Part 3.5).

Implements the 4-layer validation from the spec against a centralized rules file
(rules.yaml), so no KDP rule is hard-coded in logic:

  Layer 1  File-level    encoding, delimiter, header row, duplicate columns,
                         required columns present
  Layer 2  Field-level   data types / formats / length limits per column
  Layer 3  KDP metadata  title/subtitle length, 7 unique keywords, 2 categories,
                         valid trim/bleed/paper enums, page-count bounds
  Layer 4  Final gate    approval_status == Approved, version present & integer
                         (+ optional file-existence check)

Usage:
    python validate_csv.py META_DRAFT.csv
    python validate_csv.py META_APPROVED.csv --final-gate
    python validate_csv.py META_APPROVED.csv --final-gate --check-files --assets-root ./assets

Exit code 0 = all rows valid; 1 = one or more errors; 2 = file could not be read.
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field

import pandas as pd
import yaml

RULES_PATH = os.path.join(os.path.dirname(__file__), "rules.yaml")


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def err(self, row, msg):
        self.errors.append(f"[row {row}] {msg}")

    def warn(self, row, msg):
        self.warnings.append(f"[row {row}] {msg}")

    @property
    def ok(self) -> bool:
        return not self.errors


def load_rules(path: str = RULES_PATH) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


# --------------------------------------------------------------------------- #
# Layer 1 — file-level
# --------------------------------------------------------------------------- #
def read_csv(path: str, rules: dict, rep: Report) -> pd.DataFrame | None:
    enc = rules["file"].get("encoding", "utf-8")
    delim = rules["file"].get("delimiter", ",")
    try:
        # keep everything as string; we do our own type checks
        df = pd.read_csv(path, dtype=str, encoding=enc, sep=delim,
                         keep_default_na=False)
    except UnicodeDecodeError:
        rep.err(0, f"file is not valid {enc}")
        return None
    except Exception as e:  # noqa: BLE001 - surface any parse failure
        rep.err(0, f"could not parse CSV: {e}")
        return None

    # duplicate columns (pandas renames dupes to name.1 etc.)
    if not rules["file"].get("allow_duplicate_columns", False):
        dupes = [c for c in df.columns if c.endswith(".1")]
        if dupes:
            rep.err(0, f"duplicate column(s) detected: {dupes}")

    missing = [c for c in rules["required_columns"] if c not in df.columns]
    if missing:
        rep.err(0, f"missing required column(s): {missing}")
        return None
    return df


# --------------------------------------------------------------------------- #
# Layers 2 & 3 — field-level + KDP metadata rules
# --------------------------------------------------------------------------- #
def validate_row(idx: int, row: pd.Series, rules: dict, seen_slugs: dict,
                 rep: Report) -> None:
    f = rules["fields"]
    en = rules["enums"]
    r = idx + 2  # human-friendly row number (header = row 1)

    def val(col):
        return (row.get(col) or "").strip()

    # required non-empty core fields
    for col in ("task_id", "book_slug", "title"):
        if not val(col):
            rep.err(r, f"{col} is empty")

    # unique book_slug
    slug = val("book_slug")
    if slug:
        if slug in seen_slugs:
            rep.err(r, f"book_slug '{slug}' duplicates row {seen_slugs[slug]}")
        else:
            seen_slugs[slug] = r

    # length limits
    if len(val("title")) > f["title_max_len"]:
        rep.err(r, f"title exceeds {f['title_max_len']} chars")
    if len(val("subtitle")) > f["subtitle_max_len"]:
        rep.err(r, f"subtitle exceeds {f['subtitle_max_len']} chars")
    if len(val("description")) > f["description_max_len"]:
        rep.err(r, f"description exceeds {f['description_max_len']} chars")

    # keywords: exactly N present, unique, within length
    kws = [val(f"keyword_{i}") for i in range(1, f["keyword_count"] + 1)]
    filled = [k for k in kws if k]
    if len(filled) != f["keyword_count"]:
        rep.err(r, f"expected {f['keyword_count']} keywords, found {len(filled)}")
    for k in filled:
        if len(k) > f["keyword_max_len"]:
            rep.err(r, f"keyword '{k[:20]}...' exceeds {f['keyword_max_len']} chars")
    if f.get("keywords_unique", True):
        lowered = [k.lower() for k in filled]
        if len(set(lowered)) != len(lowered):
            rep.err(r, "duplicate keywords detected")

    # categories: exactly N present
    cats = [val("category_1"), val("category_2")]
    if len([c for c in cats if c]) != f["category_count"]:
        rep.err(r, f"expected {f['category_count']} categories")

    # enums
    for col in ("trim_size", "bleed", "paper_type", "approval_status"):
        v = val(col)
        if v and v not in en[col]:
            rep.err(r, f"{col} '{v}' not in {en[col]}")

    # page_count numeric + bounds
    pc = val("page_count")
    if pc:
        if not pc.isdigit():
            rep.err(r, f"page_count '{pc}' is not an integer")
        else:
            n = int(pc)
            if n < f["min_page_count"] or n > f["max_page_count"]:
                rep.err(r, f"page_count {n} outside "
                           f"{f['min_page_count']}-{f['max_page_count']}")

    # version integer
    ver = val("version")
    if ver and not ver.isdigit():
        rep.err(r, f"version '{ver}' is not an integer")


# --------------------------------------------------------------------------- #
# Layer 4 — final gate (only for rows destined for META_APPROVED)
# --------------------------------------------------------------------------- #
def validate_final_gate(idx: int, row: pd.Series, rules: dict, args,
                        rep: Report) -> None:
    g = rules["final_gate"]
    r = idx + 2

    def val(col):
        return (row.get(col) or "").strip()

    if val("approval_status") != g["required_status"]:
        rep.err(r, f"final gate: approval_status must be '{g['required_status']}'")
    if g.get("require_version", True) and not val("version"):
        rep.err(r, "final gate: version is required")
    if g.get("version_is_integer", True) and val("version") and not val("version").isdigit():
        rep.err(r, "final gate: version must be an integer")

    if args.check_files or g.get("require_files_exist", False):
        for col in ("cover_file", "interior_file"):
            p = val(col)
            if not p:
                rep.err(r, f"final gate: {col} path is empty")
                continue
            full = os.path.join(args.assets_root, p) if args.assets_root else p
            if not os.path.isfile(full):
                rep.err(r, f"final gate: {col} not found at '{full}'")


def validate(path: str, args) -> Report:
    rules = load_rules(args.rules)
    rep = Report()
    df = read_csv(path, rules, rep)
    if df is None:
        return rep

    seen_slugs: dict[str, int] = {}
    for idx, row in df.iterrows():
        validate_row(idx, row, rules, seen_slugs, rep)
        if args.final_gate:
            validate_final_gate(idx, row, rules, args, rep)
    return rep


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="KDP pre-upload metadata validator")
    ap.add_argument("csv", help="path to META_DRAFT.csv or META_APPROVED.csv")
    ap.add_argument("--rules", default=RULES_PATH, help="path to rules.yaml")
    ap.add_argument("--final-gate", action="store_true",
                    help="also enforce Layer 4 (approval/version/files)")
    ap.add_argument("--check-files", action="store_true",
                    help="verify cover_file/interior_file exist")
    ap.add_argument("--assets-root", default="",
                    help="base dir that file paths are relative to")
    args = ap.parse_args(argv)

    if not os.path.isfile(args.csv):
        print(f"ERROR: file not found: {args.csv}", file=sys.stderr)
        return 2

    rep = validate(args.csv, args)

    for w in rep.warnings:
        print(f"WARN  {w}")
    for e in rep.errors:
        print(f"ERROR {e}")

    if rep.ok:
        print(f"OK: {os.path.basename(args.csv)} passed validation.")
        return 0
    print(f"FAILED: {len(rep.errors)} error(s) in {os.path.basename(args.csv)}.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
