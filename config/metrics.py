"""Centralized metric definitions used by dashboard, reports, and tests."""
METRIC_DEFINITIONS = {
    "merchandise_gmv": "Sum of item price for delivered orders; excludes freight and is not profit.",
    "delivered_orders": "Distinct orders with status delivered.",
    "aov": "Completed merchandise GMV divided by distinct delivered orders.",
    "repeat_purchase_rate": "Unique customers with >=2 delivered orders divided by those with >=1.",
    "on_time_delivery_rate": "Delivered orders with actual delivery on or before estimate divided by delivered orders with both dates.",
}
