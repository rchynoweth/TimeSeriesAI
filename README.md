# TimeSeriesAI

TimeSeriesAI is a demo repository demonstrating how to generate time series forecast and leverage LLMs to generate a statistical analysis and summary of the forecasted values. Since it is a demo the forecasts are generated in batch, but could be done via a REST API if required. Additionally, the LLM behind the scenes is [DBRX](https://www.databricks.com/blog/introducing-dbrx-new-state-art-open-llm), an open source LLM developed by Databricks, and the [Databricks Foundation Model APIs](https://docs.databricks.com/en/machine-learning/foundation-models/index.html). 



## Install and Run Application 

In Databricks you will need to run [run_forecast.py](timeseries_ai/run_forecasts.py) notebook to generate the forecasts which requires access to [Databricks System Billing Tables](https://docs.databricks.com/en/administration-guide/system-tables/billing.html). 

You will likely need to make edits to the [db_sql_connector.py](timeseries_ai/libs/db_sql_connect.py) to read from your tables because I hard coded mine and don't feel like parameterizing them. 

Next you will need to have the following `.env` file to connect to Databricks from your local desktop. 
```
DATABRICKS_TOKEN=<PAT TOKEN>
DATABRICKS_WORKSPACE=<Databricks Workspace URL> #adb-<workspaceid>.<##>.azuredatabricks.net
WAREHOUSE_HTTP_PATH=<SQL Warehouse Path> # /sql/1.0/warehouses/<ID>
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

## User Interface Example

<div style="text-align: center;">
<video src="https://github.com/rchynoweth/TimeSeriesAI/assets/79483287/ca5a5d8c-bf4d-43d1-bcd4-495dc3630514" controls="controls" style="max-width: 730px;"></video>
</div>




