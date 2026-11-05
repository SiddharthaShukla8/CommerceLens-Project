import pandas as pd
from src.cleaning.cleaner import clean_sources
from src.validation.quality import validate

def test_cleaning_and_validation():
    frames={"customers":pd.DataFrame({"customer_id":["c1"],"customer_unique_id":["u1"]}),"orders":pd.DataFrame({"order_id":["o1"],"customer_id":["c1"],"order_status":["delivered"],"order_purchase_timestamp":pd.to_datetime(["2020-01-02"]),"order_delivered_customer_date":pd.to_datetime(["2020-01-01"])}),"order_items":pd.DataFrame({"order_id":["o1"],"price":[-1],"freight_value":[1]}),"products":pd.DataFrame({"product_id":["p1"],"product_category_name":[None]}),"translation":pd.DataFrame({"product_category_name":[],"product_category_name_english":[]}),"payments":pd.DataFrame(),"reviews":pd.DataFrame(),"sellers":pd.DataFrame(),"geolocation":pd.DataFrame()}
    clean,audit=clean_sources(frames)
    assert clean["order_items"].price.isna().all()
    assert not audit.empty
    assert "FAIL" not in validate(clean).query("check == 'orders.order_id uniqueness'").status.tolist()
