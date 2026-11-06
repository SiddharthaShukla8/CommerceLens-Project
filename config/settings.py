"""Runtime configuration for CommerceLens."""
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

def _setting(name: str, default: str | None = None) -> str | None:
    """Read environment variables locally and Streamlit secrets when deployed."""
    if value := os.getenv(name):
        return value
    try:
        import streamlit as st
        return st.secrets.get(name, default)
    except Exception:
        return default
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / (_setting("DATA_DIR", "data") or "data")
RAW_DIR, PROCESSED_DIR, EXPORT_DIR = DATA_DIR / "raw", DATA_DIR / "processed", DATA_DIR / "exports"
DATABASE_URL = _setting("DATABASE_URL", "postgresql+psycopg://commercelens:commercelens@localhost:5433/commercelens") or ""
DATABASE_SSLMODE = _setting("DATABASE_SSLMODE", "prefer") or "prefer"
DATABASE_CONNECT_TIMEOUT = int(_setting("DATABASE_CONNECT_TIMEOUT", "10") or 10)
REQUIRED_FILES = {
    "customers": "olist_customers_dataset.csv", "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv", "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv", "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv", "geolocation": "olist_geolocation_dataset.csv",
    "translation": "product_category_name_translation.csv",
}
DELIVERED_STATUS = "delivered"
