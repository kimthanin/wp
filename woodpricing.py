# import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash

app = dash.Dash(__name__)
server = app.server

scaler, wpgs = {}, {}
wpg = pd.read_csv('wpg.csv')

for c in wpg.Channel.unique():
    scaler[c] = {}
    scaler[c] = StandardScaler()
    wpgs[c] = wpg.loc[wpg.Channel == c].copy()
    wps = wpgs[c][['Baht', 'Ton']]
    scaler[c].fit(wps)
    wpgs[c][['Baht', 'Ton']] = scaler[c].transform(wps)
    wpgs[c] = pd.melt(wpgs[c], var_name='Type', value_name='Value',
                      id_vars=['Zone', 'Channel', 'Year', 'Month'])

# Build App
app.layout = html.Div([
    html.H1("Wood Pricing Strategy"),
    html.Label(["channel", dcc.Dropdown(
        id='channel-dropdown', clearable=False, value='N3NB',
        options=[{'label': c1, 'value': c1} for c1 in wpg.Channel.unique()])
                ]),
    dcc.Graph(id='graph'),
    html.H2("More Graph Comming Soon...."),
    dcc.Graph(id='graph1'),
])


# Define callback to update graph
@app.callback(
    Output('graph', 'figure'),
    [Input("channel-dropdown", "value")]
)
def update_figure(c):
    return px.line(wpgs[c],
                   x='Month', y='Value',
                   facet_row='Type', color='Year')

@app.callback(
    Output('graph1', 'figure'),
    [Input("channel-dropdown", "value")]
)
def update_figure(c):
    return px.line(wpgs[c],
                   x='Month', y='Value',
                   facet_row='Type', color='Year')


if __name__ == '__main__':
    # app.run_server(port=80,debug=True)
    app.run_server(port=80, host='0.0.0.0')
    # waitress-serve --listen="0.0.0.0:80" woodpricing:server
