# Data Generation Notes

## Purpose

The sample data generator creates realistic e-commerce data for customers, products and orders.

The generated data is intentionally populated with data-quality issues so that the Silver layer can demonstrate completeness, uniqueness, referential integrity and validation checks.

## Generated Datasets

### Customers

The customer dataset contains:

- customer_id
- customer_name
- email
- country
- signup_date
- customer_segment
- lifetime_value

Intentional quality issues include:

- NULL customer email values
- Duplicate customer IDs

### Products

The product dataset contains:

- product_id
- product_name
- category
- price
- cost
- stock_quantity
- reorder_level

### Orders

The order dataset contains:

- order_id
- customer_id
- order_date
- product_id
- quantity
- unit_price
- total_amount
- order_status
- payment_date

Intentional quality issues include:

- NULL customer IDs
- NULL product IDs
- Customer IDs that do not exist in the customer dataset
- Product IDs that do not exist in the product dataset
- Duplicate order IDs

## Why Quality Issues Are Introduced

The intentional issues simulate realistic upstream data-quality problems.

The purpose is not to remove the problematic records during generation. Instead, the records are retained so the Bronze layer represents the source data and the Silver layer can identify and flag quality problems.

## Validation

The generated files are validated by the automated tests in:

```text
tests/test_data_generation.py