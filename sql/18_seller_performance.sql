-- Seller GMV and fulfilled-item volume.
SELECT s.seller_id,s.seller_state,SUM(i.price) gmv,COUNT(*) items FROM analytics.fact_order_items i JOIN analytics.fact_orders o USING(order_id) JOIN analytics.dim_sellers s USING(seller_id) WHERE o.order_status='delivered' GROUP BY 1,2 ORDER BY gmv DESC LIMIT 25;
