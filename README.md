# CommerceLens

CommerceLens is an end-to-end e-commerce analytics project built with the public Brazilian E-Commerce dataset by Olist. It transforms source CSVs into validated analytical data, then presents business performance through an interactive dashboard, SQL analyses, and downloadable reports.

This is an independent portfolio project. It is not affiliated with Tata CLiQ.

## What it does

- **Automated data pipeline:** profiles and cleans source data, validates key relationships and business rules, records a cleaning audit, and exports reusable analytical datasets. PostgreSQL loading is optional.
- **Interactive dashboard:** seven sections cover executive KPIs, sales and products, customer intelligence, operations and delivery, geography, experiment analytics, and data quality. Shared date, state, and order-status filters support exploration.
- **Customer analytics:** builds RFM segments and cohort-retention summaries, with rule-based actions based on observed data.
- **Business analysis:** includes 20 runnable PostgreSQL queries and database views for common sales, customer, product, and delivery questions.
- **Reports and BI:** generates CSV/PDF reports and includes guidance and measures for connecting Power BI to PostgreSQL.
- **Experiment demonstration:** analyzes a seeded synthetic A/B test. The dashboard labels it as simulated; these results are not Olist business findings.

## Technology

| Area | Technologies |
|---|---|
| Language and data processing | Python, pandas, NumPy |
| Database and access | PostgreSQL, SQLAlchemy, psycopg |
| Dashboard and visualization | Streamlit, Plotly |
| Statistical analysis | SciPy |
| Reporting | CSV, ReportLab PDF |
| Runtime and testing | Docker, Docker Compose, pytest |

## Data flow

```text
Olist CSVs -> ingestion and profiling -> cleaning and validation
           -> processed data and order-level analytics
           -> PostgreSQL -> dashboard, SQL, reports, and Power BI
```

Raw input files are kept separate from cleaned and exported data. The pipeline can run without a database to prepare the CSV outputs, or load the analytics schema into PostgreSQL with `--database`. The database model keeps orders, order items, payments, and reviews at their appropriate fact grains.

### Metric definitions and safeguards

- Completed merchandise GMV is the sum of item prices for delivered orders. It excludes freight and is **not profit**.
- Average order value is delivered merchandise GMV divided by delivered orders.
- Repeat purchase rate is customers with at least two delivered orders divided by customers with at least one delivered order.
- Payment and order-item facts are not joined directly for revenue; combining those detail grains would multiply values for some orders.

See the [KPI dictionary](docs/KPI_DICTIONARY.md) and [database design](docs/DATABASE.md) for definitions and modeling details.

## Getting started

### Requirements

- Python 3.11 or newer
- Docker Desktop / Docker Engine if using the included PostgreSQL service
- The nine CSV files from the [Olist Brazilian E-Commerce dataset on Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

### Install and prepare data

```bash
git clone https://github.com/SiddharthaShukla8/CommerceLens-Project.git
cd CommerceLens-Project

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Place the nine unmodified Olist CSV files in `data/raw/`. The expected filenames are listed in [`config/settings.py`](config/settings.py). Raw data and `.env` are excluded from Git; do not commit credentials or source data.

### Validate, load, and launch

```bash
# Check source files and data quality
python -m src.cli validate

# Start the local PostgreSQL service (host port 5433)
docker compose up -d

# Run the pipeline, load PostgreSQL, and create analytical exports
python -m src.cli run-all --database

# Launch the dashboard
streamlit run app.py
```

The dashboard can use generated exports or a configured PostgreSQL analytics schema. If neither is available, it displays setup instructions rather than fabricating business results. See the [dataset setup guide](docs/DATASET_SETUP.md) for input details and the [deployment guide](docs/DEPLOYMENT_GUIDE.md) for hosted deployment options. The project is deployment-ready but is not currently deployed.

## Other commands

```bash
python -m src.cli run-all                 # Process data and generate exports without loading PostgreSQL
python -m src.cli report --period monthly # Generate the monthly CSV and PDF report
pytest -q                                 # Run the test suite
```

Convenience targets are available through `make install`, `make validate`, `make pipeline`, `make dashboard`, `make test`, and `make report`.

## Project layout

```text
src/          Pipeline, ingestion, cleaning, validation, analytics, and reporting
dashboard/    Dashboard data access and reusable UI components
database/     PostgreSQL schema, views, indexes, and migrations
sql/          20 standalone business-analysis queries
data/         Raw inputs, processed data, and generated exports
powerbi/      Power BI connection guidance and DAX measures
tests/        Automated pipeline, analytics, data-quality, and integration tests
docs/         Architecture, metric definitions, setup, and deployment documentation
```

## Further documentation

- [Architecture](docs/ARCHITECTURE.md)
- [ETL and data quality](docs/ETL.md)
- [Database design](docs/DATABASE.md)
- [KPI dictionary](docs/KPI_DICTIONARY.md)
- [Dataset setup](docs/DATASET_SETUP.md)
- [Deployment guide](docs/DEPLOYMENT_GUIDE.md)
- [SQL query catalog](sql/README.md)
