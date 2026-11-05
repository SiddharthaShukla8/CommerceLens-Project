"""Runtime configuration for CommerceLens."""
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / os.getenv("DATA_DIR", "data")
RAW_DIR, PROCESSED_DIR, EXPORT_DIR = DATA_DIR / "raw", DATA_DIR / "processed", DATA_DIR / "exports"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://commercelens:commercelens@localhost:5432/commercelens")
REQUIRED_FILES = {
    "customers": "olist_customers_dataset.csv", "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv", "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv", "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv", "geolocation": "olist_geolocation_dataset.csv",
    "translation": "product_category_name_translation.csv",
}
DELIVERED_STATUS = "delivered"
