# nova-data-engine

A small, self-contained **data pipeline and SQLite data layer** in Python.
It ingests raw "captures" (notes, links, tasks, ideas) from a file, validates
and cleans them, loads the good ones into a database, and answers reporting
questions over them.

This is a cleaned-up, standalone showcase of the data layer I built inside
**NOVA**, a personal AI assistant I develop in Python and Flask. NOVA itself is
private; this repo isolates the data-engineering part — the SQLite storage and
the ETL flow — so it can be shared and run on its own, with no personal data.

## What it demonstrates

- **A data pipeline (ETL):** `extract` raw JSONL → `transform` (validate + clean)
  → `load` into SQLite, in [`src/pipeline.py`](src/pipeline.py)
- **Writing SQL:** schema with keys, a `CHECK` constraint and indexes in
  [`schema.sql`](schema.sql); `JOIN` / `GROUP BY` / aggregate reports in
  [`src/query.py`](src/query.py)
- **Safe data handling:** every write uses **parameterised queries** (`?`
  placeholders) to protect data integrity and prevent SQL injection
  ([`src/capture.py`](src/capture.py))
- **Data quality:** invalid records (missing title, unknown kind) are rejected
  and reported rather than silently dropped
- **Reliability:** SQLite opened in **WAL mode** with foreign keys enforced
  ([`src/db.py`](src/db.py))

## Project layout

```
schema.sql            table definitions, constraints, indexes
src/db.py             connection + schema setup (WAL, foreign keys)
src/capture.py        parameterised inserts
src/pipeline.py       extract / transform / load
src/query.py          reporting queries
demo.py               runs the whole thing end to end
sample_data/items.jsonl   example input (includes 2 deliberately bad rows)
```

## Run it

No dependencies — uses only the Python standard library (`sqlite3`).

```bash
python demo.py
```

Expected: the pipeline reads 10 lines, loads 6, and **rejects 4** (one with no
title, one with an unsupported kind, one that isn't valid JSON, one that isn't
a JSON object), then prints captures by source, captures by kind (with average
length), and the longest captures.

## Tests

```bash
python -m pytest
```

Covers the `transform` validation rules, `extract`'s handling of malformed
JSONL lines, and a full end-to-end pipeline run against a temporary database.

## What I'd add next

- Load straight from an API instead of a file
- A scheduled nightly backup of the database
- Batch inserts in a single transaction for larger feeds
