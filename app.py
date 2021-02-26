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


# load_dotenv()
# API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
# STOCK_DATA_FOLDER = os.environ.get("STOCKS_DATA_FOLDER")
# CRYPTO_CURRENCY_DATA_FOLDER = os.environ.get("CRYPTO_CURRENCY_DATA_FOLDER")
# HRYVNIA_CURRENCY_DATA_FOLDER = os.environ.get("HRYVNIA_CURRENCY_DATA_FOLDER")

API_KEY = "C9OM4S936JARE0JM"
STOCK_DATA_FOLDER = "static/stocks/"
CRYPTO_CURRENCY_DATA_FOLDER = "static/crypto/"
HRYVNIA_CURRENCY_DATA_FOLDER = "static/hryvnia/"

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

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server
server.wsgi_app = WhiteNoise(server.wsgi_app, root='static/')

stocks = []
crypto = []
hryvnia = []


def get_stock_data(session, name, symbol, api_key, function, datatype):
    params = {
        "function": function,
        "symbol": symbol,
        "apikey": api_key,
        "datatype": datatype
    }

    print(f"Getting monthly stock data for {name}")

    response = session.get(ALPHA_VANTAGE_BASE_QUERY_URL, params=params)  # may use request instead of session

    if "5 calls per minute and 500 calls per day" in response.text:
        print("5 calls per minute were exceeded. Waiting for 1 minute...")
        time.sleep(API_CALL_SLEEP_SEC)
        response = session.get(ALPHA_VANTAGE_BASE_QUERY_URL, params=params)

    if response.status_code == requests.codes.ok:
        df = pd.read_csv(StringIO(response.text))
        df.to_csv(os.path.join(
            os.path.dirname(__file__),
            f"{STOCK_DATA_FOLDER}/{name}.csv"
        ))

        print(f"data for {name} was downloaded")
    else:
        raise Exception(response.status_code, response.reason)


def get_crypto_currency_data(session, name, symbol, market, api_key, function, datatype):
    params = {
        "function": function,
        "symbol": symbol,
        "market": market,
        "apikey": api_key,
        "datatype": datatype
    }

    print(f"Getting monthly digital currency data for {name}")

    response = session.get(ALPHA_VANTAGE_BASE_QUERY_URL, params=params)  # may use request instead of session

    if "5 calls per minute and 500 calls per day" in response.text:
        print("5 calls per minute were exceeded. Waiting for 1 minute...")
        time.sleep(API_CALL_SLEEP_SEC)
        response = session.get(ALPHA_VANTAGE_BASE_QUERY_URL, params=params)

    if response.status_code == requests.codes.ok:
        df = pd.read_csv(StringIO(response.text))
        df.to_csv(os.path.join(
            os.path.dirname(__file__),
            f"{CRYPTO_CURRENCY_DATA_FOLDER}/{name}.csv"
        ))

        print(f"data for {name} was downloaded")
    else:
        raise Exception(response.status_code, response.reason)


def get_hryvnia_currency_data(session, name, from_symbol, to_symbol, api_key, function, datatype):
    params = {
        "function": function,
        "from_symbol": from_symbol,
        "to_symbol": to_symbol,
        "apikey": api_key,
        "datatype": datatype
    }

    print(f"Getting monthly hryvnia currency data for {name}")

    response = session.get(ALPHA_VANTAGE_BASE_QUERY_URL, params=params)  # may use request instead of session

    if "5 calls per minute and 500 calls per day" in response.text:
        print("5 calls per minute were exceeded. Waiting for 1 minute...")
        time.sleep(API_CALL_SLEEP_SEC)
        response = session.get(ALPHA_VANTAGE_BASE_QUERY_URL, params=params)

    if response.status_code == requests.codes.ok:
        df = pd.read_csv(StringIO(response.text))
        df.to_csv(os.path.join(
            os.path.dirname(__file__),
            f"{HRYVNIA_CURRENCY_DATA_FOLDER}/{name}.csv"
        ))

        print(f"data for {name} was downloaded")
    else:
        raise Exception(response.status_code, response.reason)


# currently not used !!!
def load_stocks_minimum_data_from_files():
    csv_files = [
        f for f in listdir(STOCK_DATA_FOLDER) if (isfile(join(STOCK_DATA_FOLDER, f)) and f.endswith(".csv"))]

    row_data = pd.read_csv(join(STOCK_DATA_FOLDER, csv_files[0]), usecols=["timestamp"])
    stocks_data = row_data[0:10]  # todo move to settings

    for index, stock_file in enumerate(csv_files):
        stock_file_path = join(STOCK_DATA_FOLDER, stock_file)
        row_data = pd.read_csv(stock_file_path, usecols=["close"])
        stocks_data[stock_file] = row_data[0:10]  # todo move to settings

    return stocks_data


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


def load_crypto_currencies_data_from_files():
    csv_files = [
        f for f in listdir(CRYPTO_CURRENCY_DATA_FOLDER) if (isfile(join(CRYPTO_CURRENCY_DATA_FOLDER, f))
                                                            and f.endswith(".csv"))]

    crypto_currency_file_path = join(CRYPTO_CURRENCY_DATA_FOLDER, csv_files[0])
    row_data = pd.read_csv(crypto_currency_file_path, nrows=10)  # todo move to settings
    row_data = row_data.drop(columns=["Unnamed: 0"])
    row_data.insert(0, "name", csv_files[0].split('.')[0])
    crypto_currency_data = row_data

    for index, crypto_currency_file in enumerate(csv_files):
        if index == 0:
            continue

        crypto_currency_file_path = join(CRYPTO_CURRENCY_DATA_FOLDER, crypto_currency_file)
        row_data = pd.read_csv(crypto_currency_file_path, nrows=10)  # todo move to settings
        row_data = row_data.drop(columns=["Unnamed: 0"])
        row_data.insert(0, "name", crypto_currency_file.split('.')[0])

        crypto_currency_data = pd.concat([crypto_currency_data, row_data[0:10]])   # todo move to settings

    return crypto_currency_data


def load_hryvnia_data_from_files():
    csv_files = [
        f for f in listdir(HRYVNIA_CURRENCY_DATA_FOLDER) if (isfile(join(HRYVNIA_CURRENCY_DATA_FOLDER, f))
                                                             and f.endswith(".csv"))]

    hryvnia_currency_file_path = join(HRYVNIA_CURRENCY_DATA_FOLDER, csv_files[0])
    row_data = pd.read_csv(hryvnia_currency_file_path, nrows=10)  # todo move to settings
    row_data = row_data.drop(columns=["Unnamed: 0"])
    row_data.insert(0, "name", csv_files[0].split('.')[0])
    hryvnia_currency_data = row_data

    for index, stock_file in enumerate(csv_files):
        if index == 0:
            continue

        hryvnia_currency_file_path = join(HRYVNIA_CURRENCY_DATA_FOLDER, stock_file)
        row_data = pd.read_csv(hryvnia_currency_file_path, nrows=10)  # todo move to settings
        row_data = row_data.drop(columns=["Unnamed: 0"])
        row_data.insert(0, "name", stock_file.split('.')[0])

        hryvnia_currency_data = pd.concat([hryvnia_currency_data, row_data[0:10]])   # todo move to settings

    return hryvnia_currency_data


def make_layout(stocks, crypto, hryvnia):
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
                            id='stock-yaxis',
                            options=[{"label": i, "value": i} for i in stocks.columns[2:]],
                            value=stocks.columns[2])
                        ]),
                ],
                    style={'width': '25%', 'display': 'inline-block', 'margin': 20}),
                html.Div([
                    dcc.Graph(
                        id='stock-graph',
                    ),

                    dash_table.DataTable(
                        id='stock-table',
                        columns=[{"name": i, "id": i} for i in stocks.columns],
                        data=stocks.to_dict('records'),
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
                            id='crypto-yaxis',
                            options=[{"label": i, "value": i} for i in crypto.columns[2:]],
                            value=crypto.columns[3]
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
                        columns=[{"name": i, "id": i} for i in crypto.columns],
                        data=crypto.to_dict('records'),
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
                            id='hryvnia-yaxis',
                            options=[{"label": i, "value": i} for i in hryvnia.columns[2:]],
                            value=hryvnia.columns[3]
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
                        columns=[{"name": i, "id": i} for i in hryvnia.columns],
                        data=hryvnia.to_dict('records'),
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


@app.callback(
    Output('stock-graph', 'figure'),
    Input('stock-yaxis', 'value'),
)
def update_stock_graph(yaxis_column_name):
    fig = px.line(stocks, x="timestamp", y=yaxis_column_name, color="name")
    return fig


@app.callback(
    Output("stock-loading-output", "children"),
    [Input("update-stock", "n_clicks")]
)
def update_stock(n):
    if n:
        load_stock_data()
        global stocks
        stocks = load_stocks_data_from_files()
        return "Stock data were updated, please reload the page"


@app.callback(
    Output('crypto-graph', 'figure'),
    Input('crypto-yaxis', 'value'),
)
def update_crypto_graph(yaxis_column_name):
    fig = px.line(crypto, x="timestamp", y=yaxis_column_name, color="name")
    return fig


@app.callback(
    Output("crypto-loading-output", "children"),
    [Input("update-crypto", "n_clicks")]
)
def update_crypto(n):
    if n:
        load_crypto_currency_data()
        global crypto
        crypto = load_crypto_currencies_data_from_files()
        return "Crypto currencies data were updated, please reload the page"


@app.callback(
    Output('hryvnia-graph', 'figure'),
    Input('hryvnia-yaxis', 'value'),
)
def update_hryvnia_graph(yaxis_column_name):
    fig = px.line(hryvnia, x="timestamp", y=yaxis_column_name, color="name")
    return fig


@app.callback(
    Output("hryvnia-loading-output", "children"),
    [Input("update-hryvnia", "n_clicks")]
)
def update_hryvnia(n):
    if n:
        load_hryvnia_currency_data()
        global hryvnia
        hryvnia = load_hryvnia_data_from_files()
        return "Hryvnia currencies data were updated, please reload the page"


def load_stock_data():
    _args = (
        (session, name, symbol, API_KEY, "TIME_SERIES_MONTHLY", "csv")
        for name, symbol in STOCKS.items()
    )

    with concurrent.futures.ThreadPoolExecutor() as pool:
        futures = [pool.submit(get_stock_data, *args) for args in _args]
        wait(futures, timeout=130, return_when=ALL_COMPLETED)

    print("done")


def load_crypto_currency_data():
    _args = (
        (session, name, symbol, "USD", API_KEY, "DIGITAL_CURRENCY_MONTHLY", "csv")
        for name, symbol in CRYPTO_CURRENCIES.items()
    )

    with concurrent.futures.ThreadPoolExecutor() as pool:
        futures = [pool.submit(get_crypto_currency_data, *args) for args in _args]
        wait(futures, timeout=130, return_when=ALL_COMPLETED)

    print("done")


def load_hryvnia_currency_data():
    _args = (
        (session, name, from_symbol, "UAH", API_KEY, "FX_MONTHLY", "csv")
        for name, from_symbol in HRYVNIA_CURRENCY.items()
    )

    with concurrent.futures.ThreadPoolExecutor() as pool:
        futures = [pool.submit(get_hryvnia_currency_data, *args) for args in _args]
        wait(futures, timeout=130, return_when=ALL_COMPLETED)

    print("done")


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
    crypto = load_crypto_currencies_data_from_files()
    hryvnia = load_hryvnia_data_from_files()

    make_layout(stocks, crypto, hryvnia)

    app.run_server(debug=False)

