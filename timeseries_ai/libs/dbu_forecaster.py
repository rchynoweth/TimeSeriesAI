from prophet import Prophet
from pyspark.sql.functions import *
from pyspark.sql.types import * 
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
from math import sqrt



class DBUForecaster():
  """
  Class for DBU Forecasting
  """
  
  def __init__(self, forecast_periods=7, interval_width=0.85, forecast_frequency='d', include_history=True):
    """
    Initilization function

    
    :param forecast_periods: Periods to forecast. Default is 7. 
    :param interval_width: confidence level of min/max thresholds. Default is 0.85
    :param forecast_frequency: frequency of the ds column. Default is daily i.e. 'd'
    :param include_history: whether or not to include history in the output dataframe. Default is True. 
    """
    self.forecast_periods=forecast_periods
    self.forecast_frequency=forecast_frequency
    self.include_history=include_history
    self.interval_width=interval_width
    
    
    # Training output schema 
    self.forecast_result_schema = StructType([
      StructField('ds',DateType()),
      # StructField('workspace_id', StringType()),
      StructField('sku',StringType()),
      StructField('y',FloatType()),
      StructField('yhat',FloatType()),
      StructField('yhat_upper',FloatType()),
      StructField('yhat_lower',FloatType())
      ])
    
    
    # Evaluation output schema 
    self.eval_schema =StructType([
      StructField('training_date', DateType()),
      # StructField('workspace_id', StringType()),
      StructField('sku', StringType()),
      StructField('mae', FloatType()),
      StructField('mse', FloatType()),
      StructField('rmse', FloatType())
      ])
    # Evaluation output schema 
  


  def generate_forecast(self, history_pd):
    """
    Function to generate forecasts 
    """
    # remove missing values (more likely at day-store-item level)
    history_pd = history_pd.dropna()
    
    # train and configure the model
    model = Prophet( interval_width=self.interval_width )
    model.fit( history_pd )

    # make predictions
    future_pd = model.make_future_dataframe(
      periods=self.forecast_periods, 
      freq=self.forecast_frequency, 
      include_history=self.include_history
      )
    forecast_pd = model.predict( future_pd )  
    
    # ASSEMBLE EXPECTED RESULT SET
    # --------------------------------------
    # get relevant fields from forecast
    f_pd = forecast_pd[ ['ds','yhat', 'yhat_upper', 'yhat_lower'] ].set_index('ds')
    
    # get relevant fields from history
    # h_pd = history_pd[['ds','workspace_id','sku','y']].set_index('ds')
    h_pd = history_pd[['ds','sku','y']].set_index('ds')
    
    # join history and forecast
    results_pd = f_pd.join( h_pd, how='left' )
    results_pd.reset_index(level=0, inplace=True)
    
    # get sku & workspace id from incoming data set
    results_pd['sku'] = history_pd['sku'].iloc[0]
    # results_pd['workspace_id'] = history_pd['workspace_id'].iloc[0]

    # return results_pd[ ['ds', 'workspace_id', 'sku', 'y', 'yhat', 'yhat_upper', 'yhat_lower'] ]  
    return results_pd[ ['ds', 'sku', 'y', 'yhat', 'yhat_upper', 'yhat_lower'] ]  



  def evaluate_forecast(self, evaluation_pd):
    """
    Forecast evaluation function. Generates MAE, RMSE, MSE metrics. 
    """
    evaluation_pd = evaluation_pd[evaluation_pd['y'].notnull()]
    # get sku in incoming data set
    training_date = evaluation_pd['training_date'].iloc[0]
    sku = evaluation_pd['sku'].iloc[0]
    # workspace_id = evaluation_pd['workspace_id'].iloc[0]
    
    # calulate evaluation metrics
    mae = mean_absolute_error( evaluation_pd['y'], evaluation_pd['yhat'] )
    mse = mean_squared_error( evaluation_pd['y'], evaluation_pd['yhat'] )
    rmse = sqrt( mse )
    
    # assemble result set
    # results = {'training_date':[training_date], 'workspace_id':[workspace_id], 'sku':[sku], 'mae':[mae], 'mse':[mse], 'rmse':[rmse]}
    results = {'training_date':[training_date], 'sku':[sku], 'mae':[mae], 'mse':[mse], 'rmse':[rmse]}
    return pd.DataFrame.from_dict( results )
  



class ForecastHelper():

  def apply_forecast(forecast_client):
    def apply(df):
      return forecast_client.generate_forecast(df)
    return apply
  

  def score_forecasts(df, forecast_client):
    group_cols = [x for x in list(df.columns) if x not in ['ds','y']]
    print(f"Grouping By the following columns: {group_cols}")
    return (df.groupBy(*group_cols)
              .applyInPandas(ForecastHelper.apply_forecast(forecast_client), schema=forecast_client.forecast_result_schema)
              .withColumn('training_date', current_timestamp() )
              )


  def apply_forecast_eval(forecast_client):
    def apply_eval(df):
      return forecast_client.evaluate_forecast(df)
    return apply_eval
  

  def eval_forecasts(df, forecast_client):
    group_cols = [x for x in list(df.columns) if x not in ['ds', 'y', 'yhat', 'yhat_upper', 'yhat_lower'] ]
    return (df.groupBy(*group_cols)
              .applyInPandas(ForecastHelper.apply_forecast_eval(forecast_client), schema=forecast_client.eval_schema)
              )