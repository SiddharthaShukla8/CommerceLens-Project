-- Delivered orders that arrived late.
SELECT order_id,order_purchase_timestamp,order_estimated_delivery_date,order_delivered_customer_date,(order_delivered_customer_date::date-order_estimated_delivery_date::date) delayed_days FROM analytics.fact_orders WHERE order_status='delivered' AND order_delivered_customer_date>order_estimated_delivery_date ORDER BY delayed_days DESC;
