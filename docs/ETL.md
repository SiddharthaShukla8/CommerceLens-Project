# ETL and data-quality workflow

`python -m src.cli run-all --database` acquires an exclusive local run lock, validates every required source file, parses timestamps, cleans data without editing source CSVs, validates relationships, loads PostgreSQL transactionally, and only then publishes processed/analytical exports.

The run metadata records source and cleaned row counts, validation statuses, UTC start/end information, duration, and database-load status. A failed run writes a credential-free failure record and does not mark the run successful.

The verified 2026-11-06 run loaded 99,441 customers/orders, 112,650 order items, 103,886 payments, 99,224 reviews, 32,951 products, and 3,095 sellers. Geolocation was deduplicated from 1,000,163 source rows to 738,332 exact-distinct rows; it is retained as a processed source but is not needed by the dashboard's state-level aggregations.
