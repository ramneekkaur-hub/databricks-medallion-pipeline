-- Daily trends at one row per accepted order date.
CREATE OR REPLACE TABLE gold.daily_sales_trends
USING DELTA
AS
SELECT
    order_date AS sales_date,
    COUNT(order_id) AS total_orders,
    SUM(quantity) AS total_quantity,
    CAST(SUM(total_amount) AS DECIMAL(18, 2)) AS total_revenue,
    CAST(AVG(total_amount) AS DECIMAL(18, 2)) AS avg_order_value
FROM silver.orders
WHERE quality_check_result = 'PASS'
  AND order_date IS NOT NULL
GROUP BY order_date;

-- Weekly trends use Monday-based Spark/Databricks calendar weeks.
CREATE OR REPLACE TABLE gold.weekly_sales_trends
USING DELTA
AS
SELECT
    CAST(DATE_TRUNC('WEEK', order_date) AS DATE) AS week_start_date,
    COUNT(order_id) AS total_orders,
    SUM(quantity) AS total_quantity,
    CAST(SUM(total_amount) AS DECIMAL(18, 2)) AS total_revenue,
    CAST(AVG(total_amount) AS DECIMAL(18, 2)) AS avg_order_value
FROM silver.orders
WHERE quality_check_result = 'PASS'
  AND order_date IS NOT NULL
GROUP BY CAST(DATE_TRUNC('WEEK', order_date) AS DATE);
