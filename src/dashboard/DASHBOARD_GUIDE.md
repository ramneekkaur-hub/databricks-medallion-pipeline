# E-Commerce Gold Dashboard Guide

## Purpose

This dashboard presents product revenue, customer revenue distribution, and
customer segmentation from the validated Gold layer. All dashboard queries use
Gold tables, which are built only from accepted Silver records.

The SQL statements are available in
`src/dashboard/dashboard_queries.sql`.

## 1. Top 10 Products by Revenue

### Query

Use the first query in `dashboard_queries.sql`. It reads
`gold.sales_by_product`, orders products by `product_revenue` in descending
order, and returns the first 10 rows.

### Recommended visualization

Bar chart:

- Category axis: `product`
- Value axis: `product_revenue`
- Tooltip fields: `category`, `total_orders`
- Sort order: descending by `product_revenue`

### Important fields

- `product`: Product label
- `category`: Product category
- `total_orders`: Number of accepted orders
- `product_revenue`: Revenue from accepted orders

### Filters

No filter is required. An optional `category` filter may be added because the
query returns that field.

## 2. Customer Revenue Distribution

### Query

Use the second query in `dashboard_queries.sql`. It returns one numeric
`customer_revenue` observation per accepted customer from
`gold.revenue_by_customer`.

### Recommended visualization

Histogram:

- Value field: `customer_revenue`
- Choose a readable automatic bin count, then adjust it if the distribution is
  too compressed.
- Tooltip field: `customer_id`

### Important fields

- `customer_id`: Accepted customer identifier
- `customer_revenue`: Total revenue from the customer's accepted orders

### Filters

No filter is required. Customers with no accepted orders remain in the result
with zero revenue, as required by the project.

## 3. Customer Segmentation

### Query

Use the third query in `dashboard_queries.sql`. It reads the aggregated
segments from `gold.customer_segmentation` and presents them in the documented
priority order.

### Recommended visualization

Pie chart:

- Label field: `customer_segment`
- Value field: `customer_count`
- Tooltip fields: `avg_revenue`, `segment_revenue`
- Display value labels or percentages where available.

### Important fields

- `customer_segment`: High-Value, Repeat, One-Time, or Inactive
- `customer_count`: Number of accepted customers in the segment
- `avg_revenue`: Average accepted revenue per customer
- `segment_revenue`: Total accepted revenue for the segment

### Filters

No filter is required. Keep all four available segments visible so the chart
represents the complete accepted customer population.

## Creating the Dashboard in Databricks Community Edition

1. Run the data generation, Bronze, Silver, and Gold steps in that order.
2. Confirm that `gold.sales_by_product`, `gold.revenue_by_customer`, and
   `gold.customer_segmentation` are available.
3. Open the SQL editor and select the available SQL warehouse or compatible
   compute resource.
4. Copy and run each statement from `dashboard_queries.sql` separately.
5. For each result, create the recommended visualization using the field
   mappings above.
6. Add the three visualizations to a new Databricks SQL Dashboard or Lakeview
   dashboard.
7. Arrange the product and segmentation charts above the wider revenue
   histogram.
8. Save the dashboard and verify that it refreshes after the Gold tables are
   rebuilt.

If the workspace does not expose a SQL Dashboard or Lakeview option, run the
same SQL in notebook SQL cells, create the same visualizations from the result
sets, and add them to the notebook dashboard capability available in the
workspace.
