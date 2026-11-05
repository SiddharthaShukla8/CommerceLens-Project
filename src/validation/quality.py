"""Dataset validation rules producing PASS, WARNING, and FAIL results."""
from __future__ import annotations
import pandas as pd
from src.cleaning.cleaner import VALID_STATUSES

def _row(check: str, status: str, value: int | float, detail: str) -> dict:
    return {"check": check, "status": status, "value": value, "detail": detail}

def validate(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    keys = {"customers": "customer_id", "orders": "order_id", "products": "product_id", "sellers": "seller_id"}
    for table, key in keys.items():
        if key not in frames[table].columns:
            rows.append(_row(f"{table}.{key} uniqueness", "WARNING", 0, "Key column unavailable in this input"))
            continue
        duplicate = int(frames[table][key].duplicated().sum())
        rows.append(_row(f"{table}.{key} uniqueness", "PASS" if not duplicate else "FAIL", duplicate, "Duplicate primary keys"))
    orders, customers, items = frames["orders"], frames["customers"], frames["order_items"]
    orphan_customers = int((~orders.customer_id.isin(customers.customer_id)).sum())
    orphan_orders = int((~items.order_id.isin(orders.order_id)).sum())
    rows.extend([_row("orders customer FK", "PASS" if not orphan_customers else "FAIL", orphan_customers, "Orders without a customer"), _row("items order FK", "PASS" if not orphan_orders else "FAIL", orphan_orders, "Items without an order")])
    for table, column, reference, reference_column in [("order_items", "product_id", "products", "product_id"), ("order_items", "seller_id", "sellers", "seller_id"), ("payments", "order_id", "orders", "order_id"), ("reviews", "order_id", "orders", "order_id")]:
        if column in frames[table] and reference_column in frames[reference]:
            orphan_count = int((~frames[table][column].dropna().isin(frames[reference][reference_column])).sum())
            rows.append(_row(f"{table} {column} FK", "PASS" if not orphan_count else "FAIL", orphan_count, f"{table} records without a valid {reference}"))
    negative = int(((items.price < 0) | (items.freight_value < 0)).sum())
    rows.append(_row("non-negative financial values", "PASS" if not negative else "FAIL", negative, "Negative price or freight"))
    payments = frames["payments"]
    if "payment_value" in payments:
        negative_payments = int((payments.payment_value < 0).fillna(False).sum())
        rows.append(_row("non-negative payment values", "PASS" if not negative_payments else "FAIL", negative_payments, "Negative payment values"))
    invalid_statuses = int((~orders.order_status.isin(VALID_STATUSES)).sum())
    rows.append(_row("valid order statuses", "PASS" if not invalid_statuses else "FAIL", invalid_statuses, "Unexpected order statuses"))
    if {"order_purchase_timestamp", "order_delivered_customer_date"}.issubset(orders.columns):
        invalid_sequence = int(((orders.order_delivered_customer_date < orders.order_purchase_timestamp).fillna(False)).sum())
        rows.append(_row("valid delivery sequence", "PASS" if not invalid_sequence else "FAIL", invalid_sequence, "Delivery before purchase"))
    for table, frame in frames.items():
        missing_pct = round(float(frame.isna().mean().mean() * 100), 2)
        rows.append(_row(f"{table} missing values", "WARNING" if missing_pct else "PASS", missing_pct, "Average missing percentage across columns"))
    return pd.DataFrame(rows)
