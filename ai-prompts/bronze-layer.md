# AI Prompts — Bronze Layer

## Prompt 1: Bronze Ingestion Design

**PROMPT SENT:**

Using the existing assignment requirements and project documentation, implement the Bronze layer for the Databricks Medallion Architecture e-commerce pipeline.

The Bronze layer should:
- Read customers.csv, products.csv and orders.csv.
- Preserve the raw source data without cleaning or business transformations.
- Read source columns as strings so invalid values remain available for Silver validation.
- Add ingestion metadata such as ingestion timestamp, source file name and batch ID.
- Write the data to Delta Bronze tables.
- Validate that the Bronze row count matches the source row count.
- Use PySpark and keep the implementation compatible with Databricks Community Edition.

**AI RESPONSE / APPROACH:**

Cursor generated a PySpark Bronze ingestion script that reads the CSV files with schema inference disabled, adds ingestion metadata, writes Delta tables and validates source versus Bronze row counts.

**WHAT I ACCEPTED:**

I accepted the approach because it follows the Medallion principle that Bronze should preserve source data and defer data-quality validation to Silver.

**WHAT I VALIDATED:**

I reviewed the generated code to confirm that:
- Schema inference is disabled.
- Source values are not cleaned or transformed.
- Ingestion metadata is added.
- Delta tables are created in the Bronze schema.
- Source and Bronze row counts are compared.

**WHAT I CHANGED / CONSIDERED:**

The implementation was kept deliberately simple so that the Bronze layer remains responsible for ingestion rather than data cleansing.

**FINAL DECISION:**

Accepted as the Bronze ingestion implementation, subject to execution and validation in Databricks.