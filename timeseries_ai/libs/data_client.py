from pyspark.sql.functions import *

class DataClient():

  def __init__(self, spark):
    self.spark = spark # pass the spark object for DDL actions


  def load_data(self):
    """
    Load data from system.billing.usage
    """
    return (
      self.spark.sql("""
                select usage_date as created_on
                --, workspace_id
                , sku_name as sku
                , usage_quantity as dbus

                from system.billing.usage

                where usage_unit = 'DBU'
                and usage_date < current_date() -- we don't want a partial day
                """)
      )
  
  def transform_data(self, df):
    """
    Function to transform input data 
    """
    df = df.select(col('created_on').alias('ds'), 
                   col('sku'), 
                  #  col('workspace_id').cast("string"), 
                   col('dbus')
                  ).withColumn("sku",
                    when(col("sku").contains("ALL_PURPOSE"), "ALL_PURPOSE")
                    .when(col("sku").contains("JOBS"), "JOBS")
                    .when(col("sku").contains("DLT"), "DLT")
                    .when(col("sku").contains("SQL"), "SQL")
                    .when(col("sku").contains("INFERENCE"), "MODEL_INFERENCE")
                    .otherwise("OTHER"))
    
    group_df = (
      df
      # .groupBy(col("ds"), col('sku'), col('workspace_id'))
      .groupBy(col("ds"), col('sku'))
      .agg(sum('dbus').cast('float').alias("y"))
      )
      
    # filter out sku/workspaces with not enough data
    # prophet requires at least 2 rows, we will arbitrarily use 10 rows as min
    # out = group_df.groupBy("sku", "workspace_id").count().filter("count > 10").join(group_df, on=["sku", "workspace_id"], how="inner").drop('count')
    out = group_df.groupBy("sku").count().filter("count > 10").join(group_df, on=["sku"], how="inner").drop('count')
    
    return out

  def create_forecast_view(self, catalog, schema, input_table='dbu_forecasts'):
    """
    Forecast Reporting view for consolidated sku i.e. ALL_PURPOSE, SQL, DLT
    """
    return self.spark.sql(f"""
        create view if not exists {catalog}.{schema}.vw_dbu_forecasts
        as 
        with forecasts as (
        select 
        f.ds as date
        --, workspace_id
        , f.sku
        , f.y 
        , GREATEST(0, f.yhat) as yhat
        , GREATEST(0, f.yhat_lower) as yhat_lower
        , GREATEST(0, f.yhat_upper) as yhat_upper
        , f.y > f.yhat_upper as upper_anomaly_alert
        , f.y < f.yhat_lower as lower_anomaly_alert
        , f.y >= f.yhat_lower AND f.y <= f.yhat_upper as on_trend
        , f.training_date
        
        from {catalog}.{schema}.{input_table} as f
        ) 

        select 
        `date`
        --, workspace_id
        , sku
        , y
        , yhat
        , yhat_lower
        , yhat_upper
        , upper_anomaly_alert
        , lower_anomaly_alert
        , on_trend
        , avg(yhat) OVER (PARTITION BY sku ORDER BY date ROWS BETWEEN 7 PRECEDING AND 7 FOLLOWING) AS smoothed_yhat
        , avg(yhat_upper) OVER (PARTITION BY sku ORDER BY date ROWS BETWEEN 7 PRECEDING AND 7 FOLLOWING) AS smoothed_yhat_upper
        , avg(yhat_lower) OVER (PARTITION BY sku ORDER BY date ROWS BETWEEN 7 PRECEDING AND 7 FOLLOWING) AS smoothed_yhat_lower
        , training_date

        from forecasts 

    """)


