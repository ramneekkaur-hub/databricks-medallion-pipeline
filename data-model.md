# Data Model

## 1. Overview

This project uses a three-layer Medallion Architecture:

```text
CSV Source Files
       |
       v
   Bronze Layer
   Raw ingestion
       |
       v
   Silver Layer
   Validation + DQ
       |
       v
    Gold Layer
 Business aggregations
       |
       v
    Dashboard

## 2. Source Data Model

### Customers

**Grain:** One row per customer.

| Column | Data Type | Description |
|---|---|---|
| customer_id | INT | Unique customer identifier |
| customer_name | STRING | Customer name |
| email | STRING | Customer email address |
| country | STRING | Customer country |
| signup_date | DATE | Customer signup date |
| customer_segment | STRING | Premium, Standard, or Basic |
| lifetime_value | DECIMAL(18,2) | Customer lifetime value |

**Primary Key:** `customer_id`

---

### Products

**Grain:** One row per product.

| Column | Data Type | Description |
|---|---|---|
| product_id | INT | Unique product identifier |
| product_name | STRING | Product name |
| category | STRING | Product category |
| price | DECIMAL(18,2) | Product selling price |
| cost | DECIMAL(18,2) | Product cost |
| stock_quantity | INT | Current stock quantity |
| reorder_level | INT | Stock level at which reordering is required |

**Primary Key:** `product_id`

---

### Orders

**Grain:** One row per complete order.

| Column | Data Type | Description |
|---|---|---|
| order_id | INT | Unique order identifier |
| customer_id | INT | Customer identifier |
| order_date | DATE | Date the order was placed |
| product_id | INT | Product identifier |
| quantity | INT | Quantity ordered |
| unit_price | DECIMAL(18,2) | Price per unit |
| total_amount | DECIMAL(18,2) | Total order amount |
| order_status | STRING | Pending, Completed, or Cancelled |
| payment_date | DATE | Date payment was made; nullable |

**Primary Key:** `order_id`

**Foreign Keys:**
- `customer_id` references `customers.customer_id`
- `product_id` references `products.product_id`

---

## 3. Medallion Layer Model

### Bronze Layer

Bronze contains the raw source data with minimal transformation.

Tables:

- `bronze_customers`
- `bronze_products`
- `bronze_orders`

Bronze retains invalid source records so that they can be validated in Silver.

Bronze also contains ingestion metadata:

- `ingestion_timestamp`
- `source_file_name`
- `pipeline_run_id`

Bronze ingestion uses overwrite mode so that rerunning the pipeline with the same input produces reproducible results.

### Silver Layer

Silver contains typed and validated records.

Tables:

- `silver_customers`
- `silver_products`
- `silver_orders`

Silver retains both valid and invalid records.

Each Silver table contains:

- `quality_check_result`
- `quality_failure_reason`

`quality_check_result` contains `PASS` or `FAIL`.

Multiple quality failures are stored as pipe-separated reason codes.

Example:

```text
NULL_EMAIL|DUPLICATE_CUSTOMER_ID