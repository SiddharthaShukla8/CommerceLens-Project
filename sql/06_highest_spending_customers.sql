-- Highest-spending historical customers.
SELECT customer_unique_id, SUM(merchandise_gmv) gmv FROM analytics.v_order_value WHERE order_status='delivered' GROUP BY 1 ORDER BY 2 DESC LIMIT 20;
