# Databricks Setup Notes

## Prerequisites

- A Databricks Community Edition workspace
- A running cluster or other compute resource with PySpark and Delta Lake
- Python 3 for the synthetic data generator
- This repository imported into the Databricks workspace or otherwise
  available to the driver
- Permission to create managed schemas and Delta tables

No third-party Python package is required by the data generator. PySpark and
Delta Lake are supplied by Databricks.

## Optional Schema Setup

Run `database/schema.sql` in the Databricks SQL editor or a notebook SQL cell
to create the `bronze`, `silver`, and `gold` schemas and empty expected tables.

The pipeline scripts also create their target schemas and overwrite their
managed tables, so the schema file primarily documents and initializes the
expected structures.

## Generate the CSV Data

From the repository root, run:

```bash
python3 src/data_generation/generate_sample_data.py
```

This creates:

- `data/customers.csv`
- `data/products.csv`
- `data/orders.csv`

The script validates the expected row counts and prints the injected issue
summary. See `database/seed-data-notes.md` for details.

## Make the CSV Files Available to Spark

`src/bronze/ingest_bronze.py` uses the relative paths
`data/customers.csv`, `data/products.csv`, and `data/orders.csv`. Run it with
the repository root as the working directory when those paths are directly
available to Spark.

If the Community Edition workspace does not allow Spark to read repository
files through relative paths, upload the three CSV files to a Spark-accessible
workspace or DBFS location and update the `DATASETS` paths in
`src/bronze/ingest_bronze.py` to those locations.

## Pipeline Execution Order

Run the layers in this order:

1. **Bronze:** `src/bronze/ingest_bronze.py`
2. **Silver:** `src/silver/create_silver_tables.py`
3. **Gold:** `src/gold/create_gold_tables.py`
4. **Dashboard queries:** `src/dashboard/dashboard_queries.sql`

### Bronze

Run `src/bronze/ingest_bronze.py` as a Databricks Python
notebook or script. It:

- Reads all CSV source fields as strings
- Adds ingestion metadata
- Overwrites `bronze.customers`, `bronze.products`, and `bronze.orders`
- Reconciles source and Bronze row counts

### Silver

Run `src/silver/create_silver_tables.py`. The numbered quality files are
supporting modules loaded by this orchestrator and do not need to be run
separately.

The Silver step:

- Applies completeness, uniqueness, type, referential-integrity, and business
  checks
- Retains both passing and failing rows
- Creates `silver.customers`, `silver.products`, and `silver.orders`
- Creates `silver.quality_metrics`

Review `silver.quality_metrics` and sample failed records before continuing to
Gold.

### Gold

Run `src/gold/create_gold_tables.py`. It executes the numbered SQL files and
creates:

- `gold.sales_by_product`
- `gold.revenue_by_customer`
- `gold.daily_sales_trends`
- `gold.weekly_sales_trends`
- `gold.customer_segmentation`

Gold queries use only Silver records with `quality_check_result = 'PASS'`.

## Run the Dashboard Queries

1. Open a Databricks SQL editor connected to the available compute resource.
2. Open `src/dashboard/dashboard_queries.sql`.
3. Run each of the three SQL statements separately.
4. Create the recommended bar chart, histogram, and pie chart.
5. Add the visualizations to a Databricks SQL Dashboard or Lakeview dashboard.

See `src/dashboard/DASHBOARD_GUIDE.md` for field mappings and visualization
settings. If the workspace does not provide a SQL dashboard interface, run the
queries in notebook SQL cells and use the dashboard capability available
there.

## Validation Note

These instructions describe the intended Databricks execution process. The
pipeline has not been executed end-to-end in a Databricks Community Edition
workspace as part of this documentation task, so table creation, workspace
paths, and dashboard availability must be confirmed in the target workspace.
