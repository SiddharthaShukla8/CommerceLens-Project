-- Average review score by product category.
SELECT p.product_category_name_english category,AVG(r.review_score) avg_review_score,COUNT(*) reviews FROM analytics.fact_reviews r JOIN analytics.fact_order_items i USING(order_id) JOIN analytics.dim_products p USING(product_id) GROUP BY 1 ORDER BY 2;
