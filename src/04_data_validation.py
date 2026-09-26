# Databricks notebook source
# MAGIC %md
# MAGIC # 04 - Data Validation
# MAGIC
# MAGIC Final quality gate. If any check fails, this task FAILS, so the Databricks job fails
# MAGIC and GitHub Actions marks the deployment as failed (PROD will not be deployed after a bad QA run).

# COMMAND ----------

import json
import os
import sys

sys.path.append(os.getcwd())

from transformations import find_quality_issues, table_name

# COMMAND ----------

dbutils.widgets.text("catalog", "qa_catalog")
dbutils.widgets.text("schema", "sales")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

# COMMAND ----------

row_counts = {
    name: spark.table(table_name(catalog, schema, name)).count()
    for name in ("bronze_orders", "silver_orders", "gold_sales_summary")
}
print(f"Row counts: {row_counts}")

errors = [f"{name} is empty" for name, count in row_counts.items() if count == 0]
errors.extend(find_quality_issues(spark.table(table_name(catalog, schema, "silver_orders"))))

if errors:
    raise ValueError("Data validation FAILED: " + "; ".join(errors))

print("Data validation PASSED")

# COMMAND ----------

# The exit value is shown in the job run output (visible from GitHub Actions logs too).
dbutils.notebook.exit(json.dumps({"status": "PASSED", "catalog": catalog, "schema": schema, **row_counts}))
