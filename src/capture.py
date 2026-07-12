"""
capture.py — write captures into the database.

Every insert uses a parameterised query (the ? placeholders) so values are
passed to SQLite as data, never glued into the SQL string. This protects data
integrity and prevents SQL injection — the same approach I used in NOVA.
"""

import sqlite3


def get_or_create_source(conn: sqlite3.Connection, name: str) -> int:
    """Return the id for a source name, inserting it if it's new."""
    row = conn.execute(
        "SELECT id FROM source WHERE name = ?", (name,)
    ).fetchone()
    if row is not None:
        return row["id"]
    cur = conn.execute("INSERT INTO source (name) VALUES (?)", (name,))
    conn.commit()
    return cur.lastrowid


def add_capture(conn: sqlite3.Connection, source: str, kind: str,
                title: str, word_count: int) -> int:
    """Insert one capture and return its new id."""
    source_id = get_or_create_source(conn, source)
    cur = conn.execute(
        "INSERT INTO capture (source_id, kind, title, word_count) "
        "VALUES (?, ?, ?, ?)",
        (source_id, kind, title, word_count),
    )
    conn.commit()
    return cur.lastrowid
