# SQL analytics module

Each numbered file is directly executable against the initialized PostgreSQL database. The collection covers joins, aggregations, CTEs, correlated analytical logic, `CASE`-style filtering, date functions, rankings, `LAG`, running totals, moving averages, and cohort windows. Run the ETL first with `python -m src.cli run-all --database`; then execute a file via `psql` or any PostgreSQL client. These queries deliberately keep payments separate from item GMV to avoid fact-grain multiplication.
