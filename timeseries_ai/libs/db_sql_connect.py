from databricks import sql 
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


class DBSQLClient():
    def __init__(self):
        # Access an environment variable
        self.dbtoken = os.getenv('DATABRICKS_TOKEN')
        self.server_hostname = os.environ.get('DATABRICKS_WORKSPACE')
        self.http_path = os.environ.get('WAREHOUSE_HTTP_PATH')

        
    def execute_query(self, query):
        with sql.connect(server_hostname=self.server_hostname, 
                        http_path=self.http_path, 
                        access_token=self.dbtoken) as connection:
            
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()

        return result


    def get_schemas(self):
        return self.execute_query("SHOW SCHEMAS")


    def get_forecast_values(self, sku='All', catalog_name='rac_demo_catalog', schema_name='default', table_name='vw_dbu_forecasts'):
        assert sku in ['All', 'ALL_PURPOSE', 'MODEL_INFERENCE','SQL','DLT','JOBS']
        query_string = f"""
            select date, sum(yhat) as yhat, sum(yhat_lower) as yhat_lower, sum(yhat_upper) as yhat_upper, sum(y) as y
            from {catalog_name}.{schema_name}.{table_name}
            """
        if sku != 'All':
            query_string += f" where sku = '{sku}'"

        query_string += " group by all"
        query_string += " order by date desc"
        

        results = self.execute_query(query=query_string)
        return [{'Date': r.date, 'y': r.y, 'yhat': r.yhat, 'yhat_lower': r.yhat_lower, 'yhat_upper': r.yhat_upper} for r in results]



    def get_actual_values(self, sku='All', catalog_name='rac_demo_catalog', schema_name='default', table_name='vw_dbu_forecasts'):
        assert sku in ['All', 'ALL_PURPOSE', 'MODEL_INFERENCE','SQL','DLT','JOBS']
        query_string = f"""
            select date, sum(y) as y
            from {catalog_name}.{schema_name}.{table_name}
            """
        if sku != 'All':
            query_string += f" where sku = '{sku}'"

        query_string += " group by all"
        query_string += " order by date desc"
        

        results = self.execute_query(query=query_string)
        return [{'Date': r.date, 'y': r.y} for r in results]
