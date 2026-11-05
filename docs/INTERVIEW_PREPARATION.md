# Interview preparation

## 30-second introduction
CommerceLens is a portfolio e-commerce intelligence platform built on Olist's public relational dataset. I engineered a repeatable Pandas-to-PostgreSQL pipeline, defined business-safe GMV metrics, and delivered a Streamlit dashboard with customer RFM, cohorts, delivery performance, SQL analysis, and reproducible experiment statistics.

## Technical walkthrough
Raw CSV files stay immutable in `data/raw`. The pipeline profiles and cleans them with an audit trail, validates keys and financial values, exports cleaned tables and order-grain analytics, then can load staging and analytics schemas in PostgreSQL. I avoid revenue multiplication by aggregating items before joining order-level fields. RFM uses `customer_unique_id`, delivered orders, and the maximum observed purchase date. The A/B test is explicitly seeded synthetic data because Olist has no randomized exposure data.

## Interview Q&A

- **Why PostgreSQL?** It supports relational integrity, CTEs, window functions, views, and Power BI connectivity.
- **How did you prevent double counting?** GMV comes from order items; payments remain a separate fact grain and are never joined directly to items.
- **How is repeat rate calculated?** Delivered customers with two or more distinct orders divided by all customers with delivered orders.
- **How are missing values handled?** The cleaner records the affected count and applies a purpose-specific treatment, such as retaining unknown categories rather than dropping history.
- **Why is the experiment synthetic?** Olist does not supply randomized assignments or exposure records, so interpreting transactions as conversion would be invalid.

## Resume bullets

- Built CommerceLens, an end-to-end Python, PostgreSQL, Streamlit, and Plotly e-commerce analytics platform with automated ETL, quality validation, and PDF/CSV reporting.
- Implemented business-safe order-grain GMV metrics, RFM segmentation, cohort retention, delivery analysis, and 20 PostgreSQL analytical queries.
- Developed a reproducible synthetic A/B-test module with confidence intervals and two-proportion hypothesis testing, clearly separated from observed transactional data.
