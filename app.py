import os
import re
import dash
from datetime import datetime
from dash import  Dash, Input, Output, dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
import numpy as np
from dash import Input, Output
from plotly.subplots import make_subplots
import random
import pickle
pd.set_option('mode.chained_assignment', None)

datafolder = "data/"

QUERY = """
SELECT {}
FROM {}
{}
"""

def curtime():
    return datetime.strftime(datetime.utcnow(), "%Y-%m-%d %H:%M")


def load_chart(chartname):    
    with open(datafolder + chartname, "rb") as file:
        fig = pickle.load(file)
    return fig

inclusion_delay_chart = load_chart("chart_inclusion_delay")
inclusion_delay_chart_mobile = load_chart("chart_inclusion_delay_mobile")
sankey_chart = load_chart("chart_sankey")
sankey_chart_mobile = load_chart("chart_sankey_mobile")
xof_over_time_chart = load_chart("chart_xof_over_time")
xof_over_time_chart_mobile = load_chart("chart_xof_over_time_mobile")
xof_builder_chart = load_chart("chart_xof_builder")
xof_builder_chart_mobile = load_chart("chart_xof_builder_mobile")
xof_over_time_builder_chart = load_chart("chart_xof_over_time_builder")
xof_over_time_builder_chart_mobile = load_chart("chart_xof_over_time_builder_mobile")
xof_users_chart = load_chart("chart_xof_users")
xof_users_chart_mobile = load_chart("chart_xof_users_mobile")

xof_builder_mev_type_chart = load_chart("chart_xof_builder_mev_type")
xof_builder_mev_type_chart_mobile = load_chart("chart_xof_builder_mev_type_mobile")

mev_type_over_time_chart = load_chart("chart_mev_type_over_time")
mev_type_over_time_chart_mobile = load_chart("chart_mev_type_over_time_mobile")

xof_types_users_chart = load_chart("chart_xof_types_users")
xof_types_users_chart_mobile = load_chart("chart_xof_types_users_mobile")


BLACK = "rgb(26, 25, 25)"
BLACK_ALPHA = "rgba(26, 25, 25, {})"


# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-M7PME47SDC"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', 'G-M7PME47SDC');
        </script>
        <meta charset="UTF-8">
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:site" content="@nero_ETH">
        <meta name="twitter:title" content="Ethereum mempool Dashboard">
        <meta name="twitter:description" content="Selected comparative visualizations on Ethereum's mempool.">
        <meta name="twitter:image" content="https://raw.githubusercontent.com/nerolation/mempool.pics/main/assets/mempool.png">
        <meta property="og:title" content="mempool.pics" relay="" api="" dashboard="">
        <meta property="og:site_name" content="mempool.pics">
        <meta property="og:url" content="mempool.pics">
        <meta property="og:description" content="Selected comparative visualizations on Ethereum's mempool.">
        <meta property="og:type" content="website">
        <link rel="shortcut icon" href="https://raw.githubusercontent.com/nerolation/mempool.pics/main/assets/mempool.png">
        <meta property="og:image" content="https://raw.githubusercontent.com/nerolation/mempool.pics/main/assets/mempool.png">
        <meta name="description" content="Selected comparative visualizations on Ethereum's mempool.">
        <meta name="keywords" content="Ethereum, mempool, Dashboard">
        <meta name="author" content="Toni Wahrstätter">
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''
app.scripts.append_script({"external_url": "update_window_width.js"})
app.clientside_callback(
    "window.dash_clientside.update_window_size",
    Output('window-size-store', 'data'),
    Input('window-size-trigger', 'n_intervals')
)
app.title = 'Mempool.pics'
server = app.server

def table_styles(width):
    font_size = '20px' if width >= 800 else '10px'

    return [
        {'if': {'column_id': 'Slot Nr. in Epoch'}, 'maxWidth': '30px', 'textAlign': 'center', 'fontSize': font_size},
        {'if': {'column_id': 'Slot'}, 'textAlign': 'right', 'maxWidth': '40px', 'fontSize': font_size},
        {'if': {'column_id': 'Parent Slot'}, 'textAlign': 'center', 'maxWidth': '40px', 'fontSize': font_size},
        {'if': {'column_id': 'Val. ID'}, 'maxWidth': '30px', 'fontSize': font_size},
        {'if': {'column_id': 'Date'}, 'maxWidth': '80px', 'fontSize': font_size},
        {'if': {'column_id': 'CL Client'}, 'maxWidth': '80px', 'fontSize': font_size}
    ]



app.layout = html.Div(
    [
        dbc.Container(
        [
            # Title
            dbc.Row(html.H1("Ethereum Mempool Dashboard", style={'textAlign': 'center', 'marginTop': '20px', 'color': '#2c3e50', 'fontFamily': 'Ubuntu Mono, monospace', 'fontWeight': 'bold'}), className="mb-4"),
            
            html.Div([
                dbc.Row([
                    dbc.Col(
                        html.H5(
                             ['Built with 🖤 by ', html.A('Toni Wahrstätter', href='https://twitter.com/nero_eth', target='_blank'), html.Br(), ''],
                            className="mb-4 even-smaller-text", # Apply the class
                            style={'color': '#262525', 'fontFamily': 'Ubuntu Mono, monospace'}
                        ),
                        width={"size": 6, "order": 1}
                    ),

                ], className="animated fadeInUp", style={"marginBottom": "0px", "paddingBottom": "0px", 'backgroundColor': '#eee', 'fontFamily': 'Ubuntu Mono, monospace'}),
            ]),
            
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.H4("What is the mempool?", style={'textAlign': 'left', 'color': '#2c3e50', 'fontFamily': 'Ubuntu Mono, monospace'}),
                        dcc.Markdown("""

**The mempool**, also known as the txpool, is essentially a collection of pending transactions that each Ethereum node maintains locally. Unlike a single, universal mempool containing all unconfirmed transactions, each node has its own unique set of pending transactions. These transactions are then shared with other nodes on the network. When a transaction is shared, it becomes publicly visible, allowing various parties to potentially benefit from this information. For example, some may use it to extract Miner Extractable Value (MEV). The quality of a node's view into the public mempool improves with the number of its connections and the quality of those connections.
""", style={'textAlign': 'left', 'color': '#262525', 'fontFamily': 'Ubuntu Mono, monospace'}),
                    ], className="mb-2 even-even-smaller-text", md=6),

                    dbc.Col([
                        html.H4("What is private orderflow", style={'textAlign': 'left', 'color': '#2c3e50', 'fontFamily': 'Ubuntu Mono, monospace'}),
                         dcc.Markdown(f"""**Private Orderflow** refers to transactions that are not broadcasted over the public P2P network. Instead, these transactions are sent directly to the block builder. This approach requires a secure communication P2P network but directly submitted to a block builder. For the data presented on this website, [Blocknative's public mempool data](https://docs.blocknative.com/mempool-data-program) was used to identify transactions that have been publicly broadcasted over the P2P network. To tell if a tx is a frontrun, backrun, arb, etc. the [ZeroMev API](https://info.zeromev.org/api.html) was used.\n\nLast data update: {curtime()}""", 
                                      style={'textAlign': 'left', 'color': '#262525','fontFamily': 'Ubuntu Mono, monospace'}),
                    ], className="mb-2 even-even-smaller-text", md=6)
                ])
            ], className="mb-2 p-3 rounded", style={'backgroundColor': '#eee'}),
          

            dbc.Row(dbc.Col(dcc.Graph(id='xof_over_time_graph', figure=xof_over_time_chart), md=12, className="mb-4 animated fadeIn")),
            dbc.Row(dbc.Col(dcc.Graph(id='xof_over_time_builder_graph', figure=xof_over_time_builder_chart), md=12, className="mb-4 animated fadeIn")),
            dbc.Row(dbc.Col(dcc.Graph(id='xof_builder_graph', figure=xof_builder_chart), md=12, className="mb-4 animated fadeIn")),
            dbc.Row(dbc.Col(dcc.Graph(id='xof_users_graph', figure=xof_users_chart), md=12, className="mb-4 animated fadeIn")),
            
            dbc.Row(dbc.Col(dcc.Graph(id='xof_builder_mev_type_graph', figure=xof_builder_mev_type_chart), md=12, className="mb-4 animated fadeIn")),
            dbc.Row(dbc.Col(dcc.Graph(id='xof_types_users_chart_graph', figure=xof_types_users_chart), md=12, className="mb-4 animated fadeIn")),
            dbc.Row(dbc.Col(dcc.Graph(id='mev_type_over_time_graph', figure=mev_type_over_time_chart), md=12, className="mb-4 animated fadeIn")),
            
            dbc.Row(dbc.Col(dcc.Graph(id='inclusion_delay_graph', figure=inclusion_delay_chart), md=12, className="mb-4 animated fadeIn")),
            dbc.Row(dbc.Col(dcc.Graph(id='sankeygraph', figure=sankey_chart), md=12, className="mb-4 animated fadeIn")),


            dbc.Row(dcc.Interval(id='window-size-trigger', interval=1000, n_intervals=0, max_intervals=1)),
            dcc.Store(id='window-size-store', data={'width': 800})
        ],
        fluid=True,
        style={"maxWidth": "960px", 'backgroundColor': '#eee'}
    )],
    id='main-div',
    style={
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "center",
        "alignItems": "center",
        "minHeight": "100vh",
        'backgroundColor': '#eee'
    }
)

# Callbacks

    
@app.callback(
    Output('main-div', 'style'),
    Input('window-size-store', 'data')
)
def update_main_div_style_dynamic(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate

    window_width = window_size_data['width']
    if window_width > 800:
        return {'marginRight': '110px', 'marginLeft': '110px'}
    else:
        return {}

@app.callback(
    Output('xof_over_time_graph', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout1(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    if width <= 800:
        return xof_over_time_chart_mobile
    return xof_over_time_chart

@app.callback(
    Output('xof_over_time_builder_graph', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout2(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    print(width)
    if width <= 800:
        return xof_over_time_builder_chart_mobile
    return xof_over_time_builder_chart

@app.callback(
    Output('xof_builder_graph', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout3(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    print(width)
    if width <= 800:
        return xof_builder_chart_mobile
    return xof_builder_chart

@app.callback(
    Output('xof_users_graph', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout4(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    print(width)
    if width <= 800:
        return xof_users_chart_mobile
    return xof_users_chart

@app.callback(
    Output('inclusion_delay_graph', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout5(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    print(width)
    if width <= 800:
        return inclusion_delay_chart_mobile
    return inclusion_delay_chart

@app.callback(
    Output('sankeygraph', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout6(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    print(width)
    if width <= 800:
        return sankey_chart_mobile
    return sankey_chart

@app.callback(
    Output('xof_builder_mev_type_graph', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout7(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    print(width)
    if width <= 800:
        return xof_builder_mev_type_chart_mobile
    return xof_builder_mev_type_chart

@app.callback(
    Output('mev_type_over_time_graph', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout8(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    print(width)
    if width <= 800:
        return mev_type_over_time_chart_mobile
    return mev_type_over_time_chart
    
    
@app.callback(
    Output('xof_types_users_chart_graph', 'figure'),
    Input('window-size-store', 'data')
)
def update_layout9(window_size_data):
    if window_size_data is None:
        raise dash.exceptions.PreventUpdate
    width = window_size_data['width']
    print(width)
    if width <= 800:
        return xof_types_users_chart_mobile
    return xof_types_users_chart
    

if __name__ == '__main__':
    #app.run_server(debug=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)