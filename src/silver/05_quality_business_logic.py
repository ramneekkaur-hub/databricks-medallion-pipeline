"""Business-rule checks for customers, products, and orders."""

from decimal import Decimal

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F


def _append_reason(
    df: DataFrame, target_column: str, condition: Column, reason: str
) -> DataFrame:
    """Append one failure or warning reason to an internal reason array."""
    reason_array = F.when(condition, F.array(F.lit(reason))).otherwise(
        F.array().cast("array<string>")
    )
    return df.withColumn(
        target_column, F.concat(F.col(target_column), reason_array)
    )


def _customer_checks(df: DataFrame) -> DataFrame:
    result = _append_reason(
        df,
        "_quality_failure_reasons",
        F.col("lifetime_value").isNotNull() & (F.col("lifetime_value") < 0),
        "NEGATIVE_LIFETIME_VALUE",
    )
    result = _append_reason(
        result,
        "_quality_failure_reasons",
        F.col("signup_date").isNotNull()
        & (F.col("signup_date") > F.current_date()),
        "FUTURE_SIGNUP_DATE",
    )
    return _append_reason(
        result,
        "_quality_failure_reasons",
        F.col("customer_segment").isNotNull()
        & ~F.col("customer_segment").isin("Premium", "Standard", "Basic"),
        "INVALID_CUSTOMER_SEGMENT",
    )


def _product_checks(df: DataFrame) -> DataFrame:
    result = df
    checks = [
        (F.col("price").isNotNull() & (F.col("price") < 0), "NEGATIVE_PRICE"),
        (F.col("cost").isNotNull() & (F.col("cost") < 0), "NEGATIVE_COST"),
        (
            F.col("stock_quantity").isNotNull()
            & (F.col("stock_quantity") < 0),
            "NEGATIVE_STOCK_QUANTITY",
        ),
        (
            F.col("reorder_level").isNotNull()
            & (F.col("reorder_level") < 0),
            "NEGATIVE_REORDER_LEVEL",
        ),
    ]
    for condition, reason in checks:
        result = _append_reason(
            result, "_quality_failure_reasons", condition, reason
        )

    return _append_reason(
        result,
        "_quality_warning_reasons",
        F.col("cost").isNotNull()
        & F.col("price").isNotNull()
        & (F.col("cost") > F.col("price")),
        "COST_GREATER_THAN_PRICE",
    )


def _order_checks(df: DataFrame) -> DataFrame:
    amount_fields_present = (
        F.col("quantity").isNotNull()
        & F.col("unit_price").isNotNull()
        & F.col("total_amount").isNotNull()
    )
    checks = [
        (
            F.col("quantity").isNotNull() & (F.col("quantity") <= 0),
            "NON_POSITIVE_QUANTITY",
        ),
        (
            F.col("unit_price").isNotNull() & (F.col("unit_price") < 0),
            "NEGATIVE_UNIT_PRICE",
        ),
        (
            F.col("total_amount").isNotNull() & (F.col("total_amount") < 0),
            "NEGATIVE_TOTAL_AMOUNT",
        ),
        (
            amount_fields_present
            & (
                F.abs(
                    F.col("total_amount")
                    - (F.col("quantity") * F.col("unit_price"))
                )
                > F.lit(Decimal("0.01"))
            ),
            "TOTAL_AMOUNT_MISMATCH",
        ),
        (
            F.col("order_status").isNotNull()
            & ~F.col("order_status").isin("Pending", "Completed", "Cancelled"),
            "INVALID_ORDER_STATUS",
        ),
        (
            F.col("payment_date").isNotNull()
            & F.col("order_date").isNotNull()
            & (F.col("payment_date") < F.col("order_date")),
            "PAYMENT_BEFORE_ORDER_DATE",
        ),
    ]

    result = df
    for condition, reason in checks:
        result = _append_reason(
            result, "_quality_failure_reasons", condition, reason
        )
    return result


def apply_business_logic_checks(df: DataFrame, dataset_name: str) -> DataFrame:
    """Apply only the business rules defined for the selected dataset."""
    if dataset_name == "customers":
        return _customer_checks(df)
    if dataset_name == "products":
        return _product_checks(df)
    if dataset_name == "orders":
        return _order_checks(df)
    raise ValueError(f"Unknown dataset: {dataset_name}")
