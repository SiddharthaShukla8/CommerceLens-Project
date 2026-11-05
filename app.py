"""CommerceLens interactive business intelligence dashboard."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from config.settings import EXPORT_DIR
from src.analytics.mart import kpis
from src.analytics.ab_testing import synthetic_experiment, analyse_experiment
from src.analytics.insights import generate_insights
from dashboard.components.ui import inject_css, kpi_card

st.set_page_config(page_title="CommerceLens", page_icon="◈", layout="wide")
inject_css()
px.defaults.template = "plotly_white"

@st.cache_data(ttl=300, show_spinner=False)
def load_data(_: tuple[float, ...]):
    files = [EXPORT_DIR / "order_mart.csv", EXPORT_DIR / "rfm_segments.csv", EXPORT_DIR / "cohort_retention.csv", EXPORT_DIR / "data_quality.csv"]
    if not all(path.exists() for path in files): return None
    return (pd.read_csv(files[0], parse_dates=["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"]), pd.read_csv(files[1]), pd.read_csv(files[2]), pd.read_csv(files[3]))

required_paths = [EXPORT_DIR / name for name in ("order_mart.csv", "rfm_segments.csv", "cohort_retention.csv", "data_quality.csv")]
data = load_data(tuple(path.stat().st_mtime if path.exists() else 0 for path in required_paths))
with st.sidebar:
    st.title("CommerceLens")
    st.caption("E-commerce intelligence platform")
    page = st.radio("Navigate", ["Executive overview", "Sales & products", "Customer intelligence", "Operations & delivery", "Geographical analytics", "Experiment analytics", "Data quality"])
    st.divider(); st.caption("Olist public dataset · independent portfolio project")
if data is None and page != "Experiment analytics":
    st.title("Your analytics workspace is ready")
    st.info("Download the Olist CSV files into `data/raw/`, then run `python -m src.cli run-all`. CommerceLens will then calculate every KPI from your processed data.")
    st.code("docker compose up -d\npython -m src.cli run-all\nstreamlit run app.py")
    st.stop()

if page == "Experiment analytics":
    st.title("Experiment analytics")
    st.warning("SIMULATED EXPERIMENT DATA — NOT OBSERVED OLIST BUSINESS RESULTS.")
    result = analyse_experiment(synthetic_experiment())
    cols = st.columns(4)
    for col, (name, value) in zip(cols, [("Control conversion", f"{result['summary'].iloc[0]['mean']:.2%}"), ("Treatment conversion", f"{result['summary'].iloc[1]['mean']:.2%}"), ("Relative lift", f"{result['relative_lift']:.1%}"), ("P-value", f"{result['p_value']:.4f}")]):
        with col: kpi_card(name, value)
    st.plotly_chart(px.bar(result["summary"], x="experiment_group", y="mean", text_auto=".2%", title="Conversion rate by randomized group"), width="stretch", theme=None)
    st.success("Reject the null hypothesis at α = 0.05." if result["significant"] else "Do not reject the null hypothesis at α = 0.05.")
    st.caption(f"95% CI for absolute difference: {result['confidence_interval'][0]:.2%} to {result['confidence_interval'][1]:.2%}. Seeded synthetic checkout experiment; exposed users only.")
    st.stop()

mart, rfm, cohorts, quality = data
min_date, max_date = mart.order_purchase_timestamp.min().date(), mart.order_purchase_timestamp.max().date()
with st.sidebar:
    selected_range = st.date_input("Purchase date", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    states = st.multiselect("Customer state", sorted(mart.customer_state.dropna().unique()))
filtered = mart.copy()
if len(selected_range) == 2: filtered = filtered[filtered.order_purchase_timestamp.dt.date.between(selected_range[0], selected_range[1])]
if states: filtered = filtered[filtered.customer_state.isin(states)]
delivered = filtered[filtered.order_status.eq("delivered")]

if page == "Executive overview":
    st.title("Executive overview"); metric = kpis(filtered)
    cards = [("Completed GMV", f"R$ {metric['merchandise_gmv']:,.0f}", "Delivered merchandise value"), ("Delivered orders", f"{metric['delivered_orders']:,}", "Distinct orders"), ("AOV", f"R$ {metric['aov']:,.0f}", "GMV / delivered order"), ("Unique customers", f"{metric['unique_customers']:,}", "Delivered-order customers"), ("Repeat rate", f"{metric['repeat_purchase_rate']:.1f}%", "2+ delivered orders"), ("On-time delivery", f"{metric['on_time_delivery_rate']:.1f}%", "Eligible orders only")]
    for col, item in zip(st.columns(6), cards):
        with col: kpi_card(*item)
    monthly = delivered.assign(month=delivered.order_purchase_timestamp.dt.to_period("M").astype(str)).groupby("month", as_index=False).agg(gmv=("merchandise_gmv", "sum"), orders=("order_id", "nunique"))
    a,b = st.columns(2); a.plotly_chart(px.line(monthly, x="month", y="gmv", markers=True, title="Monthly merchandise GMV"), width="stretch", theme=None); b.plotly_chart(px.bar(delivered.groupby("category", as_index=False).merchandise_gmv.sum().nlargest(5,"merchandise_gmv"), x="merchandise_gmv", y="category", orientation="h", title="Top categories"), width="stretch", theme=None)
    st.subheader("Evidence-based actions")
    for insight in generate_insights(filtered, rfm): st.info(f"**{insight['observation']}** {insight['metric']} — {insight['action']}")
elif page == "Sales & products":
    st.title("Sales & product analytics")
    category = st.selectbox("Drill into category", ["All"] + sorted(delivered.category.dropna().unique().tolist()))
    visual = delivered if category == "All" else delivered[delivered.category == category]
    daily = visual.groupby(visual.order_purchase_timestamp.dt.date, as_index=False).merchandise_gmv.sum(); daily.columns = ["date", "gmv"]
    left,right = st.columns(2); left.plotly_chart(px.line(daily, x="date", y="gmv", title="Daily GMV"), width="stretch", theme=None); right.plotly_chart(px.bar(visual.groupby("category",as_index=False).agg(gmv=("merchandise_gmv","sum"),units=("units","sum")).sort_values("gmv",ascending=False).head(15),x="category",y="gmv",title="Category GMV"), width="stretch", theme=None)
    st.dataframe(visual.groupby("category",as_index=False).agg(gmv=("merchandise_gmv","sum"),units=("units","sum"),average_order_value=("merchandise_gmv","mean")).sort_values("gmv",ascending=False), width="stretch")
elif page == "Customer intelligence":
    st.title("Customer intelligence")
    segment = st.selectbox("Customer segment", ["All"] + sorted(rfm.segment.unique().tolist()))
    shown = rfm if segment == "All" else rfm[rfm.segment == segment]
    a,b = st.columns(2); a.plotly_chart(px.bar(rfm.groupby("segment",as_index=False).customer_unique_id.count(),x="segment",y="customer_unique_id",title="RFM segment distribution"), width="stretch", theme=None); b.plotly_chart(px.histogram(rfm,x="monetary",nbins=40,title="Historical customer GMV"), width="stretch", theme=None)
    st.metric("Customers in selection", f"{len(shown):,}"); st.dataframe(shown.sort_values("monetary",ascending=False), width="stretch")
    heat = cohorts.pivot(index="cohort", columns="period_number", values="retention_pct"); st.plotly_chart(px.imshow(heat, text_auto=".0f", aspect="auto", color_continuous_scale="Blues", title="Monthly cohort retention (%)"), width="stretch", theme=None)
elif page == "Operations & delivery":
    st.title("Operations & delivery")
    a,b = st.columns(2); a.plotly_chart(px.histogram(delivered,x="delivery_days",nbins=40,title="Delivery duration (days)"), width="stretch", theme=None); b.plotly_chart(px.bar(filtered.groupby("order_status",as_index=False).order_id.nunique(),x="order_status",y="order_id",title="Order-status distribution"), width="stretch", theme=None)
    late = delivered[delivered.on_time.eq(False)][["order_id","order_purchase_timestamp","order_estimated_delivery_date","order_delivered_customer_date","customer_state"]].copy(); late["delayed_days"]=(late.order_delivered_customer_date-late.order_estimated_delivery_date).dt.days
    st.subheader("Late orders"); st.dataframe(late.sort_values("delayed_days",ascending=False), width="stretch")
elif page == "Geographical analytics":
    st.title("Geographical analytics")
    state = delivered.groupby("customer_state",as_index=False).agg(gmv=("merchandise_gmv","sum"),orders=("order_id","nunique"),aov=("merchandise_gmv","mean"),on_time=("on_time","mean"))
    a,b=st.columns(2); a.plotly_chart(px.bar(state.sort_values("gmv",ascending=False),x="customer_state",y="gmv",title="GMV by customer state"), width="stretch", theme=None); b.plotly_chart(px.bar(state.sort_values("orders",ascending=False),x="customer_state",y="orders",title="Orders by customer state"), width="stretch", theme=None)
    st.dataframe(state.sort_values("gmv",ascending=False), width="stretch")
else:
    st.title("Data quality & pipeline monitoring")
    st.dataframe(quality, width="stretch")
    metadata = EXPORT_DIR / "pipeline_metadata.json"
    if metadata.exists(): st.json(metadata.read_text())
    st.download_button("Download quality CSV", quality.to_csv(index=False), "data_quality.csv", "text/csv")
