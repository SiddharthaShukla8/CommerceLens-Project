-- Rolling three-month average GMV.
WITH m AS (SELECT date_trunc('month',order_purchase_timestamp)::date AS month_start,SUM(merchandise_gmv) AS gmv FROM analytics.v_order_value WHERE order_status='delivered' GROUP BY 1) SELECT month_start,gmv,AVG(gmv) OVER(ORDER BY month_start ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling_3_month_gmv FROM m;
