# Database design

CommerceLens uses PostgreSQL schemas `staging` and `analytics`. The source CSVs are never loaded into Git or modified in place.

| Table | Grain | Key |
|---|---|---|
| `staging.customers` / `analytics.dim_customers` | one Olist customer record | `customer_id` |
| `staging.products` / `analytics.dim_products` | one product | `product_id` |
| `staging.sellers` / `analytics.dim_sellers` | one seller | `seller_id` |
| `analytics.dim_date` | one calendar date | `date_key` |
| `analytics.fact_orders` | one order | `order_id` |
| `analytics.fact_order_items` | one order item | `order_id`, `order_item_id` |
| `analytics.fact_payments` | one payment transaction | `order_id`, `payment_sequential` |
| `analytics.fact_reviews` | one review source row | no assumed unique review ID |

`analytics.v_order_value` first aggregates items to order grain. It must be used rather than joining payments and items directly, because their many-to-one relationship can multiply revenue. Indexes cover common order date/customer, item product/seller, payment-order, and review-order access paths.

## Migrations and recovery

`src.database.schema_manager` applies additive files from `database/migrations/` and records versions in `analytics.schema_migrations`; it does not reset the Docker volume. Back up a local database with `docker compose exec -T postgres pg_dump -U commercelens commercelens > backup.sql`, then restore with `psql` against a freshly provisioned database. Keep backups outside Git.
