import requests 
import json
from dotenv import load_dotenv
import os
import logging
import pandas as pd


# https://docs.databricks.com/en/large-language-models/llm-serving-intro.html
# https://learn.microsoft.com/en-us/azure/databricks/machine-learning/foundation-models/api-reference
# https://learn.microsoft.com/en-us/azure/databricks/machine-learning/foundation-models/api-reference#chat-message

# Load environment variables from .env file
load_dotenv()

class DBAIClient():
    def __init__(self):
        # Access an environment variable
        self.dbtoken = os.getenv('DATABRICKS_TOKEN')
        self.db_workspace = os.environ.get('DATABRICKS_WORKSPACE')
        # self.endpoint_url = f"https://{self.db_workspace}/serving-endpoints/databricks-llama-2-70b-chat/invocations"
        self.endpoint_url = f"https://{self.db_workspace}/serving-endpoints/databricks-dbrx-instruct/invocations"
        self.reset_messages()

    def send_chat(self):
        payload = {"messages": self.messages}
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.endpoint_url, headers=headers, json=payload, auth=("token", self.dbtoken))
        logging.info(msg=response.text)
        return json.loads(response.content.decode('utf-8'))

    def compile_message(self, model_forecasts, model_eval, sku):
        forecast_pdf = pd.DataFrame(model_forecasts)

        # Get trend alerts
        yhat_above_upper = forecast_pdf[forecast_pdf['y'] > forecast_pdf['yhat_upper']]
        yhat_below_lower = forecast_pdf[forecast_pdf['y'] < forecast_pdf['yhat_lower']]
        num_upper_alerts = str(len(yhat_above_upper))
        num_lower_alerts = str(len(yhat_below_lower))

        if sku != 'All':
            rmse = model_eval[0].get('rmse')
            mae = model_eval[0].get('mae')
            mse = model_eval[0].get('mse')

            msg = f"We have observed that there are {num_upper_alerts} occurences where the y value was above the upper threshold (yhat_upper) and {num_lower_alerts} occurrences where the y value was below the lower threshold (yhat_lower). Additionally, the {sku} sku has the following metrics: MAE = {mae}, RMSE = {rmse}, and MSE = {mse}"
        else :
            msg = f"We have observed that there are {num_upper_alerts} occurences where the y value was above the upper threshold (yhat_upper) and {num_lower_alerts} occurrences where the y value was below the lower threshold (yhat_lower). "



        return ('user', msg)

    def add_message(self, model_forecasts, model_eval, sku):
        role, text = self.compile_message(model_forecasts, model_eval, sku)
        
        msg = {
            "role": role,
            "content": text
        }
        self.messages.append(msg)


    def reset_messages(self):
        self.messages = [
            {
            "role": "system",
            "content": "We need a concise overview of the time series data with your statistical opinion and potential future trends. Do not provide recommendations to improve the model. Our focus should be on extracting key insights without overwhelming the reader. In this analysis, we'll primarily look at the observed (actual) values represented by 'y' and compare them with the model's predictions denoted by 'yhat'. Additionally, we'll examine the prediction interval, defined by 'yhat_lower' and 'yhat_upper', which indicates the range within which the predicted values are expected to fall with a certain level of confidence. Let's emphasize the significance of the Mean Absolute Error (MAE), Mean Squared Error (MSE), and Root Mean Squared Error (RMSE) metrics. These metrics quantify the discrepancies between predicted and actual values, providing essential insights into the performance of our model. MAE captures the average magnitude of errors, MSE measures the average squared differences, and RMSE serves as a measure of the standard deviation of the residuals. Do not ask any follow up questions. If you use bullet points, please do so with '-'. "
            }
        ]


