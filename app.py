import os
import time
import concurrent.futures
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import requests
from dotenv import load_dotenv
from io import StringIO
from os import listdir
from os.path import isfile, join
import dash_table
from concurrent.futures import wait, ALL_COMPLETED
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from whitenoise import WhiteNoise


load_dotenv()
API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
STOCK_DATA_FOLDER = os.environ.get("STOCKS_DATA_FOLDER")
CRYPTO_CURRENCY_DATA_FOLDER = os.environ.get("CRYPTO_CURRENCY_DATA_FOLDER")
HRYVNIA_CURRENCY_DATA_FOLDER = os.environ.get("HRYVNIA_CURRENCY_DATA_FOLDER")

ALPHA_VANTAGE_BASE_QUERY_URL = "http://www.alphavantage.co/query"
API_CALL_SLEEP_SEC = 60

STOCKS = {
    "Alibaba": "BABA",
    "Alphabet": "GOOGL",
    "Amazon": "AMZN",
    "Apple": "AAPL",
    "Facebook": "FB",
    "Microsoft": "MSFT",
    "Netflix": "NFLX",
    "Oracle": "ORCL",
    "Tesla": "TSLA",
    "Twitter": "TWTR"
}

CRYPTO_CURRENCIES = {
    "Bitcoin": "BTC",
    "EOS.IO": "EOS",
    "Ethereum": "ETH",
    "Neo": "NEO",
    "Ripple": "XRP"
}

HRYVNIA_CURRENCY = {
    "United States Dollar": "USD",
    "Euro": "EUR",
    # "Polish Zloty": "PLN",
    "Japanese Yen": "JPY",
    "British Pound Sterling": "GBP"
}

stocks = []
crypto = []
hryvnia = []


def load_stocks_data_from_files():
    csv_files = [
        f for f in listdir(STOCK_DATA_FOLDER) if (isfile(join(STOCK_DATA_FOLDER, f)) and f.endswith(".csv"))]

    stock_file_path = join(STOCK_DATA_FOLDER, csv_files[0])
    row_data = pd.read_csv(stock_file_path, nrows=10)  # todo move to settings
    row_data = row_data.drop(columns=["Unnamed: 0"])
    row_data.insert(0, "name", csv_files[0].split('.')[0])
    stocks_data = row_data

    for index, stock_file in enumerate(csv_files):
        if index == 0:
            continue

        stock_file_path = join(STOCK_DATA_FOLDER, stock_file)
        row_data = pd.read_csv(stock_file_path, nrows=10)  # todo move to settings
        row_data = row_data.drop(columns=["Unnamed: 0"])
        row_data.insert(0, "name", stock_file.split('.')[0])

        stocks_data = pd.concat([stocks_data, row_data[0:10]])   # todo move to settings

    return stocks_data


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
server.wsgi_app = WhiteNoise(server.wsgi_app, root='static/')

app.layout = html.Div(children=[
    dcc.Tabs([
        dcc.Tab(label="Stock Price", children=[
            html.Div([
                html.Div([
                    dbc.Button("Update stock data",
                               id="update-stock",
                               style={
                                   'margin': 20
                               }),
                    dbc.Spinner(html.Div(id="stock-loading-output", style={'margin': 20, 'font-style': 'italic'}))
                ]),
                html.Div([
                    html.Label("Select parameter: "),
                    dcc.Dropdown(
                        id='stock-yaxis')
                    ]),
            ],
                style={'width': '25%', 'display': 'inline-block', 'margin': 20}),
            html.Div([
                dcc.Graph(
                    id='stock-graph',
                ),

                dash_table.DataTable(
                    id='stock-table',
                    filter_action='native',
                    style_table={
                        'height': 400,
                    },
                    style_data={
                        'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis'
                    }
                )
            ])
        ]),
        dcc.Tab(label="Crypto Currencies Price", children=[
            html.Div([
                html.Div([
                    dbc.Button("Update crypto currencies data",
                               id="update-crypto",
                               style={
                                   'margin': 20
                               }),
                    dbc.Spinner(html.Div(id="crypto-loading-output", style={'margin': 20, 'font-style': 'italic'})),
                ]),

                html.Div([
                    html.Label("Select parameter: "),
                    dcc.Dropdown(
                        id='crypto-yaxis'
                    )
                ],
                    style={'width': '25%', 'display': 'inline-block', 'margin': 20})
            ]),
            html.Div([
                dcc.Graph(
                    id='crypto-graph'
                ),

                dash_table.DataTable(
                    id='crypto-table',
                    filter_action='native',
                    style_table={
                        'height': 400,
                    },
                    style_data={
                        'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis'
                    }
                )
            ])
        ]),
        dcc.Tab(label="Ukrainian Hryvnia", children=[
            html.Div([
                html.Div([
                    dbc.Button("Update hryvnia currencies data",
                               id="update-hryvnia",
                               style={
                                   'margin': 20
                               }),
                    dbc.Spinner(html.Div(id="hryvnia-loading-output", style={'margin': 20, 'font-style': 'italic'})),
                ]),

                html.Div([
                    html.Label("Select parameter: "),
                    dcc.Dropdown(
                        id='hryvnia-yaxis'
                    )
                ],
                    style={'width': '25%', 'display': 'inline-block', 'margin': 20})

            ]),
            html.Div([
                dcc.Graph(
                    id='hryvnia-graph'
                ),

                dash_table.DataTable(
                    id='hryvnia-table',
                    filter_action='native',
                    style_table={
                        'height': 400,
                    },
                    style_data={
                        'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis'
                    }
                )
            ])
        ]),
    ])
])

if __name__ == '__main__':
    session = requests.Session()

    if not API_KEY:
        raise Exception("Can't load ALPHA_VANTAGE_API_KEY")

    # if not os.path.exists(STOCK_DATA_FOLDER):
    #     os.makedirs(STOCK_DATA_FOLDER)
    #     load_stock_data()
    #
    # if not os.path.exists(CRYPTO_CURRENCY_DATA_FOLDER):
    #     os.makedirs(CRYPTO_CURRENCY_DATA_FOLDER)
    #     load_crypto_currency_data()
    #
    # if not os.path.exists(HRYVNIA_CURRENCY_DATA_FOLDER):
    #     os.makedirs(HRYVNIA_CURRENCY_DATA_FOLDER)
    #     load_hryvnia_currency_data()

    stocks = load_stocks_data_from_files()

    app.run_server(debug=False)
