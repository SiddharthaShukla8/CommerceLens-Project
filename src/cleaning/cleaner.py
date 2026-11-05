"""Cleaning with a transparent, row-counted audit trail."""
from __future__ import annotations
import pandas as pd
import numpy as np

VALID_STATUSES = {"created", "approved", "invoiced", "processing", "shipped", "delivered", "unavailable", "canceled"}

def _event(audit: list[dict], table: str, rule: str, affected: int, treatment: str) -> None:
    audit.append({"table": table, "rule": rule, "affected_rows": int(affected), "treatment": treatment})

def clean_sources(frames: dict[str, pd.DataFrame]) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    clean = {name: df.copy() for name, df in frames.items()}
    audit: list[dict] = []
    for name, df in clean.items():
        duplicate_count = int(df.duplicated().sum())
        if duplicate_count:
            clean[name] = df.drop_duplicates().copy()
        _event(audit, name, "exact_duplicates", duplicate_count, "Removed exact duplicate records only")
    products = clean["products"]
    missing_category = int(products["product_category_name"].isna().sum())
    products["product_category_name"] = products["product_category_name"].fillna("unknown")
    _event(audit, "products", "missing_category", missing_category, "Labelled as unknown to retain sale history")
    translations = clean["translation"].drop_duplicates("product_category_name")
    clean["products"] = products.merge(translations, how="left", on="product_category_name")
    items = clean["order_items"]
    for col in ["price", "freight_value"]:
        invalid = int((items[col] < 0).fillna(False).sum())
        items.loc[items[col] < 0, col] = np.nan
        _event(audit, "order_items", f"negative_{col}", invalid, "Set impossible financial amount to null for review")
    orders = clean["orders"]
    bad_status = int((~orders["order_status"].isin(VALID_STATUSES)).sum())
    orders.loc[~orders["order_status"].isin(VALID_STATUSES), "order_status"] = "unknown"
    _event(audit, "orders", "invalid_status", bad_status, "Relabelled unknown; retained source record")
    invalid_dates = (orders["order_delivered_customer_date"].notna() & orders["order_purchase_timestamp"].notna() & (orders["order_delivered_customer_date"] < orders["order_purchase_timestamp"])).sum()
    orders.loc[(orders["order_delivered_customer_date"] < orders["order_purchase_timestamp"]), "order_delivered_customer_date"] = pd.NaT
    _event(audit, "orders", "delivery_before_purchase", int(invalid_dates), "Set impossible delivery timestamp to null")
    return clean, pd.DataFrame(audit)
