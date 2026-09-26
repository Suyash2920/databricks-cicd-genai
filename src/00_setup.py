# Databricks notebook source
# MAGIC %md
# MAGIC # 00 - Environment Setup
# MAGIC
# MAGIC Creates the **catalog** and **schema** for the current environment.
# MAGIC
# MAGIC | Environment | Catalog        |
# MAGIC |-------------|----------------|
# MAGIC | QA          | `qa_catalog`   |
# MAGIC | PROD        | `prod_catalog` |
# MAGIC
# MAGIC Databricks Free Edition allows only ONE workspace, so QA and PROD are separated
# MAGIC with Unity Catalog catalogs instead of separate workspaces.

# COMMAND ----------

import os
import sys

# Make the sibling module "transformations.py" importable (deployed next to this notebook).
sys.path.append(os.getcwd())

from transformations import validate_identifier

# COMMAND ----------

# Job parameters arrive as widgets. Defaults are used only when running the notebook manually.
dbutils.widgets.text("catalog", "qa_catalog")
dbutils.widgets.text("schema", "sales")

catalog = validate_identifier(dbutils.widgets.get("catalog"))
schema = validate_identifier(dbutils.widgets.get("schema"))
print(f"Environment setup -> catalog: {catalog}, schema: {schema}")

# COMMAND ----------

# Try to create the catalog. If that is not permitted, the catalog must be created once in the UI
# (Catalog > + > Create catalog). In that case we only verify that it already exists.
try:
    spark.sql(f"CREATE CATALOG IF NOT EXISTS `{catalog}`")
    print(f"Catalog ready: {catalog}")
except Exception as error:
    existing_catalogs = [row[0] for row in spark.sql("SHOW CATALOGS").collect()]
    if catalog not in existing_catalogs:
        raise RuntimeError(
            f"Catalog '{catalog}' does not exist and could not be created. "
            f"Create it once in the Databricks UI. Details: {error}"
        ) from error
    print(f"Catalog '{catalog}' already exists (create skipped).")

spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{catalog}`.`{schema}`")
print(f"Schema ready: {catalog}.{schema}")
