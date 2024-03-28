from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import logging 
from libs.db_sql_connect import DBSQLClient
from libs.db_ai_client import DBAIClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

db_conn = DBSQLClient()
db_ai_client = DBAIClient()
actuals = db_conn.get_actual_values()
df = pd.DataFrame(actuals)
sku_options = ['All', 'ALL_PURPOSE', 'MODEL_INFERENCE','SQL','DLT','JOBS']
prev_val = 'All'



app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='Time Series AI', style={'textAlign':'center'}),
    dcc.Dropdown(sku_options, 'All', id='dropdown-selection'),
    html.Button('Generate Forecasts', id='generate-forecasts-button', n_clicks=0),  
    html.Button('Analyze Forecasts', id='generate-analysis-button', n_clicks=0),  
    dcc.Graph(id='graph-content'),
    html.Div(id='graph-text', children='To analyze data with AI please click "Analyze"....', style={'textAlign': 'center','white-space': 'pre-wrap'})

])

@callback(
    Output('graph-content', 'figure'),
   [Input('dropdown-selection', 'value'),
    Input('generate-forecasts-button', 'n_clicks')
    ]
)
def update_graph(value, n_clicks):
    if n_clicks == 0:
        actuals = db_conn.get_actual_values(sku=value)
        df = pd.DataFrame(actuals)
        return px.line(df, x='Date', y='y')
    else :
        logger.info(f"Dropdown Click Count = {n_clicks}")
        db_ai_client.reset_messages()
        forecasts = db_conn.get_forecast_values(sku=value)
        df = pd.DataFrame(forecasts)
        return px.line(df, x='Date', y=['y', 'yhat','yhat_upper', 'yhat_lower'])


@app.callback(
    Output('graph-text', 'children'),  # Update the text below the graph
    [Input('generate-analysis-button', 'n_clicks'), Input('dropdown-selection', 'value')]
)
def update_text(n_clicks, value):
    logger.info(f'Rendering New Text {n_clicks}')
    global prev_val
    if n_clicks and value==prev_val:
        logger.info(f"Text Click Count = {n_clicks}")
        model_forecasts = db_conn.get_forecast_values(sku=value)
        model_eval = db_conn.get_model_eval(sku=value)
        db_ai_client.add_message(model_forecasts, model_eval, sku=value)
        response = db_ai_client.send_chat()
        # Return updated text when button is clicked
        text = response.get('choices')[0].get('message').get('content')
        prev_val = value
        return text
    else:
        logger.info("Not rendering analysis. ")
        # Default text
        prev_val = value
        return 'To analyze data with AI please click "Analyze Forecasts"....'



if __name__ == '__main__':
    app.run(debug=True)
