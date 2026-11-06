# CommerceLens gap analysis

Audit performed locally on 2026-11-06 against the running Docker PostgreSQL database and the current `main` worktree. Statuses describe executed verification, not source-file presence.

| Feature | Existing implementation | Actual verification | Identified gap | Required fix | Final status |
|---|---|---|---|---|---|
| Nine-source ingestion and cleaning | Pandas reader, cleaner, validation | Source files, ETL metadata, and historical source counts inspected | None found in this audit | Preserve existing workflow | PASS |
| PostgreSQL warehouse | Staging plus analytics facts/dimensions | Healthy Docker Postgres, 16 tables, 774 date rows, 226 MB database | None found | Preserve port 5433 mapping and volume | PASS |
| ETL repeatability | Transactional replace load, migration runner, exclusive lock | Prior two-pass disposable-database run and automated lock tests reviewed; latest 10 tests passed | Full raw-data run not repeated to avoid replacing working exports/database unnecessarily | Repeat only in a disposable DB when ETL code changes | PASS (historically verified) |
| KPI consistency | `src.analytics.mart.kpis` and order-grain view | Python and PostgreSQL reconciled: GMV R$13,221,498.11, 96,478 delivered orders, AOV R$137.04, 93,358 customers | None found | Retain order/item grain guardrails | PASS |
| SQL analysis | 20 PostgreSQL files | All 20 independently executed; row counts recorded in `SQL_VALIDATION_REPORT.md` | None found | Preserve independent execution in QA | PASS |
| Product drill-down | Category-only order mart visual | Product selection needed an item-grain source to avoid misattributing multi-item orders | Added `item_mart` export/database fallback and category/product controls | PASS |
| Shared dashboard filters | Date and state controls | Status filter and reset action were missing | Added date/state/status filters plus reset; AppTest exercised filter change | PASS |
| Customer dashboard | RFM/cohort displays | Selected segment did not update all dependent KPIs; live cohort labels could be non-serializable | Rebuilt selected RFM/cohort data, added segment KPIs/action, converted chart labels safely | PASS |
| Operations dashboard | Delivery charts and late-order table | Required operational KPIs and seller view were incomplete | Added dynamic order, cancellation, availability, delivery and seller sections | PASS |
| Reporting | PDF plus four CSV outputs | Monthly report command ran successfully | Cohort-retention and data-quality CSVs were missing | Added both actual exports and expanded report contents | PASS |
| Automated tests | Unit, lock, and optional PostgreSQL tests | 10 passed, 2 correctly skipped without disposable DB flag | Dashboard filter/item-mart coverage was missing | Added targeted tests | PASS |
| CI PostgreSQL service | GitHub Actions service configured | Workflow inspected; secrets are not required | Hosted CI run not observed from this local environment | Verify on next approved push | NOT VERIFIED (remote execution) |
| Cloud deployment | Streamlit/Neon-ready config/docs | Env + `st.secrets` resolver, SSL mode, pool pre-ping, Docker build reviewed | No cloud account credentials or public URL | User authentication and explicit deployment approval | BLOCKED |
| Security/privacy | `.gitignore`, `.dockerignore`, configuration resolver | `.env` and raw CSVs ignored; no tracked credentials found; dashboard tables omit direct customer PII | Runtime database-role separation needs managed database provisioning | Configure reader/ETL roles in managed PostgreSQL | PARTIALLY IMPLEMENTED |

## Completion ledger

- Preserved: the existing ETL, database model, SQL queries, metric definitions, RFM, cohorts, experiment module, Docker setup, and high-contrast design.
- Fixed: dashboard item-grain drill-down, filter reset/status filtering, selected-segment calculations, cohort heatmap serialization, operational coverage, and report artifact coverage.
- Still external: remote CI observation, managed PostgreSQL provisioning, data ingestion to the managed service, Streamlit deployment, and public smoke testing.
