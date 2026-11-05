-- Cancellation trend by purchase month.
SELECT date_trunc('month',order_purchase_timestamp)::date month,COUNT(*) FILTER(WHERE order_status='canceled') cancellations,COUNT(*) total_orders FROM analytics.fact_orders GROUP BY 1 ORDER BY 1;
