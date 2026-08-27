# AI Prompts — Documentation

## 1. Purpose

This document records how AI was used to create, improve, review, and validate
the documentation for the AI Capability Exercise — Medallion Architecture
Data Pipeline.

The goal was to use AI to improve the clarity and completeness of the project
documentation while ensuring that the final documentation accurately reflected
the implementation.

AI was used as a documentation assistant, but the final content was reviewed
against the actual repository structure, source code, tests, and project
requirements.

---

# 2. Documentation Areas Covered

The documentation work covered:

- Project README
- Requirements analysis
- Medallion architecture design
- Data model
- Data quality strategy
- Data generation notes
- Database setup and seed data notes
- Dashboard guide
- Cursor workflow documentation
- Debugging notes
- Reflection
- AI usage documentation
- Setup and execution instructions

The main principle was that documentation should describe what the project
actually does rather than what was originally intended.

---

# 3. Initial Documentation Review

## Prompt Sent to AI

> Review the requirements for my AI Capability Exercise and identify all the
> documentation artifacts I need to provide in the repository.
>
> The project is an e-commerce Databricks Medallion Architecture pipeline with
> Bronze, Silver, Gold, and Dashboard layers.
>
> Required areas include requirement analysis, design, data quality,
> database setup, AI workflow, Cursor workflow, testing, debugging,
> reflection, and prompt history.
>
> Create a checklist that I can use to compare against my repository.

## AI Response Summary

AI identified that the repository needed more than just executable code.

The documentation needed to demonstrate the complete development lifecycle:

1. Understanding the requirements
2. Designing the pipeline
3. Generating sample data
4. Implementing the Medallion layers
5. Implementing data-quality validation
6. Creating Gold aggregations
7. Creating dashboard queries
8. Testing
9. Debugging
10. Using AI throughout the lifecycle
11. Reflecting on the implementation

---

## What I Accepted

I accepted the recommendation to treat the documentation as a required
deliverable rather than an optional addition.

This was important because the exercise explicitly states that the AI-assisted
development process and lifecycle artifacts are part of the submission.

---

# 4. Prompt: README Documentation

## Prompt Sent to AI

> Help me create a README for my Databricks Medallion Architecture data
> pipeline project.
>
> The project contains:
>
> - Sample e-commerce customer, product, and order data
> - Bronze ingestion
> - Silver data-quality validation
> - Gold aggregations
> - Dashboard SQL queries
> - Automated tests
>
> The README should explain the project, repository structure, prerequisites,
> installation, data generation, pipeline execution, testing, and expected
> results.
>
> Do not invent functionality that is not present in the repository.

---

## AI Response Summary

AI proposed a README structure containing:

- Project overview
- Architecture
- Repository structure
- Technology stack
- Prerequisites
- Setup instructions
- Data generation
- Bronze layer
- Silver layer
- Gold layer
- Dashboard
- Testing
- Data-quality issues
- Troubleshooting

---

## What I Accepted

I accepted the overall documentation structure because it makes the repository
easier for another engineer to understand and run.

---

## What I Changed

I reviewed the suggested content against the actual repository and removed or
adjusted anything that was not implemented.

I specifically avoided documenting functionality as complete if it had not
been implemented or validated.

---

## Validation

I checked the documented commands against the commands actually used during
development.

For example, the test suite was validated using:

```bash
python -m pytest tests/ -v

7 passed in 7.53s

