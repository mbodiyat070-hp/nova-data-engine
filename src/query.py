"""
query.py — reporting queries over the capture database.

Read-only SELECTs using JOIN, GROUP BY, aggregates and a parameterised
filter. These are the "questions" the data answers.
"""

import sqlite3


def totals_by_source(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """How many captures came from each source."""
    return conn.execute(
        "SELECT s.name AS source, COUNT(*) AS captures "
        "FROM capture c JOIN source s ON s.id = c.source_id "
        "GROUP BY s.name ORDER BY captures DESC"
    ).fetchall()


def totals_by_kind(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Count and average length per kind of capture."""
    return conn.execute(
        "SELECT kind, COUNT(*) AS captures, "
        "       ROUND(AVG(word_count), 1) AS avg_words "
        "FROM capture GROUP BY kind ORDER BY captures DESC"
    ).fetchall()


def longest(conn: sqlite3.Connection, limit: int = 3) -> list[sqlite3.Row]:
    """The longest captures by word count (limit is parameterised)."""
    return conn.execute(
        "SELECT title, word_count FROM capture "
        "ORDER BY word_count DESC LIMIT ?",
        (limit,),
    ).fetchall()
