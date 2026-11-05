import pandas as pd
from src.analytics.cohort import build_cohorts
from src.analytics.insights import generate_insights
from src.analytics.rfm import build_rfm, segment_summary
from src.analytics.mart import build_order_mart

def fixture_frames():
    return {"customers": pd.DataFrame({"customer_id": ["c1", "c2"], "customer_unique_id": ["u1", "u1"], "customer_state": ["SP", "SP"]}), "orders": pd.DataFrame({"order_id": ["o1", "o2"], "customer_id": ["c1", "c2"], "order_status": ["delivered", "delivered"], "order_purchase_timestamp": pd.to_datetime(["2018-01-01", "2018-02-01"]), "order_delivered_customer_date": pd.to_datetime(["2018-01-04", "2018-02-04"]), "order_estimated_delivery_date": pd.to_datetime(["2018-01-05", "2018-02-05"])}), "order_items": pd.DataFrame({"order_id": ["o1", "o2"], "order_item_id": [1, 1], "product_id": ["p1", "p2"], "price": [10.0, 20.0], "freight_value": [2.0, 3.0]}), "products": pd.DataFrame({"product_id": ["p1", "p2"], "product_category_name_english": ["books", "toys"]})}

def test_cohort_retention_starts_at_one_hundred_percent():
    cohorts = build_cohorts(build_order_mart(fixture_frames()))
    assert cohorts.loc[cohorts.period_number.eq(0), "retention_pct"].eq(100).all()

def test_rfm_segments_are_exclusive_and_summarized():
    rfm = build_rfm(build_order_mart(fixture_frames()))
    summary = segment_summary(rfm)
    assert len(rfm) == summary.customers.sum()
    assert summary.recommended_action.notna().all()

def test_insights_are_evidence_backed():
    mart = build_order_mart(fixture_frames())
    insights = generate_insights(mart, build_rfm(mart))
    assert insights and {"observation", "metric", "action"}.issubset(insights[0])
