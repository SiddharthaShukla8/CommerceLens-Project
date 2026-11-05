-- Repeat purchase rate calculated at unique customer grain.
WITH customer_orders AS (SELECT customer_unique_id, COUNT(*) orders FROM analytics.v_order_value WHERE order_status='delivered' GROUP BY 1) SELECT 100.0 * COUNT(*) FILTER (WHERE orders >= 2) / NULLIF(COUNT(*),0) AS repeat_rate_pct FROM customer_orders;
