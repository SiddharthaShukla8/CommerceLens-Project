"""Transparent rule-based observations, never an LLM-generated recommendation."""
import pandas as pd

def generate_insights(mart: pd.DataFrame, rfm: pd.DataFrame) -> list[dict[str, str]]:
    delivered = mart[mart.order_status.eq("delivered")]
    if delivered.empty: return []
    monthly = delivered.assign(month=delivered.order_purchase_timestamp.dt.to_period("M").astype(str)).groupby("month").merchandise_gmv.sum()
    categories = delivered.groupby("category").merchandise_gmv.sum().sort_values(ascending=False)
    state_ontime = delivered.dropna(subset=["on_time"]).groupby("customer_state").on_time.mean().sort_values()
    result = [{"observation": f"{categories.index[0]} is the leading category by GMV.", "metric": f"{categories.iloc[0]:,.0f} merchandise GMV", "action": "Protect availability and use this category for cross-sell opportunities."}]
    if len(monthly) > 1 and monthly.iloc[-1] < monthly.iloc[-2]: result.append({"observation": "Most recent monthly GMV declined.", "metric": f"{(monthly.iloc[-1]/monthly.iloc[-2]-1)*100:.1f}% month-over-month", "action": "Review category-level demand and promotion changes before increasing spend."})
    if len(state_ontime): result.append({"observation": f"{state_ontime.index[0]} has the lowest on-time delivery rate.", "metric": f"{state_ontime.iloc[0]*100:.1f}%", "action": "Investigate carrier capacity and seller dispatch performance in this state."})
    if not rfm.empty and (rfm.segment == "At Risk").any(): result.append({"observation": "High-value inactive customers are present.", "metric": f"{(rfm.segment == 'At Risk').sum()} at-risk customers", "action": "Run a targeted reactivation offer and measure incremental repeat orders."})
    return result
