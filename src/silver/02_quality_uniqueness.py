"""Primary-key uniqueness checks for Silver records."""

from typing import Dict

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F


PRIMARY_KEYS: Dict[str, str] = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id",
}


def apply_uniqueness_checks(df: DataFrame, dataset_name: str) -> DataFrame:
    """Flag every row sharing a non-null duplicate primary key."""
    key_column = PRIMARY_KEYS[dataset_name]
    populated_key = F.col(key_column).isNotNull() & (
        F.trim(F.col(key_column).cast("string")) != ""
    )
    duplicate_key = (
        F.count(F.lit(1)).over(Window.partitionBy(key_column)) > 1
    ) & populated_key
    reason_array = F.when(
        duplicate_key, F.array(F.lit(f"DUPLICATE_{key_column.upper()}"))
    ).otherwise(F.array().cast("array<string>"))

    return df.withColumn(
        "_quality_failure_reasons",
        F.concat(F.col("_quality_failure_reasons"), reason_array),
    )
