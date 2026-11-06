"""Idempotently replace staging and analytics tables from cleaned outputs."""
import pandas as pd
from sqlalchemy import create_engine, text
from config.settings import DATABASE_CONNECT_TIMEOUT, DATABASE_SSLMODE, DATABASE_URL_UNPOOLED
from src.database.schema_manager import apply_migrations

TABLE_MAP = {"customers": "customers", "orders": "orders", "order_items": "order_items", "payments": "payments", "reviews": "reviews", "products": "products", "sellers": "sellers"}
STAGING_COLUMNS = {
    "customers": ["customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"],
    "orders": ["order_id", "customer_id", "order_status", "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"],
    "order_items": ["order_id", "order_item_id", "product_id", "seller_id", "shipping_limit_date", "price", "freight_value"],
    "payments": ["order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"],
    "reviews": ["review_id", "order_id", "review_score", "review_comment_title", "review_comment_message", "review_creation_date", "review_answer_timestamp"],
    "products": ["product_id", "product_category_name", "product_category_name_english"],
    "sellers": ["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"],
}

def load_to_postgres(frames: dict[str, pd.DataFrame], mart: pd.DataFrame) -> None:
    connect_args = {"connect_timeout": DATABASE_CONNECT_TIMEOUT}
    if DATABASE_SSLMODE and not DATABASE_URL_UNPOOLED.startswith("sqlite"):
        connect_args["sslmode"] = DATABASE_SSLMODE
    engine = create_engine(DATABASE_URL_UNPOOLED, pool_pre_ping=True, pool_size=5, max_overflow=5, connect_args=connect_args)
    with engine.begin() as connection:
        apply_migrations(connection)
        for name, table in TABLE_MAP.items():
            connection.execute(text(f"TRUNCATE TABLE staging.{table} CASCADE"))
            frames[name][STAGING_COLUMNS[name]].to_sql(table, connection, schema="staging", if_exists="append", index=False, method="multi", chunksize=5000)
        for table in ["dim_customers", "dim_products", "dim_sellers", "fact_orders", "fact_order_items", "fact_payments", "fact_reviews"]:
            connection.execute(text(f"TRUNCATE TABLE analytics.{table}"))
        connection.execute(text("INSERT INTO analytics.dim_customers SELECT * FROM staging.customers"))
        connection.execute(text("INSERT INTO analytics.dim_products SELECT * FROM staging.products"))
        connection.execute(text("INSERT INTO analytics.dim_sellers SELECT * FROM staging.sellers"))
        connection.execute(text("INSERT INTO analytics.fact_orders SELECT * FROM staging.orders"))
        connection.execute(text("INSERT INTO analytics.fact_order_items SELECT * FROM staging.order_items"))
        connection.execute(text("INSERT INTO analytics.fact_payments SELECT * FROM staging.payments"))
        connection.execute(text("INSERT INTO analytics.fact_reviews SELECT * FROM staging.reviews"))
        connection.execute(text("TRUNCATE TABLE analytics.dim_date"))
        connection.execute(text("""
            INSERT INTO analytics.dim_date(date_key, calendar_year, calendar_quarter, calendar_month, month_name, week_of_year)
            SELECT d::date, EXTRACT(YEAR FROM d)::smallint, EXTRACT(QUARTER FROM d)::smallint,
                   EXTRACT(MONTH FROM d)::smallint, TO_CHAR(d, 'Month'), EXTRACT(WEEK FROM d)::smallint
            FROM generate_series(
              (SELECT MIN(order_purchase_timestamp)::date FROM staging.orders),
              (SELECT MAX(order_purchase_timestamp)::date FROM staging.orders), '1 day'::interval
            ) AS d
        """))
