# Power BI readiness

Connect Power BI to PostgreSQL using the PostgreSQL connector and the credentials in `.env`. Import `analytics.dim_customers`, `dim_products`, `dim_sellers`, `fact_orders`, `fact_order_items`, and `analytics.v_order_value`.

Use one-to-many relationships from dimensions to facts. Do not relate payments directly to items: their grains differ and would inflate metrics. Build measures from `fact_order_items` filtered to delivered orders, or use `v_order_value` at order grain.
