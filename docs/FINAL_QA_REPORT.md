# Final QA report — 2026-11-06

## SQL validation results — PASS

All 20 SQL files executed against local PostgreSQL. Seven reserved `month` aliases were corrected and every query then completed successfully. See [SQL validation report](SQL_VALIDATION_REPORT.md).

## Dashboard verification — PASS (screenshots NOT VERIFIED)

The Executive Overview and Experiment Analytics pages were browser-tested with actual Olist results; navigation controls and browser-console error/warning checks were clean. A Streamlit AppTest then exercised all seven pages with actual exports, and every page rendered without exceptions. A Sales & Product Analytics failure was reproduced from the supplied screenshot and corrected: daily GMV now uses a named aggregate rather than assigning two labels to a one-column Series. The date/state controls are shared before dependent calculations. Full screenshot capture for all seven pages is **NOT VERIFIED** in this QA pass.

## ETL idempotency — PASS

The working database was preserved. A disposable Docker database received two complete runs of the actual Olist ETL. Both runs produced 99,441 orders, 112,650 items, 103,886 payments, 99,441 distinct order IDs, and R$13,221,498.11 delivered GMV. The test database was dropped afterwards. The production ETL has a non-blocking exclusive file lock, and lock behavior has unit coverage.

## PostgreSQL integration tests — PASS

Created a disposable `commercelens_qa` Docker database, executed migration/schema tests, and removed it afterwards. Results: 2 passed. The working database still has 99,441 fact-order rows. GitHub Actions now provisions an isolated PostgreSQL 16 service and enables these tests.

## Metric reconciliation — PASS

PostgreSQL and Python agree on delivered merchandise GMV (R$13,221,498.11), delivered orders (96,478), AOV (R$137.04 after rounding), and unique customers (93,358).

## Security and Docker — PASS

`.env` and raw data remain untracked; `.dockerignore` excludes local data/secrets; Docker Compose is valid; the PostgreSQL container is healthy on host port 5433; the image builds successfully; and the image runs as a non-root user. No credentials were reported by QA output.

## Deployment preflight — PARTIALLY VERIFIED

Configuration supports `DATABASE_URL` from operating-system variables or `st.secrets`, supports `DATABASE_SSLMODE`, connection pre-ping/pooling, and a configurable container `PORT`. The dashboard was also run without local export files and correctly loaded 99,441 orders from local PostgreSQL. Streamlit Community Cloud + Neon remains deployment-ready, but cloud credentials, remote ETL, and public smoke testing are **NOT VERIFIED**.

## Git readiness — NOT VERIFIED

Do not push until the current working tree is reviewed and all QA-report/documentation changes are committed. No force-push or history rewrite was performed.

## Remaining issues

- Capture and commit clean screenshots for all seven dashboard pages.
- Run a full two-pass actual-data ETL idempotency test in a dedicated isolated database.
- Provision Neon, load real data using a direct ETL connection, configure a least-privilege runtime role, deploy Streamlit, and perform public smoke testing.
