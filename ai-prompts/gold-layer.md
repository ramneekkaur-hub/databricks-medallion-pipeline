# AI Prompts — Gold Layer

## Purpose

This document records the use of AI during the design, implementation, validation, and debugging of the Gold layer of the e-commerce Medallion Architecture project.

The Gold layer is responsible for transforming validated Silver-layer data into business-ready datasets for analytics and dashboard reporting.

The required Gold outputs are:

1. Sales by Product
2. Revenue by Customer
3. Daily/Weekly Sales Trends
4. Customer Segmentation

AI was used as an assistant throughout the lifecycle rather than only for generating code. I used AI to understand requirements, design transformations, generate and review SQL/PySpark code, identify potential data-quality and aggregation issues, suggest validation approaches, and help debug problems.

All AI-generated suggestions were reviewed and tested before being accepted.

---

# 1. Gold Layer Requirements Analysis

## Prompt 1 — Understand the Gold Layer Requirements

### PROMPT SENT

I am building an e-commerce data pipeline using Databricks and a Medallion Architecture.

The pipeline has:

- Bronze layer for raw ingestion
- Silver layer for data quality validation and cleaning
- Gold layer for business-ready analytics
- Dashboard layer for business reporting

The Gold layer needs to create the following outputs:

1. Sales by Product
   - product_id
   - product_name
   - category
   - total_orders
   - total_revenue
   - avg_order_value

2. Revenue by Customer
   - customer_id
   - customer_name
   - customer_segment
   - total_orders
   - total_revenue
   - avg_order_value
   - lifetime_value_actual

3. Daily/Weekly Sales Trends
   - date
   - order count
   - total revenue
   - average order value
   - daily and weekly reporting

4. Customer Segmentation
   - High-Value
   - Repeat
   - One-Time
   - Inactive

Help me break these requirements into appropriate Gold tables and explain the expected grain, joins, aggregations, and business logic.

Do not overcomplicate the solution.

---

## AI RESPONSE SUMMARY

AI recommended creating separate Gold datasets for each business use case rather than combining all analytical requirements into one large table.

The recommended approach was:

- Use validated Silver orders as the main source for sales metrics.
- Join orders to products for product-level reporting.
- Join orders to customers for customer-level reporting.
- Aggregate order information according to the required business grain.
- Use revenue and order activity to support customer segmentation.
- Create separate daily and weekly aggregations for trend reporting.

AI also highlighted that the Gold layer should consume validated Silver data rather than directly using raw Bronze data.

---

## MY EVALUATION

### Accepted

I accepted the recommendation to separate the Gold layer into multiple business-focused outputs.

This makes each table easier to understand and maintain.

I also accepted the recommendation that Gold transformations should be based on Silver data because the Silver layer is responsible for data-quality validation.

### Important consideration

The exact treatment of invalid records needed to be aligned with the Silver-layer design.

The Gold layer should not silently hide data-quality problems. Instead, it should use the agreed valid records while the Silver layer retains quality information and reporting.

### Rejected

I rejected the idea of creating one very large Gold table containing product, customer, trend, and segmentation information.

This would make the dataset harder to maintain and would increase the risk of incorrect joins and duplicated measures.

---

# 2. Sales by Product

## Prompt 2 — Design Sales by Product Aggregation

### PROMPT SENT

Create a Databricks SQL transformation for a Gold Sales by Product table.

The required columns are:

- product_id
- product_name
- category
- total_orders
- total_revenue
- avg_order_value

Orders contain:

- order_id
- customer_id
- product_id
- order_date
- quantity
- unit_price
- total_amount
- order_status

Products contain:

- product_id
- product_name
- category
- price
- cost
- stock_quantity
- reorder_level

Join orders to products using product_id.

The output should contain one row per product.

Calculate:

- total_orders
- total_revenue
- avg_order_value

Use appropriate handling for duplicate order records and invalid data.

Explain the logic before providing the SQL.

---

## AI RESPONSE SUMMARY

AI recommended:

- Joining orders to products using `product_id`.
- Grouping by product attributes.
- Counting orders using `order_id`.
- Summing `total_amount` for revenue.
- Calculating average order value from revenue and order count.
- Considering duplicate order IDs to avoid inflated metrics.
- Filtering records according to the agreed valid/completed order definition.

---

## MY EVALUATION

### Accepted

The expected grain was clearly defined as:

```text
One row per product