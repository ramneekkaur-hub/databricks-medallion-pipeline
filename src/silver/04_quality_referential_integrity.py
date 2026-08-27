"""Referential-integrity checks for Silver orders."""

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F


def _append_failure(df: DataFrame, condition: Column, reason: str) -> DataFrame:
    """Append one referential-integrity failure reason."""
    reason_array = F.when(condition, F.array(F.lit(reason))).otherwise(
        F.array().cast("array<string>")
    )
    return df.withColumn(
        "_quality_failure_reasons",
        F.concat(F.col("_quality_failure_reasons"), reason_array),
    )


def apply_referential_integrity_checks(
    orders: DataFrame, customers: DataFrame, products: DataFrame
) -> DataFrame:
    """Flag non-null order keys that do not exist in their parent dataset."""
    customer_keys = (
        customers.where(F.col("customer_id").isNotNull())
        .select(F.col("customer_id").alias("_customer_key"))
        .distinct()
        .withColumn("_customer_exists", F.lit(True))
    )
    product_keys = (
        products.where(F.col("product_id").isNotNull())
        .select(F.col("product_id").alias("_product_key"))
        .distinct()
        .withColumn("_product_exists", F.lit(True))
    )

    result = orders.join(
        customer_keys,
        orders["customer_id"] == customer_keys["_customer_key"],
        "left",
    )
    result = _append_failure(
        result,
        F.col("customer_id").isNotNull() & F.col("_customer_exists").isNull(),
        "CUSTOMER_ID_NOT_FOUND",
    ).drop("_customer_key", "_customer_exists")

    result = result.join(
        product_keys,
        result["product_id"] == product_keys["_product_key"],
        "left",
    )
    return _append_failure(
        result,
        F.col("product_id").isNotNull() & F.col("_product_exists").isNull(),
        "PRODUCT_ID_NOT_FOUND",
    ).drop("_product_key", "_product_exists")
