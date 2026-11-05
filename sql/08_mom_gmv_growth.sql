-- Month-over-month GMV using LAG.
WITH m AS (SELECT date_trunc('month',order_purchase_timestamp)::date AS month_start,SUM(merchandise_gmv) AS gmv FROM analytics.v_order_value WHERE order_status='delivered' GROUP BY 1) SELECT *, 100*(gmv-LAG(gmv) OVER(ORDER BY month_start))/NULLIF(LAG(gmv) OVER(ORDER BY month_start),0) AS mom_growth_pct FROM m ORDER BY month_start;
