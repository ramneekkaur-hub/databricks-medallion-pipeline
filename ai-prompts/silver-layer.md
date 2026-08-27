# AI Prompts — Silver Layer

## Objective

Implement the Silver layer so that Bronze data is validated without silently deleting problematic records.

## Prompt / Interaction Summary 1 — Silver Layer Design

I asked the AI assistant to help design the Silver layer for the e-commerce Medallion Architecture pipeline.

The requirements were to retain the source records while adding data-quality results and reasons for failures.

### AI Response Summary

The proposed approach was to implement separate validation functions for:

- Completeness
- Uniqueness
- Type validation
- Referential integrity
- Business logic

### What I Accepted

I accepted the modular approach because separate validation functions make the pipeline easier to understand, test and maintain.

### What I Changed

I reviewed the generated logic against the assignment requirements and adjusted the implementation to match the actual project schema and data.

### Validation

The implementation was validated through the pytest data-quality tests and by reviewing the generated Silver logic.

## Prompt / Interaction Summary 2 — Completeness

I asked the AI assistant to implement completeness validation for critical fields.

The validation identifies NULL values in fields such as:

- customer email
- order customer_id
- order product_id

### Validation

The tests include a missing customer email scenario and verify that the quality check detects it.

## Prompt / Interaction Summary 3 — Uniqueness

I asked the AI assistant to implement duplicate detection for business keys.

The implementation checks duplicate customer IDs and order IDs.

### Validation

The automated test:

`test_uniqueness_detects_duplicate_customer_id`

was used to verify duplicate detection.

## Prompt / Interaction Summary 4 — Referential Integrity

I asked the AI assistant to implement validation of foreign-key relationships between orders and customers/products.

### Validation

Order customer IDs are checked against the customer dataset and product IDs are checked against the product dataset.

## Prompt / Interaction Summary 5 — Testing

I used AI assistance to investigate failures in the local PySpark tests.

The initial failures were caused by the local Java/Spark environment rather than the quality-check logic.

After correcting the Java version and Spark local configuration, all tests passed.

## Final Validation

Current local test result:

```text
7 passed