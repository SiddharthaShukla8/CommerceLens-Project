# SQL validation report

Validated against the local `commercelens` PostgreSQL database on 2026-11-06. All queries were executed independently to avoid one failed transaction masking later results. `month` aliases in seven files were corrected to `month_start`, because `month` is not accepted as an unquoted alias by the configured PostgreSQL parser.

| Query | Business question / concepts | Rows | Duration | Status |
|---|---|---:|---:|---|
| 01_monthly_gmv.sql | Monthly GMV and orders; aggregation/date | 23 | 363 ms | PASS |
| 02_top_products.sql | Top products; joins/aggregation | 10 | 142 ms | PASS |
| 03_top_categories.sql | Top categories; joins/aggregation | 10 | 94 ms | PASS |
| 04_repeat_customers.sql | Repeat customers; HAVING | 2,801 | 318 ms | PASS |
| 05_repeat_rate.sql | Repeat-rate KPI; CTE/FILTER | 1 | 287 ms | PASS |
| 06_highest_spending_customers.sql | Customer spend ranking | 20 | 369 ms | PASS |
| 07_customer_frequency.sql | Frequency ranking; DENSE_RANK | 93,358 | 384 ms | PASS |
| 08_mom_gmv_growth.sql | MoM GMV; CTE/LAG | 23 | 266 ms | PASS |
| 09_monthly_category_growth.sql | Category growth; partitioned LAG | 1,264 | 123 ms | PASS |
| 10_top_products_by_category.sql | Product rank; CTE/DENSE_RANK | 355 | 305 ms | PASS |
| 11_first_purchase.sql | First purchase; MIN | 93,358 | 299 ms | PASS |
| 12_new_vs_returning.sql | New/returning orders; window/FILTER | 23 | 382 ms | PASS |
| 13_cohort_retention.sql | Cohorts; CTE/window | 219 | 490 ms | PASS |
| 14_cancellations.sql | Cancellation trend; FILTER/date | 25 | 61 ms | PASS |
| 15_delayed_deliveries.sql | Late deliveries; date arithmetic | 7,826 | 51 ms | PASS |
| 16_state_delivery.sql | State delivery performance; joins/average | 27 | 214 ms | PASS |
| 17_category_reviews.sql | Category review performance; joins | 72 | 134 ms | PASS |
| 18_seller_performance.sql | Seller GMV; joins/ranking | 25 | 87 ms | PASS |
| 19_running_gmv.sql | Running GMV; window sum | 23 | 258 ms | PASS |
| 20_rolling_gmv.sql | Three-month moving average; window frame | 23 | 271 ms | PASS |

All sales queries use delivered item values or the order-grain `analytics.v_order_value` view, rather than joining payments directly to items. Payment value remains a separate fact grain.
