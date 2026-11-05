-- Cancellation trend by purchase month.
SELECT date_trunc('month',order_purchase_timestamp)::date AS month_start,COUNT(*) FILTER(WHERE order_status='canceled') AS cancellations,COUNT(*) AS total_orders FROM analytics.fact_orders GROUP BY 1 ORDER BY 1;
