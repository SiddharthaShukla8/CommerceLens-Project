CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS staging.customers (
  customer_id TEXT PRIMARY KEY, customer_unique_id TEXT NOT NULL, customer_zip_code_prefix INTEGER,
  customer_city TEXT, customer_state TEXT
);
CREATE TABLE IF NOT EXISTS staging.orders (
  order_id TEXT PRIMARY KEY, customer_id TEXT REFERENCES staging.customers(customer_id), order_status TEXT,
  order_purchase_timestamp TIMESTAMP, order_approved_at TIMESTAMP, order_delivered_carrier_date TIMESTAMP,
  order_delivered_customer_date TIMESTAMP, order_estimated_delivery_date TIMESTAMP
);
CREATE TABLE IF NOT EXISTS staging.order_items (
  order_id TEXT REFERENCES staging.orders(order_id), order_item_id INTEGER, product_id TEXT, seller_id TEXT,
  shipping_limit_date TIMESTAMP, price NUMERIC, freight_value NUMERIC, PRIMARY KEY(order_id, order_item_id)
);
CREATE TABLE IF NOT EXISTS staging.payments (
  order_id TEXT REFERENCES staging.orders(order_id), payment_sequential INTEGER, payment_type TEXT,
  payment_installments INTEGER, payment_value NUMERIC, PRIMARY KEY(order_id, payment_sequential)
);
CREATE TABLE IF NOT EXISTS staging.products (product_id TEXT PRIMARY KEY, product_category_name TEXT, product_category_name_english TEXT);
CREATE TABLE IF NOT EXISTS staging.sellers (seller_id TEXT PRIMARY KEY, seller_zip_code_prefix INTEGER, seller_city TEXT, seller_state TEXT);
CREATE TABLE IF NOT EXISTS staging.reviews (review_id TEXT, order_id TEXT REFERENCES staging.orders(order_id), review_score INTEGER, review_comment_title TEXT, review_comment_message TEXT, review_creation_date TIMESTAMP, review_answer_timestamp TIMESTAMP);

CREATE TABLE IF NOT EXISTS analytics.dim_customers AS SELECT * FROM staging.customers WITH NO DATA;
CREATE TABLE IF NOT EXISTS analytics.dim_products AS SELECT * FROM staging.products WITH NO DATA;
CREATE TABLE IF NOT EXISTS analytics.dim_sellers AS SELECT * FROM staging.sellers WITH NO DATA;
CREATE TABLE IF NOT EXISTS analytics.fact_orders AS SELECT * FROM staging.orders WITH NO DATA;
CREATE TABLE IF NOT EXISTS analytics.fact_order_items AS SELECT * FROM staging.order_items WITH NO DATA;
CREATE TABLE IF NOT EXISTS analytics.fact_payments AS SELECT * FROM staging.payments WITH NO DATA;
CREATE TABLE IF NOT EXISTS analytics.fact_reviews AS SELECT * FROM staging.reviews WITH NO DATA;
