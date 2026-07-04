#!/usr/bin/env python3
"""Emit a Part 1 handoff packet (JSON) describing a completed artifact.

Computes the artifact sha256, fills the packet, validates it against
schemas/handoff_packet.schema.json, and writes it out. Used by Gen after image
generation to hand the batch to QA with a verifiable checksum.

Usage:
    python write_handoff_packet.py ARTIFACT.zip OUT.json \
        --task-id book-42 --book-slug cute-farm-animals-ages-4-8 \
        --stage QA --from-team Interior_Creation --to-team QA
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "schemas",
                           "handoff_packet.schema.json")

ARTIFACT_TYPES = {".zip": "ZIP", ".pdf": "PDF", ".png": "PNG", ".tif": "TIFF",
                  ".tiff": "TIFF", ".csv": "CSV", ".json": "JSON"}


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_packet(artifact_path: str, args) -> dict:
    ext = os.path.splitext(artifact_path)[1].lower()
    return {
        "packet_version": args.packet_version,
        "task_id": args.task_id,
        "book_slug": args.book_slug,
        "stage": args.stage,
        "from_team": args.from_team,
        "to_team": args.to_team,
        "handoff_type": args.handoff_type,
        "artifact": {
            "name": os.path.basename(artifact_path),
            "type": ARTIFACT_TYPES.get(ext, "ZIP"),
            "size_bytes": os.path.getsize(artifact_path),
            "sha256": sha256(artifact_path),
        },
        "event_log": [{
            "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
            "team": args.from_team,
            "action": f"handoff:{args.stage}",
            "note": args.note or "",
        }],
    }


def validate(packet: dict) -> None:
    try:
        import jsonschema
    except ImportError:
        print("WARN jsonschema not installed; skipping schema validation",
              file=sys.stderr)
        return
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)
    jsonschema.validate(packet, schema)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Write a validated handoff packet")
    ap.add_argument("artifact")
    ap.add_argument("out_json")
    ap.add_argument("--task-id", required=True)
    ap.add_argument("--book-slug", required=True)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--from-team", required=True)
    ap.add_argument("--to-team", required=True)
    ap.add_argument("--handoff-type", default="NORMAL",
                    choices=["NORMAL", "RETRY", "ESCALATION"])
    ap.add_argument("--packet-version", default="1.0")
    ap.add_argument("--note", default="")
    args = ap.parse_args(argv)

    if not os.path.isfile(args.artifact):
        print(f"ERROR: artifact not found: {args.artifact}", file=sys.stderr)
        return 2

    packet = build_packet(args.artifact, args)
    validate(packet)
    with open(args.out_json, "w") as f:
        json.dump(packet, f, indent=2)
    print(f"Wrote {args.out_json} (sha256 {packet['artifact']['sha256'][:12]}...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
