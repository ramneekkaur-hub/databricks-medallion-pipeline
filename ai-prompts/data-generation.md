# AI Prompts — Data Generation

## Prompt 1: Initial Sample Data Generator

**PROMPT SENT:**

I need to build the sample data generation component for a Databricks Medallion Architecture e-commerce pipeline.

The assignment requires three CSV files:
- customers.csv — 10,000 rows
- products.csv — 500 rows
- orders.csv — 100,000 rows

The data should be realistic and reproducible using Python.

Customers should contain:
customer_id, customer_name, email, country, signup_date, customer_segment, lifetime_value.

Products should contain:
product_id, product_name, category, price, cost, stock_quantity, reorder_level.

Orders should contain:
order_id, customer_id, order_date, product_id, quantity, unit_price, total_amount, order_status, payment_date.

The generated data must include the intentional data-quality issues specified in the assignment, including NULLs, duplicate IDs, invalid values and referential-integrity failures.

Use a fixed random seed so the dataset is reproducible.

Please generate a clean, maintainable Python script using only appropriate standard-library functionality where possible. Include comments explaining the intentional quality issues.

**AI RESPONSE / APPROACH:**

Cursor generated a Python sample-data generation script using deterministic random generation and helper functions for dates and monetary values.

**WHAT I ACCEPTED:**

I accepted the overall approach because it produced all three required CSV datasets, used a fixed random seed, generated the required row counts and intentionally introduced data-quality issues.

**WHAT I VALIDATED:**

I ran the generated script using:

python3 src/data_generation/generate_sample_data.py

The script successfully generated:
- customers.csv — 10,000 data rows
- products.csv — 500 data rows
- orders.csv — 100,000 data rows

I additionally validated the CSV line counts using wc -l.

The resulting counts were:
- customers.csv — 10,001 lines including the header
- products.csv — 501 lines including the header
- orders.csv — 100,001 lines including the header

**FINAL DECISION:**

Accepted after local execution and row-count validation.