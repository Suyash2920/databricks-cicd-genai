"""Unit tests for src/transformations.py (run in GitHub Actions CI)."""
import pytest

from transformations import (
    aggregate_sales,
    clean_orders,
    find_quality_issues,
    get_raw_orders,
    table_name,
    validate_identifier,
)


def test_raw_orders_row_count(spark):
    assert get_raw_orders(spark).count() == 12


def test_clean_orders_removes_bad_and_duplicate_rows(spark):
    silver = clean_orders(get_raw_orders(spark))
    order_ids = [row.order_id for row in silver.collect()]

    assert silver.count() == 9
    assert len(order_ids) == len(set(order_ids))
    assert "O1009" not in order_ids  # missing customer
    assert "O1010" not in order_ids  # negative quantity


def test_clean_orders_calculates_amount_and_standardizes_region(spark):
    silver = clean_orders(get_raw_orders(spark))

    assert silver.filter("order_id = 'O1002'").collect()[0].amount == 46.5
    assert silver.filter("order_id = 'O1011'").collect()[0].region == "North"


def test_aggregate_sales(spark):
    gold = aggregate_sales(clean_orders(get_raw_orders(spark)))
    result = {(row.region, row.product): row for row in gold.collect()}

    assert gold.count() == 8
    assert result[("North", "Laptop")].total_orders == 2
    assert result[("North", "Laptop")].total_revenue == 1720.0
    assert result[("West", "Keyboard")].total_quantity == 4


def test_quality_checks_pass_for_clean_data(spark):
    assert find_quality_issues(clean_orders(get_raw_orders(spark))) == []


def test_quality_checks_detect_bad_data(spark):
    bad_df = spark.createDataFrame(
        [("X1", -5.0), ("X1", 10.0), (None, 3.0)],
        "order_id string, amount double",
    )
    issues = find_quality_issues(bad_df)

    assert len(issues) == 3


@pytest.mark.parametrize("name", ["qa_catalog", "prod_catalog", "sales", "_tmp1"])
def test_validate_identifier_accepts_safe_names(name):
    assert validate_identifier(name) == name


@pytest.mark.parametrize("name", ["", "qa-catalog", "x; DROP TABLE y", "abc\n", "`x`", "1abc", None])
def test_validate_identifier_rejects_unsafe_names(name):
    with pytest.raises(ValueError):
        validate_identifier(name)


def test_table_name_is_fully_qualified():
    assert table_name("qa_catalog", "sales", "bronze_orders") == "`qa_catalog`.`sales`.`bronze_orders`"
