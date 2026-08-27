# Databricks Medallion Pipeline

## AI Capability Exercise

This project implements an end-to-end e-commerce data pipeline using the Medallion Architecture:

Bronze → Silver → Gold → Dashboard

## Technology Stack

- Python
- PySpark
- Spark SQL
- Delta Lake
- Databricks
- Cursor

## Project Overview

The pipeline processes synthetic customer, product, and order data for an
e-commerce company. It preserves raw source values, identifies data-quality
problems without deleting bad rows, and creates business-ready product,
customer, trend, and segmentation tables.

## Architecture

1. **Bronze** reads the CSV files as strings, adds ingestion metadata, and
   stores all rows in Delta tables.
2. **Silver** casts fields to the documented types and applies completeness,
   uniqueness, type, referential-integrity, and business-rule checks.
3. **Gold** uses only Silver records with `quality_check_result = 'PASS'` to
   create business aggregations.
4. **Dashboard** queries the Gold tables for product revenue, customer revenue
   distribution, and customer segmentation.

## Repository Structure

```text
data/                         Generated CSV files
database/                     Delta schemas and setup documentation
src/
├── data_generation/          Reproducible synthetic data generator
├── bronze/                   Raw CSV-to-Delta ingestion
├── silver/                   Data-quality checks and Silver orchestration
├── gold/                     Gold SQL and orchestration
└── dashboard/                Dashboard SQL and setup guide
cursor-workflow/               Project context and task breakdown
requirements-analysis.md       Confirmed requirements and decisions
data-model.md                  Source and Medallion data model
data-quality-strategy.md       Silver quality-handling strategy
design-notes.md                Architecture notes
```

## Source Data

The generator uses the fixed random seed `20260827` and creates:

- `data/customers.csv`: 10,000 rows
- `data/products.csv`: 500 rows
- `data/orders.csv`: 100,000 rows

All data is synthetic. Generated email addresses use the reserved
`example.invalid` domain.

### Intentional Data-Quality Issues

Customers include:

- 50 null emails
- 10 duplicate `customer_id` records
- Invalid dates and decimal values
- Negative lifetime values

Products include:

- Invalid price and stock values
- Negative stock quantities
- Cost-greater-than-price warning cases

Orders include:

- 100 null customer IDs and 200 null product IDs
- 50 nonexistent customer IDs and 30 nonexistent product IDs
- 20 duplicate `order_id` records
- Invalid dates, integers, decimals, and order statuses
- Zero quantities, incorrect totals, and payment dates before order dates

See `database/seed-data-notes.md` for the exact counts of the additional
validation cases.

## Prerequisites

- Python 3
- A Databricks Free Edition or personal development workspace
- Databricks compute with PySpark and Delta Lake
- Permission to create managed schemas and tables
- Source CSV files in a location accessible to Spark

No additional Python dependency is required for sample-data generation.

## Generate Sample Data

From the repository root:

```bash
python3 src/data_generation/generate_sample_data.py
```

The script creates the `data/` directory when needed, writes all three CSV
files, validates their row counts, and prints the injected-issue summary.

## Run the Pipeline

Run these components in order:

1. `src/bronze/ingest_bronze.py`
2. `src/silver/create_silver_tables.py`
3. `src/gold/create_gold_tables.py`

The numbered Silver Python files and Gold SQL files are supporting modules
executed by their respective orchestration scripts.

The Bronze reader resolves the bundled `data/*.csv` files relative to its
deployed script and uses fully qualified workspace-file URIs.

Detailed Free Edition instructions are available in
`database/setup-notes.md`. Expected schemas and table structures are defined
in `database/schema.sql`.

## Databricks Asset Bundle Deployment

Legacy Databricks Community Edition was retired in 2025. Databricks Free
Edition supports bundles and serverless jobs, subject to Free Edition quotas
and feature limits. The development bundle deploys only the Bronze, Silver,
and Gold runtime files plus the CSVs required by Bronze. Tests, documentation,
Cursor workflow files, AI prompts, virtual environments, and Git metadata are
not deployed.

The bundle requires Databricks CLI `0.218.0` or newer. Check the installed
version:

```bash
databricks version
```

On macOS, install or update the current CLI when needed:

```bash
brew tap databricks/tap
brew install databricks
brew upgrade databricks
```

Authenticate without storing credentials in this repository:

```bash
read -r -p "Databricks workspace URL: " DATABRICKS_HOST
export DATABRICKS_HOST
databricks auth login --host "$DATABRICKS_HOST" --profile medallion-dev
export DATABRICKS_CONFIG_PROFILE=medallion-dev
databricks auth describe --profile medallion-dev
```

Databricks does not allow bundle-variable interpolation in authentication
fields such as `workspace.host`. The supported `DATABRICKS_HOST` environment
variable and CLI profile therefore provide the environment-specific host.

From the repository root, validate and deploy the development target:

```bash
python3 src/data_generation/generate_sample_data.py
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
.venv/bin/python -m pytest tests/ -v
databricks bundle validate -t dev
databricks bundle deploy -t dev
databricks bundle summary -t dev
```

The data generator remains a local preparation step. Deployment syncs the
resulting CSVs, and the Databricks job starts with Bronze ingestion. The pytest
suite also remains local because its Spark tests create a local Spark session
rather than a Databricks job task. The currently installed local PySpark
version requires Java 17 for those Spark tests.

Run the deployed Bronze → Silver → Gold job:

```bash
databricks bundle run -t dev medallion_pipeline
```

This command waits for completion and reports task status. To open the deployed
job in the Databricks UI:

```bash
databricks bundle open -t dev medallion_pipeline
```

To remove the bundle-managed job and synced workspace files:

```bash
databricks bundle destroy -t dev
```

`bundle destroy` prompts before deleting deployed bundle resources. It does not
drop the Bronze, Silver, or Gold managed tables created by the pipeline.

The bundle uses serverless environment version 2 and does not configure a
classic cluster, cluster ID, catalog name, token, workspace URL, or personal
credential. The active workspace's default catalog is used. If serverless
Python job tasks, workspace files, or schema creation are unavailable in the
target workspace, run the three orchestration scripts manually on compatible
Databricks compute instead.

## Data-Quality Reporting

Silver retains both passing and failing records. Each Silver table contains:

- `quality_check_result`: `PASS` or `FAIL`
- `quality_failure_reason`: pipe-separated failure codes
- `quality_warning_reason`: non-failing warning codes where applicable

The `silver.quality_metrics` Delta table reports total, passed, failed, and
warning record counts and percentages for each dataset.

## Dashboard Setup

`src/dashboard/dashboard_queries.sql` contains queries for:

- Top 10 products by revenue
- Customer revenue distribution
- Customer segmentation

Run each query separately in Databricks SQL and configure the recommended bar
chart, histogram, and pie chart. See `src/dashboard/DASHBOARD_GUIDE.md` for
field mappings and Free Edition setup steps.

## Testing Approach

The project includes validation within the pipeline:

- The generator asserts the required source row counts.
- Bronze compares source and written table counts.
- Silver compares Bronze and Silver counts to confirm that bad rows were not
  dropped.
- Gold checks retained product and customer counts and confirms every accepted
  customer is segmented.
- Intentional source issues provide known cases for validating each Silver
  quality category.

The repository contains pytest tests for generated row counts, required source
defects, completeness, and uniqueness. During the latest local validation,
five data-generation tests passed and two Spark-based tests could not start
because the active Java 11 runtime was older than the installed PySpark
runtime requires. No Silver assertion was reached. The Java/PySpark versions
must be aligned before rerunning those tests. An end-to-end Databricks Free
Edition run is not currently documented.

## AI-Assisted Development

This project is an AI capability exercise using Cursor for requirements
analysis, design, implementation assistance, debugging, testing guidance, and
documentation. AI-generated suggestions must be reviewed and validated before
being accepted.

## Assumptions and Limitations

- Processing is batch-based; real-time streaming is out of scope.
- Bronze and downstream tables use overwrite behavior for reproducible
  learning runs.
- Source dates use `DATE`; timezone handling is out of scope.
- The project assumes one currency and does not perform currency conversion.
- Gold revenue is calculated from valid Silver `total_amount` values.
- Gold currently includes every accepted order status in revenue because no
  completed-only rule is defined.
- `lifetime_value_actual` represents cumulative accepted order revenue.
- Complex production retries and automatic schema evolution are out of scope.
- Databricks workspace paths and dashboard availability must be confirmed in
  the target Free Edition or personal workspace.
- The pipeline has not been documented as tested end-to-end in Databricks
  Free Edition.