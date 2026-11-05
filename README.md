# CommerceLens

CommerceLens is an end-to-end e-commerce intelligence platform built with Python, PostgreSQL, Streamlit, and Plotly. It uses the public Brazilian Olist e-commerce dataset and is an independent portfolio project, not a Tata CLiQ product or dataset.

## What it includes

- Repeatable CSV-to-PostgreSQL ETL pipeline with data-quality checks
- Business-ready order mart, RFM segments, customer cohorts, and rule-based insights
- 20 executable PostgreSQL analyses, a seven-section Streamlit dashboard, and CSV/PDF reports
- A reproducible, clearly-labelled synthetic A/B-test demonstration
- Power BI connection notes and DAX measures

## Quick start

1. Create and activate a Python 3.11+ virtual environment: `python3 -m venv .venv && source .venv/bin/activate`.
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`.
4. Download the nine Olist CSV files from [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) and place them in `data/raw/` without renaming them.
5. Start Docker Desktop, then run `docker compose up -d`.
6. `python -m src.cli run-all --database`
7. `streamlit run app.py`

Run `python -m src.cli validate` to profile and validate the source data before loading it. The dashboard deliberately displays a setup message when processed data is absent; it never substitutes made-up business data.

## Data model and metric safety

`fact_order_items` is the GMV grain; payment records are never joined to items for revenue. Completed merchandise GMV means delivered item price, not profit. Repeat rate is customers with two or more delivered orders divided by customers with at least one delivered order. See `docs/KPI_DICTIONARY.md` for details.

## Verification

Use `.venv/bin/pytest -q` after installation. The supplied tests validate KPI grain safety, RFM calculation, reproducible experiment analysis, and cleaning/quality behavior. `docs/ARCHITECTURE.md` documents the data flow and database fact grains.

## Commands

`make install`, `make validate`, `make pipeline`, `make test`, `make dashboard`, and `make report` are convenience aliases for the documented commands.

## Project structure

`src/` contains pipeline and analytics code; `database/` contains the PostgreSQL model; `sql/` has independently runnable analysis queries; `dashboard/` has dashboard utilities; `powerbi/` contains import guidance; `tests/` provides automated verification.
