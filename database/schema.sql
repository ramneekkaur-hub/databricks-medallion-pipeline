-- Databricks SQL / Delta Lake schemas and expected managed-table structures.
-- Pipeline scripts overwrite table contents during reproducible learning runs.

CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS bronze.customers (
    customer_id STRING,
    customer_name STRING,
    email STRING,
    country STRING,
    signup_date STRING,
    customer_segment STRING,
    lifetime_value STRING,
    ingestion_timestamp TIMESTAMP,
    source_file_name STRING,
    batch_id STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS bronze.products (
    product_id STRING,
    product_name STRING,
    category STRING,
    price STRING,
    cost STRING,
    stock_quantity STRING,
    reorder_level STRING,
    ingestion_timestamp TIMESTAMP,
    source_file_name STRING,
    batch_id STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS bronze.orders (
    order_id STRING,
    customer_id STRING,
    order_date STRING,
    product_id STRING,
    quantity STRING,
    unit_price STRING,
    total_amount STRING,
    order_status STRING,
    payment_date STRING,
    ingestion_timestamp TIMESTAMP,
    source_file_name STRING,
    batch_id STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS silver.customers (
    customer_id INT,
    customer_name STRING,
    email STRING,
    country STRING,
    signup_date DATE,
    customer_segment STRING,
    lifetime_value DECIMAL(18, 2),
    ingestion_timestamp TIMESTAMP,
    source_file_name STRING,
    batch_id STRING,
    quality_check_result STRING,
    quality_failure_reason STRING,
    quality_warning_reason STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS silver.products (
    product_id INT,
    product_name STRING,
    category STRING,
    price DECIMAL(18, 2),
    cost DECIMAL(18, 2),
    stock_quantity INT,
    reorder_level INT,
    ingestion_timestamp TIMESTAMP,
    source_file_name STRING,
    batch_id STRING,
    quality_check_result STRING,
    quality_failure_reason STRING,
    quality_warning_reason STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS silver.orders (
    order_id INT,
    customer_id INT,
    order_date DATE,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(18, 2),
    total_amount DECIMAL(18, 2),
    order_status STRING,
    payment_date DATE,
    ingestion_timestamp TIMESTAMP,
    source_file_name STRING,
    batch_id STRING,
    quality_check_result STRING,
    quality_failure_reason STRING,
    quality_warning_reason STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS silver.quality_metrics (
    dataset_name STRING,
    total_records BIGINT,
    passed_records BIGINT,
    failed_records BIGINT,
    warning_records BIGINT,
    passed_percentage DOUBLE,
    failed_percentage DOUBLE,
    warning_percentage DOUBLE,
    metrics_timestamp TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS gold.sales_by_product (
    product_id INT,
    product_name STRING,
    category STRING,
    total_orders BIGINT,
    total_revenue DECIMAL(18, 2),
    avg_order_value DECIMAL(18, 2)
) USING DELTA;

CREATE TABLE IF NOT EXISTS gold.revenue_by_customer (
    customer_id INT,
    customer_name STRING,
    customer_segment STRING,
    total_orders BIGINT,
    total_revenue DECIMAL(18, 2),
    avg_order_value DECIMAL(18, 2),
    lifetime_value_actual DECIMAL(18, 2)
) USING DELTA;

CREATE TABLE IF NOT EXISTS gold.daily_sales_trends (
    sales_date DATE,
    total_orders BIGINT,
    total_quantity BIGINT,
    total_revenue DECIMAL(18, 2),
    avg_order_value DECIMAL(18, 2)
) USING DELTA;

CREATE TABLE IF NOT EXISTS gold.weekly_sales_trends (
    week_start_date DATE,
    total_orders BIGINT,
    total_quantity BIGINT,
    total_revenue DECIMAL(18, 2),
    avg_order_value DECIMAL(18, 2)
) USING DELTA;

CREATE TABLE IF NOT EXISTS gold.customer_segmentation (
    segment_type STRING,
    customer_count BIGINT,
    avg_revenue DECIMAL(18, 2),
    total_revenue DECIMAL(18, 2)
) USING DELTA;
