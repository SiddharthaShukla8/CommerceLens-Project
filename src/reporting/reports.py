from __future__ import annotations
from datetime import datetime
from pathlib import Path
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from config.settings import EXPORT_DIR, ROOT
from src.analytics.mart import kpis

def generate_monthly_report() -> tuple[Path, Path]:
    mart_path = EXPORT_DIR / "order_mart.csv"
    if not mart_path.exists(): raise FileNotFoundError("Run `python -m src.cli run-all` before generating reports.")
    mart = pd.read_csv(mart_path, parse_dates=["order_purchase_timestamp"]); metrics = kpis(mart)
    period = datetime.now().strftime("%Y%m%d_%H%M%S"); output = ROOT / "reports" / "generated"; output.mkdir(parents=True, exist_ok=True)
    csv_path = output / f"monthly_sales_{period}.csv"; delivered = mart[mart.order_status.eq("delivered")].copy(); delivered.to_csv(csv_path, index=False)
    delivered.groupby("category", as_index=False).agg(merchandise_gmv=("merchandise_gmv", "sum"), units=("units", "sum"), delivered_orders=("order_id", "nunique")).sort_values("merchandise_gmv", ascending=False).to_csv(output / f"product_performance_{period}.csv", index=False)
    mart.groupby("customer_state", as_index=False).agg(total_orders=("order_id", "nunique"), delivered_orders=("order_status", lambda x: (x == "delivered").sum()), average_delivery_days=("delivery_days", "mean"), on_time_delivery_rate=("on_time", "mean")).to_csv(output / f"operational_metrics_{period}.csv", index=False)
    rfm_path = EXPORT_DIR / "rfm_segments.csv"
    if rfm_path.exists():
        pd.read_csv(rfm_path).groupby("segment", as_index=False).agg(customers=("customer_unique_id", "nunique"), historical_gmv=("monetary", "sum"), average_orders=("frequency", "mean")).to_csv(output / f"customer_segments_{period}.csv", index=False)
    cohort_path = EXPORT_DIR / "cohort_retention.csv"
    if cohort_path.exists():
        pd.read_csv(cohort_path).to_csv(output / f"cohort_retention_{period}.csv", index=False)
    quality_path = EXPORT_DIR / "data_quality.csv"
    if quality_path.exists():
        pd.read_csv(quality_path).to_csv(output / f"data_quality_{period}.csv", index=False)

    monthly = delivered.assign(month=delivered.order_purchase_timestamp.dt.to_period("M").astype(str)).groupby("month").merchandise_gmv.sum()
    operations = mart.groupby("customer_state", as_index=False).agg(
        orders=("order_id", "nunique"), average_delivery_days=("delivery_days", "mean"), on_time_delivery_rate=("on_time", "mean")
    )
    reporting_period = "n/a" if mart.empty else f"{mart.order_purchase_timestamp.min():%Y-%m-%d} to {mart.order_purchase_timestamp.max():%Y-%m-%d}"
    pdf_path = output / f"commerce_lens_report_{period}.pdf"; pdf = canvas.Canvas(str(pdf_path), pagesize=letter)
    pdf.setTitle("CommerceLens Monthly Report"); y = 750
    leading_category = delivered.groupby("category").merchandise_gmv.sum().sort_values(ascending=False)
    sales_trend = "n/a" if len(monthly) < 2 else f"{(monthly.iloc[-1] / monthly.iloc[-2] - 1):.1%} month-over-month"
    best_state = operations.sort_values("on_time_delivery_rate", ascending=False).iloc[0] if not operations.empty else None
    for line in [
        "CommerceLens — Executive Sales Report",
        f"Reporting period: {reporting_period}",
        f"Generated: {datetime.now():%Y-%m-%d}",
        "",
        "KPI summary",
        f"Completed Merchandise GMV: {metrics['merchandise_gmv']:,.2f}",
        f"Delivered Orders: {metrics['delivered_orders']:,}",
        f"Average Order Value: {metrics['aov']:,.2f}",
        f"Repeat Purchase Rate: {metrics['repeat_purchase_rate']:.1f}%",
        f"On-time Delivery Rate: {metrics['on_time_delivery_rate']:.1f}%",
        "",
        "Sales trend and customer finding",
        f"Latest observed monthly GMV change: {sales_trend}",
        f"Leading category: {leading_category.index[0] if len(leading_category) else 'n/a'}",
        "RFM/customer and cohort exports are included when the ETL artifacts are available.",
        "",
        "Operations finding and recommendation",
        f"Best on-time state: {best_state.customer_state if best_state is not None else 'n/a'}",
        "Protect availability in leading categories and investigate late-delivery patterns by state.",
        "",
        "Assumptions and limitations",
        "GMV excludes freight and is not profit. Results use observed Olist transactions.",
    ]:
        pdf.drawString(54, y, line); y -= 28
    pdf.save(); return csv_path, pdf_path
