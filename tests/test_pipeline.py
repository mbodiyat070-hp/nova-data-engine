"""
Tests for the ETL pipeline: extract, transform and a full end-to-end run.

Run from the project root:  python -m pytest
"""

import sqlite3
from pathlib import Path

import pytest

from src import db, pipeline


# --- transform -------------------------------------------------------------

def test_transform_accepts_valid_record():
    clean, reason = pipeline.transform({
        "source": "Notes", "kind": "Note",
        "title": "  My title  ", "content": "one two three",
    })
    assert reason is None
    assert clean == {"source": "notes", "kind": "note",
                     "title": "My title", "word_count": 3}


def test_transform_rejects_missing_title():
    clean, reason = pipeline.transform({"source": "web", "kind": "link",
                                        "title": "   ", "content": "x"})
    assert clean is None
    assert reason == "missing title"


def test_transform_rejects_unknown_kind():
    clean, reason = pipeline.transform({"source": "web", "kind": "video",
                                        "title": "T", "content": "x"})
    assert clean is None
    assert "invalid kind" in reason


# --- extract ---------------------------------------------------------------

def test_extract_rejects_bad_lines_without_crashing(tmp_path: Path):
    feed = tmp_path / "feed.jsonl"
    feed.write_text(
        '{"source": "web", "kind": "note", "title": "Good", "content": "ok"}\n'
        '{"broken": \n'
        '"a bare string"\n'
        "\n",  # blank lines are simply skipped
        encoding="utf-8",
    )
    records, rejected = pipeline.extract(feed)
    assert len(records) == 1
    assert records[0]["title"] == "Good"
    reasons = [r["reason"] for r in rejected]
    assert any("invalid JSON" in r for r in reasons)
    assert any("not a JSON object" in r for r in reasons)


# --- full run --------------------------------------------------------------

@pytest.fixture
def conn(tmp_path: Path):
    connection = db.connect(tmp_path / "test.db")
    db.init_db(connection)
    yield connection
    connection.close()


def test_run_loads_good_records_and_reports_bad_ones(conn: sqlite3.Connection,
                                                     tmp_path: Path):
    feed = tmp_path / "feed.jsonl"
    feed.write_text(
        '{"source": "web", "kind": "note", "title": "First", "content": "a b"}\n'
        '{"source": "bot", "kind": "task", "title": "Second", "content": "c"}\n'
        '{"source": "bot", "kind": "task", "title": "", "content": "no title"}\n'
        "not json at all\n",
        encoding="utf-8",
    )
    summary = pipeline.run(conn, feed)

    assert summary["read"] == 4
    assert summary["loaded"] == 2
    assert len(summary["rejected"]) == 2

    rows = conn.execute("SELECT title FROM capture ORDER BY title").fetchall()
    assert [row["title"] for row in rows] == ["First", "Second"]
