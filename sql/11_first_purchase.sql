-- First delivered purchase date per customer.
SELECT customer_unique_id, MIN(order_purchase_timestamp)::date first_purchase_date FROM analytics.v_order_value WHERE order_status='delivered' GROUP BY 1;
