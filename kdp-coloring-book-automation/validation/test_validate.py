"""Unit tests for the pre-upload metadata validator.

Run:  pytest validation/test_validate.py
"""
import argparse
import os
import textwrap

import validate_csv as v

HERE = os.path.dirname(__file__)


def _args(**over):
    base = dict(rules=v.RULES_PATH, final_gate=False, check_files=False,
                assets_root="")
    base.update(over)
    return argparse.Namespace(**base)


HEADER = ("task_id,book_slug,title,subtitle,series,series_number,description,"
          "keyword_1,keyword_2,keyword_3,keyword_4,keyword_5,keyword_6,keyword_7,"
          "category_1,category_2,trim_size,page_count,bleed,paper_type,"
          "cover_file,interior_file,approval_status,version,last_modified_by,"
          "last_modified_at,change_summary,cover_title,cover_subtitle")


def _good_row(**over):
    d = dict(
        task_id="book-1", book_slug="slug-1", title="Title", subtitle="Sub",
        series="", series_number="", description="Desc",
        keyword_1="k1", keyword_2="k2", keyword_3="k3", keyword_4="k4",
        keyword_5="k5", keyword_6="k6", keyword_7="k7",
        category_1="Cat A", category_2="Cat B", trim_size="8.5x8.5",
        page_count="50", bleed="no_bleed", paper_type="white",
        cover_file="c.pdf", interior_file="i.pdf", approval_status="Approved",
        version="1", last_modified_by="gen", last_modified_at="2026-07-03T00:00:00Z",
        change_summary="init", cover_title="CT", cover_subtitle="CS",
    )
    d.update(over)
    cols = HEADER.split(",")
    return ",".join(d[c] for c in cols)


def _write(tmp_path, *rows):
    p = tmp_path / "meta.csv"
    p.write_text(HEADER + "\n" + "\n".join(rows) + "\n")
    return str(p)


def test_valid_row_passes(tmp_path):
    path = _write(tmp_path, _good_row())
    rep = v.validate(path, _args())
    assert rep.ok, rep.errors


def test_missing_required_column(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("task_id,title\nbook-1,Title\n")
    rep = v.validate(str(p), _args())
    assert not rep.ok
    assert any("missing required column" in e for e in rep.errors)


def test_too_few_keywords(tmp_path):
    path = _write(tmp_path, _good_row(keyword_7=""))
    rep = v.validate(path, _args())
    assert not rep.ok
    assert any("keywords" in e for e in rep.errors)


def test_duplicate_keywords(tmp_path):
    path = _write(tmp_path, _good_row(keyword_2="k1"))
    rep = v.validate(path, _args())
    assert not rep.ok
    assert any("duplicate keywords" in e for e in rep.errors)


def test_invalid_trim_size(tmp_path):
    path = _write(tmp_path, _good_row(trim_size="9x9"))
    rep = v.validate(path, _args())
    assert not rep.ok
    assert any("trim_size" in e for e in rep.errors)


def test_duplicate_slug(tmp_path):
    path = _write(tmp_path, _good_row(task_id="b1", book_slug="dup"),
                  _good_row(task_id="b2", book_slug="dup"))
    rep = v.validate(path, _args())
    assert not rep.ok
    assert any("duplicates" in e for e in rep.errors)


def test_page_count_bounds(tmp_path):
    path = _write(tmp_path, _good_row(page_count="5"))
    rep = v.validate(path, _args())
    assert not rep.ok
    assert any("page_count" in e for e in rep.errors)


def test_final_gate_requires_approved(tmp_path):
    path = _write(tmp_path, _good_row(approval_status="Draft"))
    rep = v.validate(path, _args(final_gate=True))
    assert not rep.ok
    assert any("final gate" in e for e in rep.errors)


def test_final_gate_passes_when_approved(tmp_path):
    path = _write(tmp_path, _good_row(approval_status="Approved", version="2"))
    rep = v.validate(path, _args(final_gate=True))
    assert rep.ok, rep.errors
