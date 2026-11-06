# Final QA report — 2026-11-06

## Status summary

| Area | Status | Executed evidence |
|---|---|---|
| Core unit and dashboard-data tests | PASS | `pytest -q`: **10 passed, 2 skipped**. The skipped tests require an explicitly enabled disposable PostgreSQL database. |
| PostgreSQL integration tests | PASS | 2 passed using a newly created disposable `commercelens_audit_qa` database; it was dropped afterwards and the working database remained at 99,441 fact orders. |
| SQL validation | PASS | 20/20 query files executed independently against local PostgreSQL. See [SQL validation report](SQL_VALIDATION_REPORT.md). |
| Dashboard rendering and controls | PASS | Streamlit AppTest rendered all seven pages; date/state/status filters, category/product drill-down, and RFM segment selection were exercised. Browser screenshots for all seven pages were captured with no console errors. |
| Metric reconciliation | PASS | PostgreSQL and Python agree on delivered GMV, orders, AOV, and unique customers. |
| Report generation | PASS | `python -m src.cli report --period monthly` generated PDF plus sales, product, customer, cohort, operations, and data-quality CSVs. |
| Docker and Compose | PASS | `docker compose config --quiet` and a Docker image build succeeded; Postgres was healthy on host port 5433. |
| Security preflight | PASS | `.env`, raw CSVs, and generated reports are ignored; no tracked credentials were found in the repository scan. |
| Cloud deployment | NOT VERIFIED | Requires managed database credentials, hosting login, and explicit deployment approval. |
| Remote GitHub Actions run | NOT VERIFIED | Workflow is configured, but this local QA pass cannot claim a hosted run completed. |

## Current database verification

- Docker PostgreSQL 16 is healthy at `localhost:5433`; native host PostgreSQL on 5432 was not changed.
- Database size: **226 MB**.
- Analytical tables: 99,441 orders; 112,650 order items; 103,886 payments; 99,224 reviews; 774 date rows.
- Migration recorded: `001_analytics_hardening.sql`.

## Metric reconciliation

| Metric | PostgreSQL / Python result |
|---|---:|
| Delivered merchandise GMV | R$13,221,498.11 |
| Delivered orders | 96,478 |
| AOV | R$137.04 |
| Unique customers | 93,358 |

GMV is delivered item price, not payment value or profit. Item facts are pre-aggregated to order grain for order-level KPIs, and product drill-down uses the separate item-grain mart.

## Fixes verified in this pass

- Added an item-grain dashboard mart/export and PostgreSQL fallback for accurate category/product drill-downs.
- Added shared date, state, and order-status filters plus reset behavior.
- Made RFM segment KPIs and recommendations respond to the selected data.
- Fixed cohort heatmap serialization for live recomputation.
- Added operational KPIs and seller performance results.
- Added cohort-retention and data-quality CSV report artifacts; expanded PDF report content.
- Preserved the high-contrast dashboard styling and confirmed it in the live local dashboard.

## Remaining external work

1. Push the reviewed local commits only after user approval.
2. Observe a GitHub Actions run after that push.
3. Provision a managed PostgreSQL database, create separate ETL writer and dashboard reader roles, and load the actual local Olist data with the direct ETL URL.
4. Configure Streamlit Community Cloud secrets, deploy `app.py`, and execute the public smoke-test checklist.

No public deployment is claimed by this report.
