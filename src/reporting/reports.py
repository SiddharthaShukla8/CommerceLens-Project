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
    csv_path = output / f"monthly_sales_{period}.csv"; mart[mart.order_status.eq("delivered")].to_csv(csv_path, index=False)
    pdf_path = output / f"commerce_lens_report_{period}.pdf"; pdf = canvas.Canvas(str(pdf_path), pagesize=letter)
    pdf.setTitle("CommerceLens Monthly Report"); y = 750
    for line in ["CommerceLens — Monthly Analytics Report", f"Generated: {datetime.now():%Y-%m-%d}", "", f"Completed Merchandise GMV: {metrics['merchandise_gmv']:,.2f}", f"Delivered Orders: {metrics['delivered_orders']:,}", f"Average Order Value: {metrics['aov']:,.2f}", f"Repeat Purchase Rate: {metrics['repeat_purchase_rate']:.1f}%", f"On-time Delivery Rate: {metrics['on_time_delivery_rate']:.1f}%", "", "Notes: GMV excludes freight and is not profit. Results are sourced from processed Olist data."]:
        pdf.drawString(54, y, line); y -= 28
    pdf.save(); return csv_path, pdf_path
