-- Running monthly GMV.
WITH m AS (SELECT date_trunc('month',order_purchase_timestamp)::date month,SUM(merchandise_gmv) gmv FROM analytics.v_order_value WHERE order_status='delivered' GROUP BY 1) SELECT month,gmv,SUM(gmv) OVER(ORDER BY month) running_gmv FROM m;
