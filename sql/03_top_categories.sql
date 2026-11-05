-- Top ten categories by delivered merchandise GMV.
SELECT p.product_category_name_english category, SUM(i.price) gmv FROM analytics.fact_order_items i JOIN analytics.fact_orders o USING(order_id) JOIN analytics.dim_products p USING(product_id) WHERE o.order_status='delivered' GROUP BY 1 ORDER BY 2 DESC LIMIT 10;
