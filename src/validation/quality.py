"""Dataset validation rules producing PASS, WARNING, and FAIL results."""
from __future__ import annotations
import pandas as pd

def _row(check: str, status: str, value: int | float, detail: str) -> dict:
    return {"check": check, "status": status, "value": value, "detail": detail}

def validate(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    keys = {"customers": "customer_id", "orders": "order_id", "products": "product_id", "sellers": "seller_id"}
    for table, key in keys.items():
        duplicate = int(frames[table][key].duplicated().sum())
        rows.append(_row(f"{table}.{key} uniqueness", "PASS" if not duplicate else "FAIL", duplicate, "Duplicate primary keys"))
    orders, customers, items = frames["orders"], frames["customers"], frames["order_items"]
    orphan_customers = int((~orders.customer_id.isin(customers.customer_id)).sum())
    orphan_orders = int((~items.order_id.isin(orders.order_id)).sum())
    rows.extend([_row("orders customer FK", "PASS" if not orphan_customers else "FAIL", orphan_customers, "Orders without a customer"), _row("items order FK", "PASS" if not orphan_orders else "FAIL", orphan_orders, "Items without an order")])
    negative = int(((items.price < 0) | (items.freight_value < 0)).sum())
    rows.append(_row("non-negative financial values", "PASS" if not negative else "FAIL", negative, "Negative price or freight"))
    for table, frame in frames.items():
        missing_pct = round(float(frame.isna().mean().mean() * 100), 2)
        rows.append(_row(f"{table} missing values", "WARNING" if missing_pct else "PASS", missing_pct, "Average missing percentage across columns"))
    return pd.DataFrame(rows)
