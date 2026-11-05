-- Customer purchase frequency ranking.
SELECT customer_unique_id, COUNT(*) orders, DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) frequency_rank FROM analytics.v_order_value WHERE order_status='delivered' GROUP BY 1 ORDER BY frequency_rank;
