"""
demo.py — run the whole thing end to end.

Builds a fresh database, runs the ETL pipeline over the sample data, then
prints reports. Run from the project root:

    python demo.py
"""

from pathlib import Path

from src import db, pipeline, query

SAMPLE = Path(__file__).parent / "sample_data" / "items.jsonl"


def show(title, rows):
    print(f"\n{title}")
    print("-" * len(title))
    for row in rows:
        print("  " + " | ".join(f"{k}: {row[k]}" for k in row.keys()))


def main() -> None:
    # Start from a clean database each run so the demo is reproducible.
    if db.DB_PATH.exists():
        db.DB_PATH.unlink()

    conn = db.connect()
    db.init_db(conn)

    summary = pipeline.run(conn, SAMPLE)
    print(f"Pipeline: read {summary['read']}, loaded {summary['loaded']}, "
          f"rejected {len(summary['rejected'])}")
    for bad in summary["rejected"]:
        print(f"  rejected ({bad['reason']}): {bad['record']}")

    show("Captures by source", query.totals_by_source(conn))
    show("Captures by kind", query.totals_by_kind(conn))
    show("Longest captures", query.longest(conn))

    conn.close()


if __name__ == "__main__":
    main()
