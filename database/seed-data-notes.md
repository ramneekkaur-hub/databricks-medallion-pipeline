# Seed Data Notes

## Overview

`src/data_generation/generate_sample_data.py` creates three completely
synthetic CSV files in `data/`. It uses the fixed random seed `20260827`, so
running the generator again produces the same source values and intentional
quality issues.

Empty CSV fields represent source `NULL` values during Bronze and Silver
processing. No real personal information is used; generated email addresses
use the reserved `example.invalid` domain.

## Generated Files

### `data/customers.csv`

- Expected rows: **10,000**, excluding the header
- Contains customer identifiers, synthetic names and emails, country, signup
  date, source segment, and lifetime value

Intentional issues:

- 50 null emails
- 10 duplicate `customer_id` records
- 10 invalid `signup_date` values
- 10 invalid `lifetime_value` values
- 10 negative `lifetime_value` values

The 10 injected duplicate records cause 20 customer rows to participate in
duplicate-ID groups because both the original and repeated rows are flagged.

### `data/products.csv`

- Expected rows: **500**, excluding the header
- Contains product identifiers, synthetic names, category, price, cost, stock,
  and reorder level

Intentional issues:

- 10 invalid `price` values
- 10 invalid `stock_quantity` values
- 5 negative `stock_quantity` values
- 5 records where cost is greater than price

Cost greater than price is a warning only and does not fail the product record.

### `data/orders.csv`

- Expected rows: **100,000**, excluding the header
- Contains one row per order

Required intentional issues:

- 100 null `customer_id` values
- 200 null `product_id` values
- 50 `customer_id` values that do not exist in customers
- 30 `product_id` values that do not exist in products
- 20 duplicate `order_id` records

Additional validation examples:

- 25 invalid `order_date` values
- 25 invalid `quantity` values
- 25 invalid `unit_price` values
- 25 zero-quantity values
- 25 incorrect `total_amount` values
- 25 invalid `order_status` values
- 25 payment dates before their order dates

The 20 injected duplicate records cause 40 order rows to participate in
duplicate-ID groups because both the original and repeated rows are flagged.
