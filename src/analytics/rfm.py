from __future__ import annotations
import pandas as pd

def build_rfm(mart: pd.DataFrame) -> pd.DataFrame:
    orders = mart[mart.order_status.eq("delivered")].dropna(subset=["order_purchase_timestamp", "customer_unique_id"])
    reference = orders.order_purchase_timestamp.max() + pd.Timedelta(days=1)
    rfm = orders.groupby("customer_unique_id").agg(recency=("order_purchase_timestamp", lambda x: (reference - x.max()).days), frequency=("order_id", "nunique"), monetary=("merchandise_gmv", "sum")).reset_index()
    if rfm.empty: return rfm
    n = min(5, rfm.customer_unique_id.nunique())
    rfm["r_score"] = pd.qcut(rfm.recency.rank(method="first", ascending=False), n, labels=False, duplicates="drop") + 1
    rfm["f_score"] = pd.qcut(rfm.frequency.rank(method="first"), n, labels=False, duplicates="drop") + 1
    rfm["m_score"] = pd.qcut(rfm.monetary.rank(method="first"), n, labels=False, duplicates="drop") + 1
    rfm["segment"] = "Other Customers"
    rfm.loc[(rfm.r_score >= 4) & (rfm.f_score >= 4), "segment"] = "Champions"
    rfm.loc[(rfm.r_score >= 3) & (rfm.f_score >= 3), "segment"] = "Loyal Customers"
    rfm.loc[(rfm.r_score >= 4) & (rfm.f_score <= 2), "segment"] = "Recent Customers"
    rfm.loc[(rfm.r_score <= 2) & (rfm.f_score >= 3), "segment"] = "Cannot Lose Them"
    rfm.loc[(rfm.r_score <= 2) & (rfm.f_score <= 2), "segment"] = "Hibernating"
    rfm.loc[(rfm.r_score == 3) & (rfm.f_score <= 2), "segment"] = "Potential Loyalists"
    rfm.loc[(rfm.r_score <= 2) & (rfm.m_score >= 4), "segment"] = "At Risk"
    return rfm
