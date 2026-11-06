"""Dashboard data access with an export-first, PostgreSQL fallback strategy."""
from __future__ import annotations

import pandas as pd
from sqlalchemy import create_engine, text
from config.settings import DATABASE_CONNECT_TIMEOUT, DATABASE_SSLMODE, DATABASE_URL, EXPORT_DIR
from src.analytics.cohort import build_cohorts
from src.analytics.rfm import build_rfm

MART_SQL = """
WITH item_category AS (
  SELECT i.order_id, p.product_category_name_english AS category, SUM(i.price) AS category_gmv,
         ROW_NUMBER() OVER (PARTITION BY i.order_id ORDER BY SUM(i.price) DESC, p.product_category_name_english) AS category_rank
  FROM analytics.fact_order_items i
  LEFT JOIN analytics.dim_products p USING (product_id)
  GROUP BY 1,2
), item_agg AS (
  SELECT order_id, SUM(price) AS merchandise_gmv, SUM(freight_value) AS freight_value, COUNT(*) AS units
  FROM analytics.fact_order_items GROUP BY 1
)
SELECT o.*, c.customer_unique_id, c.customer_state, a.merchandise_gmv, a.freight_value,
       a.merchandise_gmv + a.freight_value AS order_value, COALESCE(ic.category, 'unknown') AS category,
       a.units,
       EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400.0 AS delivery_days,
       CASE WHEN o.order_delivered_customer_date IS NOT NULL AND o.order_estimated_delivery_date IS NOT NULL
            THEN o.order_delivered_customer_date <= o.order_estimated_delivery_date END AS on_time
FROM analytics.fact_orders o
JOIN analytics.dim_customers c USING (customer_id)
LEFT JOIN item_agg a USING (order_id)
LEFT JOIN item_category ic ON ic.order_id = o.order_id AND ic.category_rank = 1
"""

ITEM_MART_SQL = """
SELECT i.order_id, i.order_item_id, i.product_id, i.seller_id, i.price,
       i.freight_value, COALESCE(p.product_category_name_english, 'unknown') AS category,
       o.order_status, o.order_purchase_timestamp, o.order_delivered_customer_date,
       o.order_estimated_delivery_date, c.customer_unique_id, c.customer_state
FROM analytics.fact_order_items i
JOIN analytics.fact_orders o USING (order_id)
JOIN analytics.dim_customers c USING (customer_id)
LEFT JOIN analytics.dim_products p USING (product_id)
"""

def _engine():
    args = {"connect_timeout": DATABASE_CONNECT_TIMEOUT}
    if DATABASE_SSLMODE:
        args["sslmode"] = DATABASE_SSLMODE
    return create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=args)


def filter_order_mart(
    mart: pd.DataFrame,
    date_range: tuple | list,
    states: list[str],
    statuses: list[str],
) -> pd.DataFrame:
    """Apply the dashboard's shared filters at the order grain."""
    selected = mart.copy()
    if len(date_range) == 2:
        selected = selected[selected.order_purchase_timestamp.dt.date.between(*date_range)]
    if states:
        selected = selected[selected.customer_state.isin(states)]
    if statuses:
        selected = selected[selected.order_status.isin(statuses)]
    return selected

def load_dashboard_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame] | None:
    files = [EXPORT_DIR / name for name in ("order_mart.csv", "item_mart.csv", "rfm_segments.csv", "cohort_retention.csv", "data_quality.csv")]
    if all(path.exists() for path in files):
        return (
            pd.read_csv(files[0], parse_dates=["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"]),
            pd.read_csv(files[1], parse_dates=["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"]),
            pd.read_csv(files[2]),
            pd.read_csv(files[3]),
            pd.read_csv(files[4]),
        )
    try:
        engine = _engine()
        with engine.connect() as connection:
            mart = pd.read_sql(text(MART_SQL), connection, parse_dates=["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"])
            item_mart = pd.read_sql(text(ITEM_MART_SQL), connection, parse_dates=["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"])
        engine.dispose()
    except Exception:
        return None
    if mart.empty:
        return None
    rfm, cohorts = build_rfm(mart), build_cohorts(mart)
    quality = pd.DataFrame([{"check": "dashboard database fallback", "status": "PASS", "value": len(mart), "detail": "Loaded order mart from PostgreSQL"}])
    return mart, item_mart, rfm, cohorts, quality
