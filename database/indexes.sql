CREATE INDEX IF NOT EXISTS idx_orders_purchase ON staging.orders(order_purchase_timestamp);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON staging.orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_items_product ON staging.order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_items_seller ON staging.order_items(seller_id);
CREATE INDEX IF NOT EXISTS idx_customers_state ON staging.customers(customer_state);
