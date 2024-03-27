# Databricks notebook source
# MAGIC %load_ext autoreload
# MAGIC %autoreload 2

# COMMAND ----------

catalog_name = 'rac_demo_catalog'
schema_name = 'default'

# COMMAND ----------

spark.sql(f'create catalog if not exists {catalog_name}')
spark.sql(f'use catalog {catalog_name}')
spark.sql(f'create schema if not exists {schema_name}')
spark.sql(f'use schema {schema_name}')

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import libraries and create class clients

# COMMAND ----------

from libs import *
import uuid 
from pyspark.sql.functions import *

run_id = str(uuid.uuid4())
print(run_id)

# COMMAND ----------

data_client = DataClient(spark=spark)
forecast_client = DBUForecaster(forecast_frequency='d', interval_width=0.85, forecast_periods=30)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Data

# COMMAND ----------

df = data_client.load_data()
df = data_client.transform_data(df)
display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate and Save Forecasts 

# COMMAND ----------

results_df = (ForecastHelper.score_forecasts(df=df, forecast_client=forecast_client)) 
display(results_df)

# COMMAND ----------

(
  results_df
  .withColumn('run_id', lit(run_id))
  .write
  .format('delta')
  .mode('append')
  .saveAsTable('dbu_forecasts')
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Evaluate and Save Forecast Results

# COMMAND ----------

evaluation_df = (ForecastHelper.eval_forecasts(df=results_df, forecast_client=forecast_client))
display(evaluation_df)

# COMMAND ----------

(
  evaluation_df
  .withColumn('run_id', lit(run_id))
  .write
  .format('delta')
  .mode('append')
  .saveAsTable('dbu_forecast_evaluations')
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Output View

# COMMAND ----------

data_client.create_forecast_view(catalog=catalog_name, schema=schema_name, input_table='dbu_forecasts')

# COMMAND ----------

display(spark.read.table('vw_dbu_forecasts'))

# COMMAND ----------


