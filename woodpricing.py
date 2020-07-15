import dash
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

scaler,wpgs = {},{}
wpg=pd.read_csv('wpg.csv')
for c in wpg.Channel.unique():
    scaler[c] = {}
    scaler[c] = StandardScaler()
    wpgs[c] = wpg.loc[wpg.Channel==c].copy()
    wps = wpgs[c][['Baht','Ton']]
    scaler[c].fit(wps)
    print(c, scaler[c].mean_)
    wpgs[c][['Baht','Ton']] = scaler[c].transform(wps)
    wpgs[c]=pd.melt(wpgs[c], id_vars=['Zone','Channel','Year','Month'],var_name='Type', value_name='Value')

# Build App
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Wood Pricing Strategy"),
    html.Label(["channel", dcc.Dropdown(
        id='channel-dropdown', clearable=False, value='N3NB',
        options=[{'label': c1, 'value': c1} for c1 in wpg.Channel.unique()])
               ]),
    dcc.Graph(id='graph'),
    html.H2("More Graph Comming Soon..."),
    dcc.Graph(id='graph1'),
])

# Define callback to update graph
@app.callback(
    Output('graph', 'figure'),
    [Input("channel-dropdown", "value")]
)
def update_figure(c):
    return px.line(wpgs[c], x='Month', y='Value', facet_row='Type', color='Year')

if __name__ == '__main__':
    app.run_server(debug=True)