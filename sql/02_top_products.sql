-- Top ten products by delivered merchandise GMV.
SELECT i.product_id, SUM(i.price) gmv FROM analytics.fact_order_items i JOIN analytics.fact_orders o USING(order_id) WHERE o.order_status='delivered' GROUP BY 1 ORDER BY 2 DESC LIMIT 10;
