# Candidate Information

**Name:** Ramneek Kaur  
**Role:** SSE
**Primary Technology Stack:** Python, PySpark, SQL, Databricks  
**Primary AI Tool Used:** Cursor / AI Assistant  
**Project Option Selected:** Data Pipeline — Medallion Architecture  
**Assessment Start Date:** 25th August 2026 
**Submission Date:** 28th August 2026

## Tools & Environment

- Databricks Community Edition
- Python
- PySpark
- SQL
- Delta Lake
- pandas
- pytest
- Cursor / AI assistant

## Project Overview

This project implements an e-commerce data pipeline using the Medallion Architecture:

Bronze → Silver → Gold → Dashboard

The pipeline processes customer, product and order data and intentionally introduces data-quality issues so that the Silver layer can identify and report them.

## Local Development

The project includes a Python virtual environment and pytest-based tests.

Run tests with:

```bash
python -m pytest tests/ -v