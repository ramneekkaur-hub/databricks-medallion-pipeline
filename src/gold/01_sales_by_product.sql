-- Product sales metrics use accepted products and accepted orders only.
-- The LEFT JOIN retains accepted products that have no accepted orders.
CREATE OR REPLACE TABLE gold.sales_by_product
USING DELTA
AS
WITH valid_products AS (
    SELECT
        product_id,
        product_name,
        category
    FROM silver.products
    WHERE quality_check_result = 'PASS'
),
valid_orders AS (
    SELECT
        order_id,
        product_id,
        total_amount
    FROM silver.orders
    WHERE quality_check_result = 'PASS'
)
SELECT
    p.product_id,
    p.product_name,
    p.category,
    COUNT(o.order_id) AS total_orders,
    CAST(COALESCE(SUM(o.total_amount), 0) AS DECIMAL(18, 2)) AS total_revenue,
    CAST(COALESCE(AVG(o.total_amount), 0) AS DECIMAL(18, 2)) AS avg_order_value
FROM valid_products AS p
LEFT JOIN valid_orders AS o
    ON p.product_id = o.product_id
GROUP BY
    p.product_id,
    p.product_name,
    p.category;
