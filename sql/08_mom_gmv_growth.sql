-- Month-over-month GMV using LAG.
WITH m AS (SELECT date_trunc('month',order_purchase_timestamp)::date month,SUM(merchandise_gmv) gmv FROM analytics.v_order_value WHERE order_status='delivered' GROUP BY 1) SELECT *, 100*(gmv-LAG(gmv) OVER(ORDER BY month))/NULLIF(LAG(gmv) OVER(ORDER BY month),0) mom_growth_pct FROM m ORDER BY month;
