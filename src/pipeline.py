"""
pipeline.py — a small ETL (extract, transform, load) pipeline.

Reads raw captures from a JSONL file, validates and cleans each record,
then loads the good ones into the database. Invalid records are collected
and reported rather than silently dropped — a basic data-quality step.

This is the core idea of data engineering: move data from one place to
another in a clean, reliable shape.
"""

import json
from pathlib import Path

from . import capture

VALID_KINDS = {"note", "link", "task", "idea"}


def extract(path: Path) -> list[dict]:
    """Read raw records from a JSONL file (one JSON object per line)."""
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def transform(record: dict) -> tuple[dict | None, str | None]:
    """Validate and clean one record.

    Returns (clean_record, None) if it's good, or (None, reason) if it
    fails a data-quality check.
    """
    title = (record.get("title") or "").strip()
    if not title:
        return None, "missing title"

    kind = (record.get("kind") or "").strip().lower()
    if kind not in VALID_KINDS:
        return None, f"invalid kind: {kind!r}"

    source = (record.get("source") or "unknown").strip().lower()
    content = (record.get("content") or "").strip()

    clean = {
        "source": source,
        "kind": kind,
        "title": title,
        "word_count": len(content.split()),   # derived field
    }
    return clean, None


def load(conn, records: list[dict]) -> int:
    """Insert clean records; returns how many were loaded."""
    for r in records:
        capture.add_capture(conn, r["source"], r["kind"],
                            r["title"], r["word_count"])
    return len(records)


def run(conn, path: Path) -> dict:
    """Run the full pipeline and return a small summary."""
    raw = extract(path)
    clean, rejected = [], []
    for record in raw:
        cleaned, reason = transform(record)
        if cleaned is not None:
            clean.append(cleaned)
        else:
            rejected.append({"record": record, "reason": reason})

    loaded = load(conn, clean)
    return {"read": len(raw), "loaded": loaded, "rejected": rejected}
