"""CommerceLens interactive business intelligence dashboard."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from config.settings import EXPORT_DIR
from dashboard.components.ui import inject_css, kpi_card
from dashboard.data import filter_order_mart, load_dashboard_data
from src.analytics.ab_testing import analyse_experiment, synthetic_experiment
from src.analytics.cohort import build_cohorts
from src.analytics.insights import generate_insights
from src.analytics.mart import kpis
from src.analytics.rfm import SEGMENT_ACTIONS, build_rfm, segment_summary


st.set_page_config(page_title="CommerceLens", page_icon="◈", layout="wide")
inject_css()
px.defaults.template = "plotly_white"


@st.cache_data(ttl=300, show_spinner=False)
def load_data(_: tuple[float, ...]):
    return load_dashboard_data()


def _reset_filters() -> None:
    for key in ("purchase_date", "customer_states", "order_statuses"):
        st.session_state.pop(key, None)


def _sales_summary(items: pd.DataFrame) -> dict[str, float]:
    return {
        "gmv": float(items.price.sum()),
        "units": int(len(items)),
        "orders": int(items.order_id.nunique()),
        "average_price": float(items.price.mean()) if not items.empty else 0.0,
    }


required_paths = [
    EXPORT_DIR / name
    for name in ("order_mart.csv", "item_mart.csv", "rfm_segments.csv", "cohort_retention.csv", "data_quality.csv")
]
data = load_data(tuple(path.stat().st_mtime if path.exists() else 0 for path in required_paths))

with st.sidebar:
    st.title("CommerceLens")
    st.caption("E-commerce intelligence platform")
    page = st.radio(
        "Navigate",
        [
            "Executive overview", "Sales & products", "Customer intelligence",
            "Operations & delivery", "Geographical analytics", "Experiment analytics", "Data quality",
        ],
    )
    st.divider()
    st.caption("Olist public dataset · independent portfolio project")

if data is None and page != "Experiment analytics":
    st.title("Your analytics workspace is ready")
    st.info("Load the Olist CSV files with the ETL pipeline or configure a PostgreSQL database containing the CommerceLens analytics schema.")
    st.code("docker compose up -d\npython -m src.cli run-all --database\nstreamlit run app.py")
    st.stop()

if page == "Experiment analytics":
    st.title("Experiment analytics")
    st.warning("SIMULATED EXPERIMENT DATA — NOT OBSERVED OLIST BUSINESS RESULTS.")
    result = analyse_experiment(synthetic_experiment())
    cols = st.columns(4)
    metrics = [
        ("Control conversion", f"{result['summary'].iloc[0]['mean']:.2%}"),
        ("Treatment conversion", f"{result['summary'].iloc[1]['mean']:.2%}"),
        ("Relative lift", f"{result['relative_lift']:.1%}"),
        ("P-value", f"{result['p_value']:.4f}"),
    ]
    for column, (name, value) in zip(cols, metrics):
        with column:
            kpi_card(name, value)
    st.plotly_chart(
        px.bar(result["summary"], x="experiment_group", y="mean", text_auto=".2%", title="Conversion rate by randomized group"),
        width="stretch", theme=None,
    )
    st.success("Reject the null hypothesis at α = 0.05." if result["significant"] else "Do not reject the null hypothesis at α = 0.05.")
    st.caption(f"95% CI for absolute difference: {result['confidence_interval'][0]:.2%} to {result['confidence_interval'][1]:.2%}. Seeded synthetic checkout experiment; exposed users only.")
    st.stop()

mart, item_mart, _, _, quality = data
min_date, max_date = mart.order_purchase_timestamp.min().date(), mart.order_purchase_timestamp.max().date()
with st.sidebar:
    st.divider()
    st.subheader("Shared filters")
    selected_range = st.date_input("Purchase date", value=(min_date, max_date), min_value=min_date, max_value=max_date, key="purchase_date")
    states = st.multiselect("Customer state", sorted(mart.customer_state.dropna().unique()), key="customer_states")
    statuses = st.multiselect("Order status", sorted(mart.order_status.dropna().unique()), key="order_statuses")
    st.button("Reset filters", on_click=_reset_filters, use_container_width=True)

filtered = filter_order_mart(mart, selected_range, states, statuses)
filtered_items = item_mart[item_mart.order_id.isin(filtered.order_id)]
delivered = filtered[filtered.order_status.eq("delivered")]
delivered_items = filtered_items[filtered_items.order_status.eq("delivered")]

if filtered.empty:
    st.title(page.title())
    st.warning("No orders match the active filters. Reset filters or select a broader range.")
    st.stop()

if page == "Executive overview":
    st.title("Executive overview")
    metric = kpis(filtered)
    cards = [
        ("Completed GMV", f"R$ {metric['merchandise_gmv']:,.0f}", "Delivered merchandise value"),
        ("Delivered orders", f"{metric['delivered_orders']:,}", "Distinct orders"),
        ("AOV", f"R$ {metric['aov']:,.0f}", "GMV / delivered order"),
        ("Unique customers", f"{metric['unique_customers']:,}", "Delivered-order customers"),
        ("Repeat rate", f"{metric['repeat_purchase_rate']:.1f}%", "2+ delivered orders"),
        ("On-time delivery", f"{metric['on_time_delivery_rate']:.1f}%", "Eligible orders only"),
    ]
    for column, item in zip(st.columns(6), cards):
        with column:
            kpi_card(*item)
    monthly = (delivered.assign(month=delivered.order_purchase_timestamp.dt.to_period("M").astype(str))
               .groupby("month", as_index=False)
               .agg(gmv=("merchandise_gmv", "sum"), orders=("order_id", "nunique")))
    category = (delivered_items.groupby("category", as_index=False).price.sum()
                .rename(columns={"price": "gmv"}).nlargest(5, "gmv"))
    left, right = st.columns(2)
    left.plotly_chart(px.line(monthly, x="month", y="gmv", markers=True, title="Monthly merchandise GMV"), width="stretch", theme=None)
    right.plotly_chart(px.bar(category, x="gmv", y="category", orientation="h", title="Top categories"), width="stretch", theme=None)
    status_counts = filtered.groupby("order_status", as_index=False).order_id.nunique()
    st.plotly_chart(px.bar(status_counts, x="order_status", y="order_id", title="Order-status distribution"), width="stretch", theme=None)
    st.subheader("Evidence-based actions")
    rfm_current = build_rfm(filtered)
    for insight in generate_insights(filtered, rfm_current):
        st.info(f"**{insight['observation']}** {insight['metric']} — {insight['action']}")

elif page == "Sales & products":
    st.title("Sales & product analytics")
    categories = sorted(delivered_items.category.dropna().unique().tolist())
    category = st.selectbox("Product category", ["All"] + categories)
    category_items = delivered_items if category == "All" else delivered_items[delivered_items.category.eq(category)]
    products = sorted(category_items.product_id.dropna().unique().tolist())
    product = st.selectbox("Product", ["All"] + products)
    visual = category_items if product == "All" else category_items[category_items.product_id.eq(product)]
    summary = _sales_summary(visual)
    sales_cards = [("Merchandise GMV", f"R$ {summary['gmv']:,.0f}", "Selected items"), ("Units sold", f"{summary['units']:,}", "Order-item records"), ("Delivered orders", f"{summary['orders']:,}", "Orders containing selection"), ("Average selling price", f"R$ {summary['average_price']:,.2f}", "Per item")]
    for column, item in zip(st.columns(4), sales_cards):
        with column:
            kpi_card(*item)
    daily = visual.assign(date=visual.order_purchase_timestamp.dt.date).groupby("date", as_index=False).price.sum().rename(columns={"price": "gmv"})
    weekly = visual.assign(week=visual.order_purchase_timestamp.dt.to_period("W").dt.start_time).groupby("week", as_index=False).price.sum().rename(columns={"price": "gmv"})
    category_totals = (delivered_items.groupby("category", as_index=False).agg(gmv=("price", "sum"), units=("order_item_id", "count"))
                       .sort_values("gmv", ascending=False))
    left, right = st.columns(2)
    left.plotly_chart(px.line(daily, x="date", y="gmv", title="Daily merchandise GMV"), width="stretch", theme=None)
    right.plotly_chart(px.line(weekly, x="week", y="gmv", title="Weekly merchandise GMV"), width="stretch", theme=None)
    st.plotly_chart(px.bar(category_totals.head(15), x="category", y="gmv", title="Category GMV"), width="stretch", theme=None)
    product_table = (visual.groupby(["product_id", "category"], as_index=False).agg(gmv=("price", "sum"), units=("order_item_id", "count"), average_selling_price=("price", "mean"))
                     .sort_values("gmv", ascending=False))
    st.subheader("Product performance")
    st.dataframe(product_table, width="stretch", hide_index=True)
    st.download_button("Download selected product CSV", product_table.to_csv(index=False), "product_performance.csv", "text/csv")

elif page == "Customer intelligence":
    st.title("Customer intelligence")
    rfm_current = build_rfm(filtered)
    segments = sorted(rfm_current.segment.unique().tolist())
    segment = st.selectbox("Customer segment", ["All"] + segments)
    shown = rfm_current if segment == "All" else rfm_current[rfm_current.segment.eq(segment)]
    customer_cards = [
        ("Customers", f"{shown.customer_unique_id.nunique():,}", "In selected segment"),
        ("Historical GMV", f"R$ {shown.monetary.sum():,.0f}", "Delivered merchandise"),
        ("Avg. purchase value", f"R$ {shown.monetary.mean():,.2f}" if not shown.empty else "R$ 0.00", "Per customer"),
        ("Avg. purchase frequency", f"{shown.frequency.mean():.2f}" if not shown.empty else "0.00", "Delivered orders/customer"),
    ]
    for column, item in zip(st.columns(4), customer_cards):
        with column:
            kpi_card(*item)
    summary = segment_summary(rfm_current)
    left, right = st.columns(2)
    left.plotly_chart(px.bar(summary.sort_values("customers", ascending=False), x="segment", y="customers", title="RFM segment distribution"), width="stretch", theme=None)
    right.plotly_chart(px.histogram(shown, x="monetary", nbins=40, title="Historical customer GMV"), width="stretch", theme=None)
    if segment != "All":
        st.info(f"**Recommended action for {segment}:** {SEGMENT_ACTIONS[segment]}")
    st.subheader("Customers in selection")
    st.dataframe(shown.sort_values("monetary", ascending=False), width="stretch", hide_index=True)
    cohorts_current = build_cohorts(filtered)
    heat = cohorts_current.pivot(index="cohort", columns="period_number", values="retention_pct")
    heat.index = heat.index.astype(str)
    st.plotly_chart(px.imshow(heat, text_auto=".0f", aspect="auto", color_continuous_scale="Blues", title="Monthly cohort retention (%)"), width="stretch", theme=None)

elif page == "Operations & delivery":
    st.title("Operations & delivery")
    eligible = delivered.dropna(subset=["on_time"])
    cancelled = filtered.order_status.eq("canceled").sum()
    unavailable = filtered.order_status.eq("unavailable").sum()
    operations_cards = [
        ("Delivered orders", f"{delivered.order_id.nunique():,}", "Selected period"),
        ("Cancelled orders", f"{cancelled:,}", f"{cancelled / len(filtered):.1%} of selected orders"),
        ("Unavailable orders", f"{unavailable:,}", "Selected period"),
        ("On-time delivery", f"{eligible.on_time.mean():.1%}" if not eligible.empty else "n/a", "Eligible deliveries"),
        ("Average delivery", f"{delivered.delivery_days.mean():.1f} days" if not delivered.empty else "n/a", "Delivered orders"),
    ]
    for column, item in zip(st.columns(5), operations_cards):
        with column:
            kpi_card(*item)
    left, right = st.columns(2)
    left.plotly_chart(px.histogram(delivered, x="delivery_days", nbins=40, title="Delivery duration (days)"), width="stretch", theme=None)
    right.plotly_chart(px.bar(filtered.groupby("order_status", as_index=False).order_id.nunique(), x="order_status", y="order_id", title="Order-status distribution"), width="stretch", theme=None)
    late = delivered[delivered.on_time.eq(False)][["order_id", "order_purchase_timestamp", "order_estimated_delivery_date", "order_delivered_customer_date", "customer_state"]].copy()
    late["delayed_days"] = (late.order_delivered_customer_date - late.order_estimated_delivery_date).dt.days
    st.subheader("Delayed orders")
    st.dataframe(late.sort_values("delayed_days", ascending=False), width="stretch", hide_index=True)
    sellers = (delivered_items.groupby("seller_id", as_index=False).agg(gmv=("price", "sum"), units=("order_item_id", "count"), orders=("order_id", "nunique"))
               .sort_values("gmv", ascending=False).head(20))
    st.plotly_chart(px.bar(sellers, x="seller_id", y="gmv", title="Top sellers by delivered GMV"), width="stretch", theme=None)

elif page == "Geographical analytics":
    st.title("Geographical analytics")
    state = (filtered.groupby("customer_state", as_index=False)
             .agg(orders=("order_id", "nunique"), merchandise_gmv=("merchandise_gmv", "sum"), customers=("customer_unique_id", "nunique"), on_time=("on_time", "mean"), cancellation_rate=("order_status", lambda x: x.eq("canceled").mean()))
             .assign(aov=lambda frame: frame.merchandise_gmv / frame.orders))
    left, right = st.columns(2)
    left.plotly_chart(px.bar(state.sort_values("merchandise_gmv", ascending=False), x="customer_state", y="merchandise_gmv", title="GMV by customer state"), width="stretch", theme=None)
    right.plotly_chart(px.bar(state.sort_values("orders", ascending=False), x="customer_state", y="orders", title="Orders by customer state"), width="stretch", theme=None)
    st.dataframe(state.sort_values("merchandise_gmv", ascending=False), width="stretch", hide_index=True)

else:
    st.title("Data quality & pipeline monitoring")
    st.dataframe(quality, width="stretch", hide_index=True)
    metadata = EXPORT_DIR / "pipeline_metadata.json"
    if metadata.exists():
        st.json(metadata.read_text())
    else:
        st.info("This dashboard session is using PostgreSQL fallback data. Run the ETL pipeline to publish local pipeline metadata and exports.")
    st.download_button("Download quality CSV", quality.to_csv(index=False), "data_quality.csv", "text/csv")
