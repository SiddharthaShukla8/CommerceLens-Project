"""Business-safe order-grain dataset and KPI calculations."""
from __future__ import annotations
import pandas as pd
import numpy as np

def build_order_mart(f: dict[str, pd.DataFrame]) -> pd.DataFrame:
    products = f["products"][["product_id", "product_category_name_english"]].rename(columns={"product_category_name_english": "category"})
    item = f["order_items"].merge(products, on="product_id", how="left")
    item["category"] = item["category"].fillna("unknown")
    item_agg = item.groupby("order_id", as_index=False).agg(merchandise_gmv=("price", "sum"), freight_value=("freight_value", "sum"), units=("order_item_id", "count"))
    categories = item.groupby(["order_id", "category"], as_index=False).agg(category_gmv=("price", "sum"), units=("order_item_id", "count"))
    main_category = categories.sort_values(["order_id", "category_gmv"], ascending=[True, False]).drop_duplicates("order_id")[["order_id", "category"]]
    customers = f["customers"][["customer_id", "customer_unique_id", "customer_state"]]
    orders = f["orders"].merge(customers, on="customer_id", how="left").merge(item_agg, on="order_id", how="left").merge(main_category, on="order_id", how="left")
    orders["merchandise_gmv"] = orders["merchandise_gmv"].fillna(0.0)
    orders["freight_value"] = orders["freight_value"].fillna(0.0)
    orders["order_value"] = orders["merchandise_gmv"] + orders["freight_value"]
    orders["delivery_days"] = (orders.order_delivered_customer_date - orders.order_purchase_timestamp).dt.total_seconds() / 86400
    eligible = orders.order_delivered_customer_date.notna() & orders.order_estimated_delivery_date.notna()
    orders["on_time"] = np.where(eligible, orders.order_delivered_customer_date <= orders.order_estimated_delivery_date, np.nan)
    return orders


def build_item_mart(f: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build a delivered-sales-safe item-grain mart for product analysis.

    Product and category filters must operate at item grain.  This mart is
    intentionally separate from the order-grain KPI mart so filtering a
    multi-item order does not accidentally attribute every item to one product.
    """
    product_columns = ["product_id", "product_category_name_english"]
    products = f["products"][product_columns].rename(
        columns={"product_category_name_english": "category"}
    )
    order_columns = [
        "order_id", "customer_id", "order_status", "order_purchase_timestamp",
        "order_delivered_customer_date", "order_estimated_delivery_date",
    ]
    customers = f["customers"][["customer_id", "customer_unique_id", "customer_state"]]
    orders = f["orders"][order_columns].merge(customers, on="customer_id", how="left")
    items = f["order_items"].merge(products, on="product_id", how="left")
    items["category"] = items["category"].fillna("unknown")
    return items.merge(orders, on="order_id", how="inner")

def kpis(mart: pd.DataFrame) -> dict[str, float]:
    delivered = mart[mart.order_status.eq("delivered")].copy()
    customers = delivered.customer_unique_id.dropna()
    order_counts = delivered.groupby("customer_unique_id").order_id.nunique()
    eligible = delivered.on_time.dropna()
    return {"merchandise_gmv": float(delivered.merchandise_gmv.sum()), "delivered_orders": int(delivered.order_id.nunique()), "aov": float(delivered.merchandise_gmv.sum() / max(delivered.order_id.nunique(), 1)), "unique_customers": int(customers.nunique()), "repeat_purchase_rate": float((order_counts.ge(2).sum() / max(len(order_counts), 1)) * 100), "on_time_delivery_rate": float(eligible.mean() * 100) if len(eligible) else 0.0}
