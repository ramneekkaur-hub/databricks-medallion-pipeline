import importlib.util
from pathlib import Path

from pyspark.sql import SparkSession


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SILVER_DIR = PROJECT_ROOT / "src" / "silver"


def load_module(filename, module_name):
    path = SILVER_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


completeness = load_module(
    "01_quality_completeness.py",
    "quality_completeness",
)

uniqueness = load_module(
    "02_quality_uniqueness.py",
    "quality_uniqueness",
)


def create_spark():
    return (
        SparkSession.builder
        .master("local[2]")
        .appName("ecommerce-quality-tests")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )


def empty_reasons(df):
    from pyspark.sql import functions as F

    return df.withColumn(
        "_quality_failure_reasons",
        F.array().cast("array<string>"),
    )


def test_completeness_detects_missing_customer_email():
    spark = create_spark()

    df = spark.createDataFrame(
        [
            (
                "1",
                "Customer 1",
                "",
                "Australia",
                "2024-01-01",
                "Standard",
                "100.00",
            ),
            (
                "2",
                "Customer 2",
                "customer2@example.com",
                "Australia",
                "2024-01-01",
                "Standard",
                "200.00",
            ),
        ],
        [
            "customer_id",
            "customer_name",
            "email",
            "country",
            "signup_date",
            "customer_segment",
            "lifetime_value",
        ],
    )

    df = empty_reasons(df)

    result = completeness.apply_completeness_checks(
        df,
        "customers",
    )

    failed = (
        result
        .filter(result.customer_id == "1")
        .select("_quality_failure_reasons")
        .collect()[0]
    )

    assert "NULL_EMAIL" in failed["_quality_failure_reasons"]

    spark.stop()


def test_uniqueness_detects_duplicate_customer_id():
    spark = create_spark()

    df = spark.createDataFrame(
        [
            ("1", "Customer 1"),
            ("1", "Customer 1 duplicate"),
            ("2", "Customer 2"),
        ],
        ["customer_id", "customer_name"],
    )

    df = empty_reasons(df)

    result = uniqueness.apply_uniqueness_checks(
        df,
        "customers",
    )

    duplicate_rows = (
        result
        .filter(result.customer_id == "1")
        .select("_quality_failure_reasons")
        .collect()
    )

    assert len(duplicate_rows) == 2

    for row in duplicate_rows:
        assert "DUPLICATE_CUSTOMER_ID" in row["_quality_failure_reasons"]

    spark.stop()
