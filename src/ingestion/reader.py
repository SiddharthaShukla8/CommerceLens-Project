"""Safe, reusable Olist CSV ingestion."""
from pathlib import Path
import pandas as pd
from config.settings import REQUIRED_FILES
from src.utils.logging import get_logger

LOG = get_logger(__name__)
DATE_COLUMNS = {
    "orders": ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"],
    "order_items": ["shipping_limit_date"], "reviews": ["review_creation_date", "review_answer_timestamp"],
}

def missing_sources(raw_dir: Path) -> list[str]:
    return [filename for filename in REQUIRED_FILES.values() if not (raw_dir / filename).exists()]

def read_sources(raw_dir: Path) -> dict[str, pd.DataFrame]:
    missing = missing_sources(raw_dir)
    if missing:
        raise FileNotFoundError("Missing required Olist files: " + ", ".join(missing))
    frames = {}
    for name, filename in REQUIRED_FILES.items():
        path = raw_dir / filename
        frame = pd.read_csv(path, encoding="utf-8")
        for column in DATE_COLUMNS.get(name, []):
            if column in frame:
                frame[column] = pd.to_datetime(frame[column], errors="coerce")
        frames[name] = frame
        LOG.info("Loaded %s rows from %s", len(frame), filename)
    return frames
