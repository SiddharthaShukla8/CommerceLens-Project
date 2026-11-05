CREATE OR REPLACE VIEW analytics.v_order_value AS
SELECT o.order_id, o.customer_id, o.order_status, o.order_purchase_timestamp, o.order_delivered_customer_date,
       o.order_estimated_delivery_date, c.customer_unique_id, c.customer_state,
       SUM(i.price) AS merchandise_gmv, SUM(i.freight_value) AS freight_value,
       SUM(i.price + i.freight_value) AS order_value
FROM staging.orders o
JOIN staging.customers c ON c.customer_id = o.customer_id
JOIN staging.order_items i ON i.order_id = o.order_id
GROUP BY 1,2,3,4,5,6,7,8;
