"""Dashboard data access with an export-first, PostgreSQL fallback strategy and deterministic test fixtures."""
from __future__ import annotations

import os
from pathlib import Path
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


def get_deterministic_test_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return a deterministic, lightweight analytics fixture for automated testing environments.
    
    Contains diverse purchase dates, multiple customer states (AM, SC, RJ, SP, PR, BA),
    multiple order statuses (delivered, shipped, canceled), multiple product categories,
    and distinct customers to test full dashboard behavior without requiring production DB or raw CSVs.
    """
    orders = [
        {
            "order_id": "ord-001", "customer_id": "cust-001", "order_status": "delivered",
            "order_purchase_timestamp": pd.Timestamp("2017-09-01 10:00:00"),
            "order_delivered_customer_date": pd.Timestamp("2017-09-05 14:00:00"),
            "order_estimated_delivery_date": pd.Timestamp("2017-09-12 00:00:00"),
            "customer_unique_id": "uniq-cust-001", "customer_state": "AM",
            "merchandise_gmv": 150.0, "freight_value": 20.0, "order_value": 170.0,
            "category": "health_beauty", "units": 1, "delivery_days": 4.16, "on_time": True,
        },
        {
            "order_id": "ord-002", "customer_id": "cust-002", "order_status": "delivered",
            "order_purchase_timestamp": pd.Timestamp("2017-09-02 12:30:00"),
            "order_delivered_customer_date": pd.Timestamp("2017-09-15 11:00:00"),
            "order_estimated_delivery_date": pd.Timestamp("2017-09-10 00:00:00"),
            "customer_unique_id": "uniq-cust-002", "customer_state": "SC",
            "merchandise_gmv": 320.0, "freight_value": 35.0, "order_value": 355.0,
            "category": "computers", "units": 2, "delivery_days": 12.93, "on_time": False,
        },
        {
            "order_id": "ord-003", "customer_id": "cust-003", "order_status": "shipped",
            "order_purchase_timestamp": pd.Timestamp("2017-09-03 15:45:00"),
            "order_delivered_customer_date": pd.NaT,
            "order_estimated_delivery_date": pd.Timestamp("2017-09-20 00:00:00"),
            "customer_unique_id": "uniq-cust-003", "customer_state": "AM",
            "merchandise_gmv": 85.0, "freight_value": 15.0, "order_value": 100.0,
            "category": "health_beauty", "units": 1, "delivery_days": None, "on_time": None,
        },
        {
            "order_id": "ord-004", "customer_id": "cust-004", "order_status": "canceled",
            "order_purchase_timestamp": pd.Timestamp("2017-09-04 09:15:00"),
            "order_delivered_customer_date": pd.NaT,
            "order_estimated_delivery_date": pd.Timestamp("2017-09-25 00:00:00"),
            "customer_unique_id": "uniq-cust-004", "customer_state": "RJ",
            "merchandise_gmv": 60.0, "freight_value": 12.0, "order_value": 72.0,
            "category": "furniture_decor", "units": 1, "delivery_days": None, "on_time": None,
        },
        {
            "order_id": "ord-005", "customer_id": "cust-005", "order_status": "delivered",
            "order_purchase_timestamp": pd.Timestamp("2017-09-04 18:20:00"),
            "order_delivered_customer_date": pd.Timestamp("2017-09-09 16:00:00"),
            "order_estimated_delivery_date": pd.Timestamp("2017-09-15 00:00:00"),
            "customer_unique_id": "uniq-cust-005", "customer_state": "SP",
            "merchandise_gmv": 190.0, "freight_value": 18.0, "order_value": 208.0,
            "category": "watches_gifts", "units": 1, "delivery_days": 4.90, "on_time": True,
        },
        {
            "order_id": "ord-006", "customer_id": "cust-006", "order_status": "delivered",
            "order_purchase_timestamp": pd.Timestamp("2017-10-10 11:00:00"),
            "order_delivered_customer_date": pd.Timestamp("2017-10-18 14:00:00"),
            "order_estimated_delivery_date": pd.Timestamp("2017-10-22 00:00:00"),
            "customer_unique_id": "uniq-cust-001", "customer_state": "AM",
            "merchandise_gmv": 110.0, "freight_value": 20.0, "order_value": 130.0,
            "category": "health_beauty", "units": 1, "delivery_days": 8.12, "on_time": True,
        },
        {
            "order_id": "ord-007", "customer_id": "cust-007", "order_status": "delivered",
            "order_purchase_timestamp": pd.Timestamp("2017-10-15 14:30:00"),
            "order_delivered_customer_date": pd.Timestamp("2017-10-22 17:00:00"),
            "order_estimated_delivery_date": pd.Timestamp("2017-10-28 00:00:00"),
            "customer_unique_id": "uniq-cust-007", "customer_state": "PR",
            "merchandise_gmv": 210.0, "freight_value": 25.0, "order_value": 235.0,
            "category": "computers", "units": 1, "delivery_days": 7.10, "on_time": True,
        },
        {
            "order_id": "ord-008", "customer_id": "cust-008", "order_status": "delivered",
            "order_purchase_timestamp": pd.Timestamp("2017-11-05 16:00:00"),
            "order_delivered_customer_date": pd.Timestamp("2017-11-12 12:00:00"),
            "order_estimated_delivery_date": pd.Timestamp("2017-11-18 00:00:00"),
            "customer_unique_id": "uniq-cust-008", "customer_state": "BA",
            "merchandise_gmv": 95.0, "freight_value": 15.0, "order_value": 110.0,
            "category": "furniture_decor", "units": 1, "delivery_days": 6.83, "on_time": True,
        },
    ]
    mart = pd.DataFrame(orders)

    items = [
        {
            "order_id": "ord-001", "order_item_id": 1, "product_id": "prod-health-001", "seller_id": "seller-001",
            "shipping_limit_date": pd.Timestamp("2017-09-06 10:00:00"), "price": 150.0, "freight_value": 20.0,
            "category": "health_beauty", "order_status": "delivered",
            "order_purchase_timestamp": pd.Timestamp("2017-09-01 10:00:00"),
            "order_delivered_customer_date": pd.Timestamp("2017-09-05 14:00:00"),
            "order_estimated_delivery_date": pd.Timestamp("2017-09-12 00:00:00"),
            "customer_unique_id": "uniq-cust-001", "customer_state": "AM",
        },
        {
            "order_id": "ord-002", "order_item_id": 1, "product_id": "prod-comp-001", "seller_id": "seller-002",
            "shipping_limit_date": pd.Timestamp("2017-09-07 12:30:00"), "price": 200.0, "freight_value": 20.0,
            "category": "computers", "order_status": "delivered",
            "order_purchase_timestamp": pd.Timestamp("2017-09-02 12:30:00"),
            "order_delivered_customer_date": pd.Timestamp("2017-09-15 11:00:00"),
            "order_estimated_delivery_date": pd.Timestamp("2017-09-10 00:00:00"),
            "customer_unique_id": "uniq-cust-002", "customer_state": "SC",
        },
        {
            "order_id": "ord-002", "order_item_id": 2, "product_id": "prod-comp-002", "seller_id": "seller-002",
            "shipping_limit_date": pd.Timestamp("2017-09-07 12:30:00"), "price": 120.0, "freight_value": 15.0,
            "category": "computers", "order_status": "delivered",
            "order_purchase_timestamp": pd.Timestamp("2017-09-02 12:30:00"),
            "order_delivered_customer_date": pd.Timestamp("2017-09-15 11:00:00"),
            "order_estimated_delivery_date": pd.Timestamp("2017-09-10 00:00:00"),
            "customer_unique_id": "uniq-cust-002", "customer_state": "SC",
        },
        {
            "order_id": "ord-003", "order_item_id": 1, "product_id": "prod-health-002", "seller_id": "seller-001",
            "shipping_limit_date": pd.Timestamp("2017-09-08 15:45:00"), "price": 85.0, "freight_value": 15.0,
            "category": "health_beauty", "order_status": "shipped",
            "order_purchase_timestamp": pd.Timestamp("2017-09-03 15:45:00"),
            "order_delivered_customer_date": pd.NaT,
            "order_estimated_delivery_date": pd.Timestamp("2017-09-20 00:00:00"),
            "customer_unique_id": "uniq-cust-003", "customer_state": "AM",
        },
        {
            "order_id": "ord-004", "order_item_id": 1, "product_id": "prod-furn-001", "seller_id": "seller-003",
            "shipping_limit_date": pd.Timestamp("2017-09-09 09:15:00"), "price": 60.0, "freight_value": 12.0,
            "category": "furniture_decor", "order_status": "canceled",
            "order_purchase_timestamp": pd.Timestamp("2017-09-04 09:15:00"),
            "order_delivered_customer_date": pd.NaT,
            "order_estimated_delivery_date": pd.Timestamp("2017-09-25 00:00:00"),
            "customer_unique_id": "uniq-cust-004", "customer_state": "RJ",
        },
        {
            "order_id": "ord-005", "order_item_id": 1, "product_id": "prod-watch-001", "seller_id": "seller-004",
            "shipping_limit_date": pd.Timestamp("2017-09-09 18:20:00"), "price": 190.0, "freight_value": 18.0,
            "category": "watches_gifts", "order_status": "delivered",
            "order_purchase_timestamp": pd.Timestamp("2017-09-04 18:20:00"),
            "order_delivered_customer_date": pd.Timestamp("2017-09-09 16:00:00"),
            "order_estimated_delivery_date": pd.Timestamp("2017-09-15 00:00:00"),
            "customer_unique_id": "uniq-cust-005", "customer_state": "SP",
        },
        {
            "order_id": "ord-006", "order_item_id": 1, "product_id": "prod-health-001", "seller_id": "seller-001",
            "shipping_limit_date": pd.Timestamp("2017-10-15 11:00:00"), "price": 110.0, "freight_value": 20.0,
            "category": "health_beauty", "order_status": "delivered",
            "order_purchase_timestamp": pd.Timestamp("2017-10-10 11:00:00"),
            "order_delivered_customer_date": pd.Timestamp("2017-10-18 14:00:00"),
            "order_estimated_delivery_date": pd.Timestamp("2017-10-22 00:00:00"),
            "customer_unique_id": "uniq-cust-001", "customer_state": "AM",
        },
        {
            "order_id": "ord-007", "order_item_id": 1, "product_id": "prod-comp-001", "seller_id": "seller-002",
            "shipping_limit_date": pd.Timestamp("2017-10-20 14:30:00"), "price": 210.0, "freight_value": 25.0,
            "category": "computers", "order_status": "delivered",
            "order_purchase_timestamp": pd.Timestamp("2017-10-15 14:30:00"),
            "order_delivered_customer_date": pd.Timestamp("2017-10-22 17:00:00"),
            "order_estimated_delivery_date": pd.Timestamp("2017-10-28 00:00:00"),
            "customer_unique_id": "uniq-cust-007", "customer_state": "PR",
        },
        {
            "order_id": "ord-008", "order_item_id": 1, "product_id": "prod-furn-002", "seller_id": "seller-003",
            "shipping_limit_date": pd.Timestamp("2017-11-10 16:00:00"), "price": 95.0, "freight_value": 15.0,
            "category": "furniture_decor", "order_status": "delivered",
            "order_purchase_timestamp": pd.Timestamp("2017-11-05 16:00:00"),
            "order_delivered_customer_date": pd.Timestamp("2017-11-12 12:00:00"),
            "order_estimated_delivery_date": pd.Timestamp("2017-11-18 00:00:00"),
            "customer_unique_id": "uniq-cust-008", "customer_state": "BA",
        },
    ]
    item_mart = pd.DataFrame(items)
    rfm, cohorts = build_rfm(mart), build_cohorts(mart)
    quality = pd.DataFrame([
        {"check": "deterministic_fixture", "status": "PASS", "value": len(mart), "detail": "Test-mode deterministic dataset"},
        {"check": "database_connection", "status": "PASS", "value": "ISOLATED", "detail": "No production DB accessed during test suite"},
    ])
    return mart, item_mart, rfm, cohorts, quality


def load_dashboard_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame] | None:
    # Check explicit test mode first (used during CI and automated test runs)
    if os.getenv("COMMERCELENS_TEST_MODE") == "1":
        return get_deterministic_test_data()

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
