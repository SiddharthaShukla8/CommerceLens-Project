import pandas as pd

from dashboard.data import filter_order_mart


def test_shared_dashboard_filters_change_order_population():
    mart = pd.DataFrame(
        {
            "order_id": ["o1", "o2", "o3"],
            "order_purchase_timestamp": pd.to_datetime(["2018-01-01", "2018-02-01", "2018-02-02"]),
            "customer_state": ["SP", "RJ", "SP"],
            "order_status": ["delivered", "canceled", "delivered"],
        }
    )

    selected = filter_order_mart(
        mart,
        (pd.Timestamp("2018-02-01").date(), pd.Timestamp("2018-02-28").date()),
        ["SP"],
        ["delivered"],
    )

    assert selected.order_id.tolist() == ["o3"]
