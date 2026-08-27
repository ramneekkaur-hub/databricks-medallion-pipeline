# Design Notes

## 1. Architecture Overview

The project follows the Databricks Medallion Architecture:

```text
CSV Files
   |
   v
Bronze
Raw source data + ingestion metadata
   |
   v
Silver
Typed data + data quality validation
   |
   v
Gold
Business aggregations
   |
   v
Dashboard
Business reporting and visualization