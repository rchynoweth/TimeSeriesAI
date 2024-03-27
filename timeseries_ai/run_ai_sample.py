# Databricks notebook source
# MAGIC %load_ext autoreload
# MAGIC %autoreload 2

# COMMAND ----------

catalog_name = 'rac_demo_catalog'
schema_name = 'default'

# COMMAND ----------

spark.sql(f'use catalog {catalog_name}')
spark.sql(f'use schema {schema_name}')

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import libraries and create class clients

# COMMAND ----------

import os
import requests 
import json
from libs import *
from pyspark.sql.functions import *

# COMMAND ----------

db_token = os.environ.get("DATABRICKS_TOKEN")
workspace_id = os.environ.get("DATABRICKS_WORKSPACE_ID")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Data

# COMMAND ----------

forecast_df = spark.read.table('vw_dbu_forecasts')
evaluation_df = spark.read.table('dbu_forecast_evaluations')

# COMMAND ----------

# https://learn.microsoft.com/en-us/azure/databricks/machine-learning/foundation-models/api-reference
# https://learn.microsoft.com/en-us/azure/databricks/machine-learning/foundation-models/api-reference#chat-message

endpoint_url = f"https://adb-{workspace_id}.azuredatabricks.net/serving-endpoints/databricks-llama-2-70b-chat/invocations"
print(endpoint_url)

messages = [
        {
            "role": "system",
            "content": "We are analyzing time series data, and you are to provide a summary of the data. The only question you should ask is if the user wants more. Be opinionated but don't over analyze. Please keep in mind the following definitions: 'y' typically refers to the observed or actual values of the dependent variable in a dataset. Representing the predicted values by a model, 'yhat' or ˆy, serves as the estimations of the dependent variable based on the model's parameters. These terms, 'yhat_lower' and 'yhat_upper', denote the lower and upper bounds of the prediction interval respectively, indicating the range within which the predicted values are expected to fall with a certain level of confidence. The Mean Absolute Error (MAE) quantifies the average magnitude of errors between predicted and actual values, calculated by averaging the absolute differences between the two. Mean Squared Error (MSE) measures the average squared differences between predicted and actual values, providing an average of the squared errors. The Root Mean Squared Error (RMSE) is the square root of MSE, serving as a measure of the standard deviation of the residuals and indicating the typical distance between the observed and predicted values."
        },
        {
            "role": "user",
            "content": "Provide a summary where we have the following evaluation statistics for All Purpose Compute in Databricks: MAE = 922.8, MSE=1790209.9, and RMSE = 1337.9873"
        }
    ]


# Define your payload
payload = {
    "messages": messages
}

# "max_tokens": 128

# Define headers
headers = {
    "Content-Type": "application/json"
}

# Make the POST request
response = requests.post(endpoint_url, headers=headers, json=payload, auth=("token", db_token))


messages.append({'role': "assistant", 'content':response.text})
messages.append({'role': 'user', 'content': "Here is a list of my y values for All Purpose compute. Anything to add to your analysis? [2093.39111328125, 3364.405029296875, 4092.28076171875, 3935.21484375, 3584.5498046875, 3308.855224609375, 1811.58203125, 1764.9798583984375, 3104.965087890625, 3061.26123046875, 3342.009033203125, 3736.623779296875, 4280.07177734375, 1834.7059326171875, 1176.6998291015625, 3941.81103515625, 3706.906005859375, 3639.894287109375, 3539.328125, 4323.94482421875, 1689.037353515625, 1743.302490234375, 3474.532470703125, 3773.332763671875, 4049.286376953125, 3308.769287109375, 3186.986328125, 1923.621337890625, 1490.4100341796875, 3270.697509765625, 3473.410888671875, 3681.88330078125, 4323.03759765625, 3143.856689453125, 1538.3724365234375, 1523.0982666015625, 2878.147705078125, 3142.520751953125, 3223.0341796875, 4036.237548828125, 4743.71875, 3250.144775390625, 3234.570068359375, 5239.3466796875, 5725.23681640625, 5575.125, 6706.0859375, 4476.208984375, 2327.784423828125, 1798.3170166015625, 3676.74853515625]"})
payload = {"messages": messages}
response = requests.post(endpoint_url, headers=headers, json=payload, auth=("token", db_token))


# Print the response
print(response.text)


# COMMAND ----------

messages

# COMMAND ----------

a

# COMMAND ----------

# https://docs.databricks.com/en/large-language-models/llm-serving-intro.html
# https://learn.microsoft.com/en-us/azure/databricks/machine-learning/foundation-models/api-reference
# https://learn.microsoft.com/en-us/azure/databricks/machine-learning/foundation-models/api-reference#chat-message
# https://learn.microsoft.com/en-us/azure/databricks/machine-learning/foundation-models/api-reference#chat-message

# COMMAND ----------


