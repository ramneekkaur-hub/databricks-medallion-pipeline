# Requirements Analysis

## 1. Problem Statement

The project will build an end-to-end batch data pipeline for an e-commerce company using Databricks Medallion Architecture.

The pipeline will ingest customer, product, and order CSV files into the Bronze layer, validate and clean the data in the Silver layer, and create business-ready analytics in the Gold layer.

The pipeline must identify and retain data quality issues rather than silently deleting them. Invalid records will be flagged in the Silver layer with one or more failure reasons. Only valid Silver records will be used for Gold analytics.

---

## 2. Functional Requirements

### 2.1 Source Data

The pipeline will process three CSV datasets.

#### Customers

Expected volume: approximately 10,000 rows.

Fields:

- `customer_id`
- `customer_name`
- `email`
- `country`
- `signup_date`
- `customer_segment`
- `lifetime_value`

#### Orders

Expected volume: approximately 100,000 rows.

Fields:

- `order_id`
- `customer_id`
- `order_date`
- `product_id`
- `quantity`
- `unit_price`
- `total_amount`
- `order_status`
- `payment_date`

Each row represents one complete order.

`order_id` must be unique.

#### Products

Expected volume: approximately 500 rows.

Fields:

- `product_id`
- `product_name`
- `category`
- `price`
- `cost`
- `stock_quantity`
- `reorder_level`

---

## 3. Data Generation Requirements

The project must:

- Generate customers, orders, and products CSV files.
- Generate approximately 10,000 customers.
- Generate approximately 100,000 orders.
- Generate approximately 500 products.
- Use synthetic data only.
- Introduce intentional data quality issues.
- Document the injected issues and expected detection results.
- Use reproducible data generation using a fixed random seed where practical.
- Validate generated row counts before ingestion.

The generated data must include the following intentional issues.

### Customers

- 50 rows with NULL email.
- 10 duplicate `customer_id` records.

### Orders

- 100 rows with NULL `customer_id`.
- 200 rows with NULL `product_id`.
- 50 rows with a `customer_id` that does not exist in customers.
- 30 rows with a `product_id` that does not exist in products.
- 20 duplicate `order_id` records.

Additional invalid records may be generated to test type validation and business rules, provided they are documented.

---

## 4. Bronze Layer Requirements

The Bronze layer must:

- Read the raw CSV files.
- Create separate Delta tables for customers, orders, and products.
- Preserve the source data with minimal transformation.
- Retain invalid source records.
- Add ingestion metadata to every record.
- Record the ingestion timestamp.
- Record the source file name.
- Record a pipeline/batch identifier where practical.
- Validate that Bronze row counts match the source files.
- Use overwrite mode for this learning assignment so reruns are reproducible.
- Avoid unexplained duplicate records caused by pipeline reruns.

Bronze tables:

- `bronze_customers`
- `bronze_orders`
- `bronze_products`

No business cleaning or filtering should be performed in Bronze.

---

## 5. Silver Layer Requirements

The Silver layer must:

- Convert fields to their expected data types.
- Validate data quality.
- Retain both valid and invalid records.
- Never silently delete invalid records.
- Flag invalid records.
- Store one or more failure reasons for invalid records.
- Generate data quality metrics.

Every Silver table must contain:

- `quality_check_result`
- `quality_failure_reason`

`quality_check_result` will use:

- `PASS`
- `FAIL`

Multiple failure reasons will be stored as a pipe-separated string.

