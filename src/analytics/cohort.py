import pandas as pd

def build_cohorts(mart: pd.DataFrame) -> pd.DataFrame:
    orders = mart[mart.order_status.eq("delivered")].dropna(subset=["customer_unique_id", "order_purchase_timestamp"]).copy()
    orders["month"] = orders.order_purchase_timestamp.dt.to_period("M")
    orders["cohort"] = orders.groupby("customer_unique_id").month.transform("min")
    activity = orders.groupby(["cohort", "month"]).customer_unique_id.nunique().rename("customers").reset_index()
    activity["period_number"] = (activity.month.astype(int) - activity.cohort.astype(int)).astype(int)
    size = activity[activity.period_number.eq(0)][["cohort", "customers"]].rename(columns={"customers": "cohort_size"})
    return activity.merge(size, on="cohort").assign(retention_pct=lambda x: x.customers / x.cohort_size * 100)
