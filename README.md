# TimeSeriesAI

TimeSeriesAI is a demo repository showcasing time series forecasting and the utilization of LLMs for generating statistical analyses and summaries of forecasted values. Although forecasts are currently generated in batches, integration with a REST API is feasible if needed. The underlying LLM utilized in this demonstration is [DBRX](https://www.databricks.com/blog/introducing-dbrx-new-state-art-open-llm), an open-source LLM developed by Databricks. DBRX is hosted using [Databricks Foundation Model APIs](https://docs.databricks.com/en/machine-learning/foundation-models/index.html). The model is not fine-tuned, but can be done so using various blogs or academic papers providing analysis or research in time series data. For example, the [FB Prophet Paper](https://peerj.com/preprints/3190/) could be a great fine-tuning data point. Please note that I am not sure if there would be legal/copyright restrictions around using certain content. 

<div style="text-align: center;">
<video src="https://github.com/rchynoweth/TimeSeriesAI/assets/79483287/ca5a5d8c-bf4d-43d1-bcd4-495dc3630514" controls="controls" style="max-width: 730px;"></video>
</div>


## Install and Run Application 

In Databricks you will need to run [run_forecast.py](timeseries_ai/run_forecasts.py) notebook to generate the forecasts which requires access to [Databricks System Billing Tables](https://docs.databricks.com/en/administration-guide/system-tables/billing.html). Please use DBR 13.3LTS ML or higher to produce forecasts. 


Next you will need to have the following `.env` file to connect to Databricks from your local desktop. 
```
DATABRICKS_TOKEN=<PAT TOKEN>
DATABRICKS_WORKSPACE=<Databricks Workspace URL> #adb-<workspaceid>.<##>.azuredatabricks.net
WAREHOUSE_HTTP_PATH=<SQL Warehouse Path> # /sql/1.0/warehouses/<ID>
DATABRICKS_CATALOG=<catalog with forecast data>
DATABRICKS_SCHEMA=<schema with forecast data>
```


To run the application locally please execute the following commands. Please note that you will need to comment out the first two lines of the [__init__.py](timeseries_ai/libs/__init__.py) file as it is coupled with the Databricks job that requires PySpark and I do not install
```
# Create environment 
conda create -n timeseriesai python=3.10

conda activate timeseriesai

# install requirements 
pip install -r requirements.txt

# change working directory and run application
cd timeseries_ai

python run_app.py
```

Please note that running "Analyze Forecasts" for "All Skus" is current'y not supported. 

