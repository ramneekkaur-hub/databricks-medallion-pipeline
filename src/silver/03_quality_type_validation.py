"""Type validation and casting for Silver records."""

from typing import Dict

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


EXPECTED_TYPES: Dict[str, Dict[str, str]] = {
    "customers": {
        "customer_id": "int",
        "signup_date": "date",
        "lifetime_value": "decimal(18,2)",
    },
    "products": {
        "product_id": "int",
        "price": "decimal(18,2)",
        "cost": "decimal(18,2)",
        "stock_quantity": "int",
        "reorder_level": "int",
    },
    "orders": {
        "order_id": "int",
        "customer_id": "int",
        "order_date": "date",
        "product_id": "int",
        "quantity": "int",
        "unit_price": "decimal(18,2)",
        "total_amount": "decimal(18,2)",
        "payment_date": "date",
    },
}


def apply_type_validation(df: DataFrame, dataset_name: str) -> DataFrame:
    """Flag failed casts, then expose the successfully typed values."""
    result = df
    for column_name, target_type in EXPECTED_TYPES[dataset_name].items():
        source_value = F.col(column_name)
        # try_cast returns NULL for malformed values instead of aborting the
        # pipeline when Spark ANSI mode is enabled.
        typed_value = F.expr(
            f"try_cast(`{column_name}` AS {target_type})"
        )
        has_source_value = source_value.isNotNull() & (
            F.trim(source_value.cast("string")) != ""
        )
        invalid_type = has_source_value & typed_value.isNull()
        reason_array = F.when(
            invalid_type,
            F.array(F.lit(f"INVALID_{column_name.upper()}_TYPE")),
        ).otherwise(F.array().cast("array<string>"))

        result = result.withColumn(
            "_quality_failure_reasons",
            F.concat(F.col("_quality_failure_reasons"), reason_array),
        ).withColumn(column_name, typed_value)

    return result
