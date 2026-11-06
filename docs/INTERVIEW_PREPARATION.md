# CommerceLens interview preparation

## Project explanations

### 30 seconds

CommerceLens is an end-to-end e-commerce intelligence portfolio project built on Olist's public relational dataset. I created a repeatable Pandas-to-PostgreSQL pipeline, defined business-safe GMV metrics, and built a Streamlit dashboard for sales, products, customer RFM, cohorts, delivery performance, and a clearly labelled synthetic A/B-test demonstration.

### 1 minute

The project starts with nine immutable Olist CSV sources. Python profiles, cleans, and validates them, then loads staging and analytics tables in PostgreSQL. I modelled orders, order items, payments, and reviews at their natural grains. That is important because joining payments and items directly can multiply money values. For order-level KPIs I aggregate items first; for product drill-down I use a separate item-grain mart. The Streamlit dashboard uses PostgreSQL when local exports are absent, so it can run in a cloud environment with only a database URL. I validated the delivered GMV, delivered orders, AOV, and unique-customer metrics between Python and PostgreSQL.

### 3 minute technical explanation

Raw data remains outside Git. The ETL reader checks all nine required files, the cleaner parses dates and records an audit, and validation checks keys, relationships, financial values, and known missingness. The loader performs a transactional controlled replacement and applies additive tracked migrations; a local lock prevents concurrent pipeline runs. PostgreSQL holds staging tables, customer/product/seller/date dimensions, and order/item/payment/review facts. `fact_orders` is one row per order and `fact_order_items` is one row per item.

For analytics, `kpis()` is the single Python definition used by dashboard and reports. Delivered merchandise GMV is the sum of item `price` for delivered orders; it excludes freight and is not profit. AOV divides that GMV by distinct delivered orders. Customer identity uses `customer_unique_id`, not the one-order `customer_id`. RFM scores recency, frequency, and historical delivered merchandise value with quantiles. Cohorts use a customer's first delivered-purchase month. The project includes 20 executable PostgreSQL analyses demonstrating joins, CTEs, aggregation, `HAVING`, `LAG`, `DENSE_RANK`, running totals, and rolling averages. The experiment page never presents synthetic conversion as Olist business performance.

### 5 minute walkthrough

1. Open the Executive Overview and state the metric definitions before discussing values.
2. Show the date/state/order-status filters; explain that they recalculate the order population, not only chart appearance.
3. Open Sales & Products. Select a category and product to show the item-grain drill-down, daily/weekly charts, and downloadable table.
4. Open Customer Intelligence. Select an RFM segment and explain customer count, historical spend, frequency, cohort heatmap, and the evidence-based action.
5. Open Operations and Geography. Discuss delivery eligibility, on-time denominator, late orders, seller performance, and state-level aggregation rather than false coordinate precision.
6. Open Experiment Analytics and point out the simulated-data banner, control/treatment conversion, confidence interval, p-value, and interpretation.
7. End with Data Quality/Pipeline Monitoring, SQL validation, automated tests, Docker, and the managed-PostgreSQL deployment path.

## Technical talking points

| Topic | Explain it using this project |
|---|---|
| PostgreSQL / warehouse | Staging captures cleaned source-shaped data; analytics holds dimensions and facts; migrations are additive. |
| SQL joins and CTEs | Query files avoid item/payment fanout and use CTEs/window functions for cohort, growth, rank, and rolling metrics. |
| Query performance | Indexes cover purchase date, customer, item product/seller, payment order, and review order; measure with `EXPLAIN ANALYZE` before claiming gains. |
| Pandas / NumPy | Pandas handles parsing, joins, grouping, exports, and validation; NumPy represents conditional on-time eligibility safely. |
| Cleaning and EDA | Keep raw sources immutable; flag missingness and invalid financial values rather than blindly dropping records. |
| RFM / cohorts | RFM uses delivered orders and `customer_unique_id`; cohorts use first delivered-purchase month and do not treat future unobserved months as zero. |
| A/B testing | Uses seeded synthetic assignment because Olist has no exposure or randomization data; report two-proportion p-value and CI. |
| Dashboard / reporting | Streamlit consumes exports or database fallback; reports are generated from actual mart data as PDF and CSV artifacts. |

## Business metric definitions

- **GMV:** delivered item price only; it is neither profit nor payment total.
- **AOV:** delivered merchandise GMV divided by distinct delivered orders.
- **Repeat purchase rate:** customers with at least two delivered orders divided by customers with at least one delivered order.
- **Retention:** activity in later months for customers grouped by their first delivered-purchase month.
- **Historical customer spend:** observed delivered merchandise value, not a predictive customer lifetime value model.
- **Delivery metrics:** on-time rate excludes orders lacking either actual or estimated delivery date; cancellation rate uses the selected-order denominator.

## Realistic interview questions

1. Why did you not join payments directly to order items?
   They have different detail grains and would multiply financial values for multi-item or multi-payment orders.
2. How do filters remain trustworthy?
   Shared filters narrow the order population; product/category analysis uses an item-grain mart, while order KPIs stay order-grain.
3. How would you deploy it?
   Provision managed PostgreSQL, run migrations/ETL with a writer URL, configure a least-privilege reader URL as a Streamlit secret, then smoke test the public app.
4. What could you improve with more time?
   Add provider-backed monitoring, scheduled reports only after configuring a scheduler, and measured query-plan tuning on production-scale usage.
