import requests 
import json
from dotenv import load_dotenv
import os


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
        self.endpoint_url = f"https://{self.db_workspace}/serving-endpoints/databricks-llama-2-70b-chat/invocations"
        self.messages = [
            {
            "role": "system",
            "content": "We are analyzing time series data, and you are to provide a summary of the data. Do not ask any questions. Do not respond with bullet points. Be opinionated but don't over analyze. Please keep in mind the following definitions: 'y' typically refers to the observed or actual values of the dependent variable in a dataset. Representing the predicted values by a model, 'yhat' or ˆy, serves as the estimations of the dependent variable based on the model's parameters. These terms, 'yhat_lower' and 'yhat_upper', denote the lower and upper bounds of the prediction interval respectively, indicating the range within which the predicted values are expected to fall with a certain level of confidence. The Mean Absolute Error (MAE) quantifies the average magnitude of errors between predicted and actual values, calculated by averaging the absolute differences between the two. Mean Squared Error (MSE) measures the average squared differences between predicted and actual values, providing an average of the squared errors. The Root Mean Squared Error (RMSE) is the square root of MSE, serving as a measure of the standard deviation of the residuals and indicating the typical distance between the observed and predicted values."
        }
        ]

    def send_chat(self):
        payload = {"messages": self.messages}
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.endpoint_url, headers=headers, json=payload, auth=("token", self.dbtoken))
        return json.loads(response.content.decode('utf-8'))


    def add_message(self):
        msg = {
            "role": "user",
            "content": "Provide a summary where we have the following evaluation statistics for All Purpose Compute in Databricks: MAE = 922.8, MSE=1790209.9, and RMSE = 1337.9873"
        }
        self.messages.append(msg)




