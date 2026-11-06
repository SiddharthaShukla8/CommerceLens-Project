# Deployment guide

## Recommended architecture

Use **Streamlit Community Cloud** for this portfolio dashboard and **Neon PostgreSQL** for the managed database. Community Cloud is purpose-built for Streamlit, deploys from a GitHub repository, supports a selected Python version and secrets in Advanced settings. Neon provides a standard PostgreSQL connection string and requires TLS for public database connections. This project’s verified local database is modest, but check the live database size before selecting a Neon plan; provider limits and pricing can change.

**Alternative:** use the included Dockerfile on Render with Neon. Render supports Dockerfile deployments and requires a web service to bind `0.0.0.0` on its `PORT`; the Dockerfile does exactly that.

This recommendation was checked against the official Streamlit, Neon, and Render documentation on 2026-11-06. Streamlit Community Cloud secrets are consumed through `st.secrets`, which is why `config/settings.py` checks both environment variables and `st.secrets`. Select the Python version in Streamlit's Advanced settings before deployment: Community Cloud does not let an existing deployment change Python version in place. The project runs locally on Python 3.13; confirm the selected hosted version satisfies all pinned dependency ranges before clicking Deploy.

## One-time production data load

1. Provision a Neon PostgreSQL project close to the web host and create separate least-privilege reader and ETL writer accounts.
2. Save the writer URL only in your local shell or untracked `.env`. It must include TLS (for example, a Neon supplied `sslmode=require` URL). Use the direct connection supplied by the provider for migrations/ETL when required; retain a pooled URL for the dashboard if the provider supplies one.
3. From the local machine that contains the Olist CSVs, export the direct URL for this one command, then run `python -m src.cli run-all --database`.
4. Verify counts with `SELECT COUNT(*) FROM analytics.fact_orders;` and confirm `analytics.schema_migrations` is populated.
5. Add the reader `DATABASE_URL`, `DATABASE_SSLMODE=require`, and `DATABASE_CONNECT_TIMEOUT=10` to the Streamlit Cloud secret settings. Never upload raw CSVs or `.env`.

## Web deployment and smoke test

In Streamlit Community Cloud select this repository, `main`, and `app.py`; select the supported Python version in Advanced settings and paste the reader settings as secrets:

```toml
DATABASE_URL = "postgresql+psycopg://READER:REDACTED@HOST/DATABASE?sslmode=require"
DATABASE_SSLMODE = "require"
DATABASE_CONNECT_TIMEOUT = "10"
```

Confirm the dashboard loads, the executive KPIs appear, each navigation section opens, the experiment warning is visible, and no secret is displayed. The app is deployment-ready but **not deployed**: account access and production credentials are still required.

For Render, create a Docker web service from the repository, leave the Dockerfile command in use, and configure the same reader environment variables. Do not enable automatic deployment until you have reviewed the production database connection and smoke-tested a manual deploy.

## Rollback and troubleshooting

Keep a PostgreSQL backup before rerunning production ETL. To rollback application code, redeploy the previous Git commit; database migrations are additive, so restore a verified backup rather than deleting the database volume. Database connection errors usually indicate an unavailable secret, incorrect TLS mode, insufficient database privileges, or an IP allow-list restriction.
