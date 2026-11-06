import pandas as pd
from src.analytics.mart import build_item_mart, build_order_mart, kpis
from src.analytics.rfm import build_rfm
from src.analytics.ab_testing import synthetic_experiment, analyse_experiment

def fixture_frames():
    return {"customers":pd.DataFrame({"customer_id":["c1","c2"],"customer_unique_id":["u1","u1"],"customer_state":["SP","SP"]}),"orders":pd.DataFrame({"order_id":["o1","o2"],"customer_id":["c1","c2"],"order_status":["delivered","delivered"],"order_purchase_timestamp":pd.to_datetime(["2018-01-01","2018-02-01"]),"order_delivered_customer_date":pd.to_datetime(["2018-01-04","2018-02-04"]),"order_estimated_delivery_date":pd.to_datetime(["2018-01-05","2018-02-05"])}),"order_items":pd.DataFrame({"order_id":["o1","o2"],"order_item_id":[1,1],"product_id":["p1","p2"],"seller_id":["s1","s2"],"price":[10.0,20.0],"freight_value":[2.0,3.0]}),"products":pd.DataFrame({"product_id":["p1","p2"],"product_category_name_english":["books","toys"]})}

def test_kpi_and_rfm():
    mart=build_order_mart(fixture_frames()); metrics=kpis(mart)
    assert metrics["merchandise_gmv"] == 30
    assert metrics["repeat_purchase_rate"] == 100
    assert build_rfm(mart).iloc[0].frequency == 2

def test_synthetic_experiment_is_reproducible():
    assert synthetic_experiment().equals(synthetic_experiment())
    assert "p_value" in analyse_experiment(synthetic_experiment())


def test_item_mart_preserves_item_grain_for_product_drill_down():
    items = build_item_mart(fixture_frames())
    assert len(items) == 2
    assert not {"product_id", "seller_id", "category", "price", "order_status"}.difference(items.columns)
    assert items.groupby("product_id").price.sum().to_dict() == {"p1": 10.0, "p2": 20.0}
