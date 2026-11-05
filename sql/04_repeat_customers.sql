-- Customers with more than one delivered order.
SELECT customer_unique_id, COUNT(*) delivered_orders FROM analytics.v_order_value WHERE order_status='delivered' GROUP BY 1 HAVING COUNT(*) > 1 ORDER BY 2 DESC;
