"""
db.py — database connection and schema setup.

Central place that opens SQLite the same way everywhere: with write-ahead
logging (so reads don't block writes), foreign keys enforced, and rows
returned as dict-like objects. This is the pattern I used in NOVA.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "nova.db"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.sql"


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Open a connection with the settings the whole app relies on."""
    conn = sqlite3.connect(db_path, timeout=5)
    conn.row_factory = sqlite3.Row          # access columns by name
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Create the tables and indexes from schema.sql if they don't exist."""
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()
