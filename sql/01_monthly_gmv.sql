-- Business question: What are monthly delivered GMV and orders?
SELECT date_trunc('month', order_purchase_timestamp)::date AS month, SUM(merchandise_gmv) AS gmv, COUNT(*) AS orders FROM analytics.v_order_value WHERE order_status='delivered' GROUP BY 1 ORDER BY 1;
