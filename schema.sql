-- ============================================================
--  nova-data-engine — database schema
--  A capture log: pieces of information ("captures") are ingested
--  from different sources, cleaned, and stored for querying.
--  This mirrors the SQLite data layer I built inside NOVA.
-- ============================================================

PRAGMA journal_mode = WAL;   -- allow reads while a write is in progress
PRAGMA foreign_keys = ON;    -- enforce the source relationship

-- Where a capture came from (e.g. "notes", "web", "bot")
CREATE TABLE IF NOT EXISTS source (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT NOT NULL UNIQUE
);

-- One row per captured item
CREATE TABLE IF NOT EXISTS capture (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    source_id   INTEGER NOT NULL,
    kind        TEXT    NOT NULL CHECK (kind IN ('note','link','task','idea')),
    title       TEXT    NOT NULL,
    word_count  INTEGER NOT NULL DEFAULT 0 CHECK (word_count >= 0),
    FOREIGN KEY (source_id) REFERENCES source(id)
);

-- Indexes for the columns the reports group and filter on
CREATE INDEX IF NOT EXISTS idx_capture_source ON capture(source_id);
CREATE INDEX IF NOT EXISTS idx_capture_kind   ON capture(kind);
CREATE INDEX IF NOT EXISTS idx_capture_date   ON capture(created_at);
