CREATE TABLE IF NOT EXISTS analytics.schema_migrations (
  version TEXT PRIMARY KEY,
  applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS analytics.dim_date (
  date_key DATE PRIMARY KEY,
  calendar_year SMALLINT NOT NULL,
  calendar_quarter SMALLINT NOT NULL,
  calendar_month SMALLINT NOT NULL,
  month_name TEXT NOT NULL,
  week_of_year SMALLINT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_fact_orders_purchase ON analytics.fact_orders(order_purchase_timestamp);
CREATE INDEX IF NOT EXISTS idx_fact_orders_customer ON analytics.fact_orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_fact_items_product ON analytics.fact_order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_fact_items_seller ON analytics.fact_order_items(seller_id);
CREATE INDEX IF NOT EXISTS idx_fact_payments_order ON analytics.fact_payments(order_id);
CREATE INDEX IF NOT EXISTS idx_fact_reviews_order ON analytics.fact_reviews(order_id);
