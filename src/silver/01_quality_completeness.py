"""Completeness checks for required Silver fields."""

from typing import Dict, List

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F


REQUIRED_COLUMNS: Dict[str, List[str]] = {
    "customers": [
        "customer_id",
        "customer_name",
        "email",
        "country",
        "signup_date",
        "customer_segment",
        "lifetime_value",
    ],
    "products": [
        "product_id",
        "product_name",
        "category",
        "price",
        "cost",
        "stock_quantity",
        "reorder_level",
    ],
    "orders": [
        "order_id",
        "customer_id",
        "order_date",
        "product_id",
        "quantity",
        "unit_price",
        "total_amount",
        "order_status",
    ],
}


def _append_failure(df: DataFrame, condition: Column, reason: str) -> DataFrame:
    """Append one reason when a quality condition fails."""
    reason_array = F.when(condition, F.array(F.lit(reason))).otherwise(
        F.array().cast("array<string>")
    )
    return df.withColumn(
        "_quality_failure_reasons",
        F.concat(F.col("_quality_failure_reasons"), reason_array),
    )


def apply_completeness_checks(df: DataFrame, dataset_name: str) -> DataFrame:
    """Flag null and blank values in required fields."""
    result = df
    for column_name in REQUIRED_COLUMNS[dataset_name]:
        missing = F.col(column_name).isNull() | (
            F.trim(F.col(column_name).cast("string")) == ""
        )
        result = _append_failure(
            result, missing, f"NULL_{column_name.upper()}"
        )
    return result
