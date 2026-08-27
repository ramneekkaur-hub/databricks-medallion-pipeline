-- Segment each accepted customer using accepted order history, then aggregate.
CREATE OR REPLACE TABLE gold.customer_segmentation
USING DELTA
AS
WITH valid_customers AS (
    SELECT customer_id
    FROM silver.customers
    WHERE quality_check_result = 'PASS'
),
valid_orders AS (
    SELECT
        order_id,
        customer_id,
        total_amount
    FROM silver.orders
    WHERE quality_check_result = 'PASS'
),
customer_metrics AS (
    SELECT
        c.customer_id,
        COUNT(o.order_id) AS total_orders,
        COALESCE(SUM(o.total_amount), 0) AS total_revenue
    FROM valid_customers AS c
    LEFT JOIN valid_orders AS o
        ON c.customer_id = o.customer_id
    GROUP BY c.customer_id
),
classified_customers AS (
    SELECT
        customer_id,
        total_revenue,
        CASE
            WHEN total_revenue >= 5000 THEN 'High-Value'
            WHEN total_orders >= 2 THEN 'Repeat'
            WHEN total_orders = 1 THEN 'One-Time'
            ELSE 'Inactive'
        END AS segment_type
    FROM customer_metrics
)
SELECT
    segment_type,
    COUNT(customer_id) AS customer_count,
    CAST(AVG(total_revenue) AS DECIMAL(18, 2)) AS avg_revenue,
    CAST(SUM(total_revenue) AS DECIMAL(18, 2)) AS total_revenue
FROM classified_customers
GROUP BY segment_type;
