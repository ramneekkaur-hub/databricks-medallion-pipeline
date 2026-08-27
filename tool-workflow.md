# AI-Assisted Tool Workflow

## Primary AI Tool

Cursor was the primary AI development tool used for this project. It was used
inside the repository to review project files, discuss requirements, generate
and revise code, run limited local checks, and create documentation.

## Providing Project Context

Work began by asking Cursor to read:

- `cursor-workflow/project-context.md`
- `cursor-workflow/cursor-rules-or-instructions.md`
- `cursor-workflow/task-breakdown.md`

The project context described the source datasets, expected volumes, Medallion
layers, required quality checks, Gold outputs, dashboard requirements, and
technology stack. The task breakdown supplied the intended phase order.

Additional context was captured in:

- `requirements-analysis.md`
- `data-model.md`
- `data-quality-strategy.md`
- `design-notes.md`

The requirements were refined through follow-up prompts. The user explicitly
confirmed data types, allowed statuses, amount tolerance, segmentation rules,
failure-reason format, duplicate handling, overwrite behavior, and Gold
inclusion rules before implementation continued.

## Requirement Analysis

Cursor was first used in the planning phase rather than immediately generating
pipeline code. It identified:

- The problem statement
- Functional and non-functional requirements
- Assumptions and edge cases
- Ambiguous business rules
- Acceptance criteria for each layer
- A recommended implementation sequence

The initial analysis was reviewed by the user. Confirmed decisions were then
incorporated into the requirements, including pipe-separated failure reasons,
retaining invalid Silver rows, using only valid rows in Gold, and the
High-Value/Repeat/One-Time/Inactive segmentation rules.

## Architecture and Layer Design

Cursor used the confirmed requirements and data model to design:

- **Bronze:** raw string ingestion, ingestion metadata, Delta tables, overwrite
  mode, and source-to-table row reconciliation
- **Silver:** modular completeness, uniqueness, type, referential-integrity,
  and business-rule checks with accumulated failure reasons
- **Gold:** product revenue, customer revenue, daily and weekly trends, and
  customer-segmentation aggregations
- **Dashboard:** Gold-based SQL for the three required visualizations

The design deliberately kept invalid records in Silver. Gold queries filter on
`quality_check_result = 'PASS'`.

## Code Generation

Cursor generated and revised:

- Standard Python for reproducible synthetic CSV generation
- PySpark for Bronze ingestion and Silver validation
- Spark SQL for Gold aggregations and dashboard queries
- Python orchestration scripts for Silver and Gold
- Delta schema and project setup documentation

Code generation was performed one project phase at a time. Cursor was
instructed not to generate later layers before the current requirements were
understood.

No unnecessary Python dependency was added. The sample-data generator uses the
Python standard library, while pipeline code relies on PySpark and Delta Lake
provided by Databricks.

## Validation of AI-Generated Code

Validation performed during the Cursor sessions included:

- Running `generate_sample_data.py` successfully
- Confirming final source counts of 10,000 customers, 500 products, and
  100,000 orders
- Running an in-memory check of all documented generator issue counts
- Reviewing generated files against the confirmed requirements
- Running editor lint checks after code and documentation changes
- Correcting zero-quantity test data so it did not unintentionally double the
  expected total-amount mismatch count

The Bronze, Silver, and Gold code contains runtime count or reconciliation
checks, but the complete pipeline has not been run end-to-end in Databricks
Community Edition.

## Testing and Validation Workflow

Intentional defects were generated to provide known Silver test cases:

- Null required fields
- Duplicate identifiers
- Invalid types
- Missing customer and product references
- Invalid quantities, amounts, statuses, and dates
- A non-failing product cost warning

The generator's issue counts were checked locally. Silver also produces
`silver.quality_metrics` with passed, failed, and warning counts and
percentages.

A local PySpark integration check for the Silver rules was attempted. The first
attempt could not start Spark because the sandbox blocked required system and
network operations. A retry outside the sandbox was started but interrupted
before completion. Therefore, the Silver rule counts and Delta writes must
still be validated in Databricks.

No dedicated automated test suite currently exists in the repository.

## Debugging with Cursor

Cursor was used to investigate and correct issues found during development:

- Generator issue counts were reviewed for overlap and consistency.
- Zero-quantity orders were changed to use a matching zero total so they test
  only the intended quantity rule.
- Silver type conversion uses `try_cast` so malformed values are flagged
  instead of aborting execution when Spark ANSI mode is enabled.
- A normal Python import check failed for the required numbered Silver module
  filenames. The Silver orchestrator was changed to load those files directly
  with the Python standard library.
- Databricks-relative source paths were documented as an environment-dependent
  item that must be confirmed in the target workspace.

## Data-Quality Assistance

Cursor helped translate the assignment into explicit checks and reason codes.
The Silver design:

- Accumulates multiple failure reasons per row
- Stores reasons as a pipe-separated string
- Flags every row participating in a duplicate-ID group
- Handles null keys through completeness rather than uniqueness
- Keeps type failures and original Bronze records auditable
- Treats cost greater than price as a warning rather than a failure
- Preserves row counts between Bronze and Silver

This approach supports validation without silently deleting bad data.

## Information That Must Not Be Shared with AI Tools

The following should not be provided to Cursor or another external AI tool:

- Real customer names, email addresses, addresses, or other PII
- Production customer, order, payment, or behavioral data
- Passwords, access tokens, API keys, private keys, or certificates
- Databricks credentials and connection secrets
- Confidential business metrics or proprietary data not approved for sharing
- Production logs containing sensitive identifiers or payloads

This project avoids that risk by using fully synthetic names and reserved
`example.invalid` email addresses. Secrets must be stored using approved secret
management rather than source files or prompts.

## Reusing the Workflow in Production

The context-first workflow can be reused for a production pipeline by:

1. Documenting schemas, business rules, quality expectations, and operational
   constraints before requesting code.
2. Giving the AI only approved, anonymized examples.
3. Dividing work into reviewable layer-specific changes.
4. Requiring human review of every generated change.
5. Adding automated unit, integration, data-contract, and reconciliation tests.
6. Running lint, security, and dependency checks in CI.
7. Validating generated SQL and PySpark against a non-production Databricks
   environment.
8. Using managed secrets, access controls, monitoring, and deployment
   approvals.
9. Recording prompts, decisions, test evidence, and unresolved assumptions.

Production reuse would require stronger orchestration, idempotency,
observability, recovery, and security controls than this learning assignment.

## Lessons Learned

### What worked

- Reading project context before implementation reduced unsupported
  assumptions.
- User review converted ambiguities into explicit rules before code generation.
- A fixed seed made source data and defect counts reproducible.
- Layer-specific prompts kept changes focused and reviewable.
- Known intentional defects made validation expectations concrete.
- Lint checks and executable count checks caught issues beyond visual review.

### What did not work or remains incomplete

- Numbered Python filenames were not reliably importable through normal module
  imports and required an explicit loader.
- Local Spark execution was restricted by the sandbox, and the unrestricted
  Silver validation retry did not finish.
- The pipeline has not been validated end-to-end in Databricks Community
  Edition.
- Relative CSV path behavior and dashboard availability remain dependent on
  the target Databricks workspace.
- A dedicated automated test suite and recorded Databricks test results still
  need to be added.

AI accelerated planning, implementation, review, and documentation, but it did
not replace requirement decisions, human review, or execution in the target
platform.
