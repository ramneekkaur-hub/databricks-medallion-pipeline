-- 1. Top 10 products by revenue
-- Bar chart: product_name on the category axis and product_revenue on the value axis.
SELECT
    product_id,
    product_name AS product,
    category,
    total_orders,
    total_revenue AS product_revenue
FROM gold.sales_by_product
ORDER BY product_revenue DESC, product_id ASC
LIMIT 10;

-- 2. Customer revenue distribution
-- Histogram: customer_revenue is the numeric value to bin.
SELECT
    customer_id,
    total_revenue AS customer_revenue
FROM gold.revenue_by_customer
WHERE total_revenue IS NOT NULL
ORDER BY customer_revenue ASC, customer_id ASC;

-- 3. Customer segmentation
-- Pie chart: segment_type is the label and customer_count is the value.
SELECT
    segment_type AS customer_segment,
    customer_count,
    avg_revenue,
    total_revenue AS segment_revenue
FROM gold.customer_segmentation
ORDER BY
    CASE segment_type
        WHEN 'High-Value' THEN 1
        WHEN 'Repeat' THEN 2
        WHEN 'One-Time' THEN 3
        WHEN 'Inactive' THEN 4
        ELSE 5
    END;
