# Portfolio readiness

## Resume bullets

- Built CommerceLens, a Python, PostgreSQL, Pandas, and Streamlit e-commerce intelligence platform with a repeatable Olist ETL pipeline, data-quality validation, and business-safe GMV reporting.
- Implemented 20 PostgreSQL business analyses plus RFM segmentation, customer cohort retention, operational delivery metrics, and a rule-based recommendation engine.
- Delivered a seven-section interactive dashboard and reproducible synthetic A/B-test analysis using confidence intervals and two-proportion hypothesis testing, clearly separated from observed transaction data.

## Recruiter walkthrough

Start with the README, then open the executive dashboard. Explain one metric end-to-end: delivered item price enters the immutable CSV source, is cleaned and validated, is aggregated to order grain to avoid payment/item multiplication, becomes a shared Python KPI and PostgreSQL view, and is displayed as completed merchandise GMV. Note that it is not profit and that the experiment page uses simulated data only.
