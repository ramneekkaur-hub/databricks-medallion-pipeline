"""Orchestrate all quality checks and create the Silver Delta tables."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import Dict

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


BRONZE_SCHEMA = "bronze"
SILVER_SCHEMA = "silver"
DATASETS = ("customers", "products", "orders")


def _load_stage(module_name: str) -> ModuleType:
    """Load a required numbered module directly from the Silver directory."""
    module_directory = (
        Path(__file__).resolve().parent
        if "__file__" in globals()
        else Path.cwd()
    )
    module_path = module_directory / f"{module_name}.py"
    specification = spec_from_file_location(
        f"_silver_{module_name}", module_path
    )
    if specification is None or specification.loader is None:
        raise ImportError(f"Unable to load Silver module: {module_path}")

    module = module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


completeness = _load_stage("01_quality_completeness")
uniqueness = _load_stage("02_quality_uniqueness")
type_validation = _load_stage("03_quality_type_validation")
referential_integrity = _load_stage("04_quality_referential_integrity")
business_logic = _load_stage("05_quality_business_logic")


def initialize_quality_columns(df: DataFrame) -> DataFrame:
    """Create internal arrays used to accumulate failures and warnings."""
    empty_array = F.array().cast("array<string>")
    return df.withColumn(
        "_quality_failure_reasons", empty_array
    ).withColumn("_quality_warning_reasons", empty_array)


def apply_initial_checks(df: DataFrame, dataset_name: str) -> DataFrame:
    """Run checks that do not depend on another dataset."""
    result = initialize_quality_columns(df)
    result = completeness.apply_completeness_checks(result, dataset_name)
    result = uniqueness.apply_uniqueness_checks(result, dataset_name)
    return type_validation.apply_type_validation(result, dataset_name)


def finalize_quality_columns(df: DataFrame) -> DataFrame:
    """Convert internal arrays into the documented Silver quality columns."""
    failures = F.array_distinct(F.col("_quality_failure_reasons"))
    warnings = F.array_distinct(F.col("_quality_warning_reasons"))
    return (
        df.withColumn(
            "quality_check_result",
            F.when(F.size(failures) == 0, F.lit("PASS")).otherwise(F.lit("FAIL")),
        )
        .withColumn(
            "quality_failure_reason",
            F.when(F.size(failures) > 0, F.concat_ws("|", failures)).otherwise(
                F.lit(None).cast("string")
            ),
        )
        .withColumn(
            "quality_warning_reason",
            F.when(F.size(warnings) > 0, F.concat_ws("|", warnings)).otherwise(
                F.lit(None).cast("string")
            ),
        )
        .drop("_quality_failure_reasons", "_quality_warning_reasons")
    )


def build_silver_dataframes(spark: SparkSession) -> Dict[str, DataFrame]:
    """Read Bronze tables and apply every quality category."""
    checked = {
        dataset_name: apply_initial_checks(
            spark.table(f"{BRONZE_SCHEMA}.{dataset_name}"), dataset_name
        )
        for dataset_name in DATASETS
    }

    checked["orders"] = (
        referential_integrity.apply_referential_integrity_checks(
            checked["orders"], checked["customers"], checked["products"]
        )
    )

    return {
        dataset_name: finalize_quality_columns(
            business_logic.apply_business_logic_checks(
                checked[dataset_name], dataset_name
            )
        )
        for dataset_name in DATASETS
    }


def write_silver_table(
    spark: SparkSession, dataset_name: str, silver_df: DataFrame
) -> DataFrame:
    """Overwrite one Silver table and verify that every Bronze row remains."""
    bronze_count = spark.table(f"{BRONZE_SCHEMA}.{dataset_name}").count()
    table_name = f"{SILVER_SCHEMA}.{dataset_name}"

    (
        silver_df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(table_name)
    )

    saved_df = spark.table(table_name)
    silver_count = saved_df.count()
    if silver_count != bronze_count:
        raise RuntimeError(
            f"Row-count validation failed for {dataset_name}: "
            f"bronze={bronze_count}, silver={silver_count}"
        )

    print(
        f"Created {table_name}: bronze={bronze_count}, silver={silver_count}"
    )
    return saved_df


def quality_metrics(df: DataFrame, dataset_name: str) -> DataFrame:
    """Calculate pass/fail and warning counts and percentages."""
    metrics = df.agg(
        F.count(F.lit(1)).alias("total_records"),
        F.sum(
            F.when(F.col("quality_check_result") == "PASS", 1).otherwise(0)
        ).alias("passed_records"),
        F.sum(
            F.when(F.col("quality_check_result") == "FAIL", 1).otherwise(0)
        ).alias("failed_records"),
        F.sum(
            F.when(F.col("quality_warning_reason").isNotNull(), 1).otherwise(0)
        ).alias("warning_records"),
    )

    return (
        metrics.withColumn("dataset_name", F.lit(dataset_name))
        .withColumn(
            "passed_percentage",
            F.when(
                F.col("total_records") > 0,
                F.round(
                    F.col("passed_records") * 100.0 / F.col("total_records"), 2
                ),
            ).otherwise(F.lit(0.0)),
        )
        .withColumn(
            "failed_percentage",
            F.when(
                F.col("total_records") > 0,
                F.round(
                    F.col("failed_records") * 100.0 / F.col("total_records"), 2
                ),
            ).otherwise(F.lit(0.0)),
        )
        .withColumn(
            "warning_percentage",
            F.when(
                F.col("total_records") > 0,
                F.round(
                    F.col("warning_records") * 100.0 / F.col("total_records"), 2
                ),
            ).otherwise(F.lit(0.0)),
        )
        .withColumn("metrics_timestamp", F.current_timestamp())
        .select(
            "dataset_name",
            "total_records",
            "passed_records",
            "failed_records",
            "warning_records",
            "passed_percentage",
            "failed_percentage",
            "warning_percentage",
            "metrics_timestamp",
        )
    )


def main() -> None:
    """Build Silver tables and publish a combined quality metrics table."""
    spark = SparkSession.builder.appName("ecommerce-silver-quality").getOrCreate()
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {SILVER_SCHEMA}")

    silver_dataframes = build_silver_dataframes(spark)
    saved_dataframes = {
        dataset_name: write_silver_table(
            spark, dataset_name, silver_dataframes[dataset_name]
        )
        for dataset_name in DATASETS
    }

    metrics_df = quality_metrics(
        saved_dataframes["customers"], "customers"
    )
    for dataset_name in ("products", "orders"):
        metrics_df = metrics_df.unionByName(
            quality_metrics(saved_dataframes[dataset_name], dataset_name)
        )

    (
        metrics_df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(f"{SILVER_SCHEMA}.quality_metrics")
    )
    spark.table(f"{SILVER_SCHEMA}.quality_metrics").show(truncate=False)


if __name__ == "__main__":
    main()
