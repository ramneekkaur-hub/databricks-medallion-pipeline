# Project Context

## Project Name

Databricks Medallion Architecture E-Commerce Pipeline

## Objective

Build an end-to-end data pipeline for an e-commerce company using the Medallion Architecture.

The pipeline will process data through:

1. Bronze Layer
2. Silver Layer
3. Gold Layer
4. Dashboard

## Source Data

The project contains three source datasets:

### Customers

Fields:

* customer_id
* customer_name
* email
* country
* signup_date
* customer_segment
* lifetime_value

Expected volume: approximately 10,000 rows.

### Orders

Fields:

* order_id
* customer_id
* order_date
* product_id
* quantity
* unit_price
* total_amount
* order_status
* payment_date

Expected volume: approximately 100,000 rows.

### Products

Fields:

* product_id
* product_name
* category
* price
* cost
* stock_quantity
* reorder_level

Expected volume: approximately 500 rows.

## Bronze Layer

The Bronze layer will:

* Read raw CSV files.
* Preserve source data.
* Perform minimal transformation.
* Store data in Delta tables.
* Record ingestion metadata.

## Silver Layer

The Silver layer will perform data quality validation.

Required checks:

1. Completeness
2. Uniqueness
3. Referential Integrity
4. Type Validation and Business Logic Validation

Invalid records should be flagged rather than silently deleted.

## Gold Layer

The Gold layer will create business-ready aggregations.

Required outputs:

1. Sales by Product
2. Revenue by Customer
3. Customer Segmentation

An additional Daily or Weekly Sales Trends table may also be created.

## Dashboard

The project will contain at least three visualizations:

1. Top 10 Products by Revenue
2. Customer Revenue Distribution
3. Customer Segmentation

## Technology

* Python
* PySpark
* Spark SQL
* Delta Lake
* Databricks
* Git
* Cursor

## AI Development Approach

AI assistance will be used for:

* Requirement analysis
* Pipeline design
* Code generation
* Testing
* Debugging
* Documentation

All AI-generated suggestions must be reviewed and validated before being accepted.

## Important Development Principle

Do not generate implementation code without understanding:

* Inputs
* Outputs
* Business requirements
* Data quality requirements
* Edge cases
* Testing requirements
