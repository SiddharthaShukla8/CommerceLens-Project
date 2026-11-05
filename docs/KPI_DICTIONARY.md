# KPI dictionary

| KPI | Definition |
|---|---|
| Completed merchandise GMV | Sum of `price` for delivered order items. It excludes freight and is not profit. |
| Delivered orders | Distinct orders with `order_status = delivered`. |
| AOV | Completed merchandise GMV / delivered orders. |
| Repeat purchase rate | Unique customers with at least two delivered orders / customers with at least one delivered order. Uses `customer_unique_id`. |
| On-time delivery rate | Delivered orders where actual delivery was on/before estimated delivery, among records having both dates. |

All dashboard and PDF values use `src.analytics.mart.kpis`. PostgreSQL order-level sales analysis uses `analytics.v_order_value`, which aggregates `fact_order_items` before combining order attributes. The denominator for on-time delivery excludes missing actual/estimated delivery dates; repeat rate excludes customers without a delivered order.
