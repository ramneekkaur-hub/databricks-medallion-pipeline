# Data Quality Strategy

## 1. Purpose

The purpose of the Silver layer is to identify, flag, and report data quality issues while retaining all source records.

Invalid records must not be silently deleted.

Each Silver record will contain:

- `quality_check_result`
- `quality_failure_reason`

A record can have multiple failure reasons.

Multiple failure reasons will be stored as a pipe-separated string.

Example:

```text
NULL_EMAIL|DUPLICATE_CUSTOMER_ID