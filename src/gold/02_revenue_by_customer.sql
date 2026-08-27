-- Customer revenue is calculated from accepted order total_amount values.
-- Accepted customers with no accepted orders remain with zero metrics.
CREATE OR REPLACE TABLE gold.revenue_by_customer
USING DELTA
AS
WITH valid_customers AS (
    SELECT
        customer_id,
        customer_name,
        customer_segment
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
customer_revenue AS (
    SELECT
        c.customer_id,
        c.customer_name,
        c.customer_segment,
        COUNT(o.order_id) AS total_orders,
        COALESCE(SUM(o.total_amount), 0) AS total_revenue,
        COALESCE(AVG(o.total_amount), 0) AS avg_order_value
    FROM valid_customers AS c
    LEFT JOIN valid_orders AS o
        ON c.customer_id = o.customer_id
    GROUP BY
        c.customer_id,
        c.customer_name,
        c.customer_segment
)
SELECT
    customer_id,
    customer_name,
    customer_segment,
    total_orders,
    CAST(total_revenue AS DECIMAL(18, 2)) AS total_revenue,
    CAST(avg_order_value AS DECIMAL(18, 2)) AS avg_order_value,
    CAST(total_revenue AS DECIMAL(18, 2)) AS lifetime_value_actual
FROM customer_revenue;
