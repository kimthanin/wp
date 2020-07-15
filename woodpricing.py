#!/usr/bin/env python
# coding: utf-8

# In[1]:


import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from jupyter_dash import JupyterDash
app = JupyterDash(__name__)
# In[ ]:


import dash
app = dash.Dash(__name__)


# In[3]:


import pandas as pd; import numpy as np; wpg=pd.read_csv('wpg.csv')
from sklearn.preprocessing import StandardScaler
scaler,wpgs = {},{}
for c in wpg.Channel.unique():
    scaler[c] = {}
    scaler[c] = StandardScaler()
    wpgs[c] = wpg.loc[wpg.Channel==c].copy()
    wps = wpgs[c][['Baht','Ton']]
    scaler[c].fit(wps)
    print(c, scaler[c].mean_)
    wpgs[c][['Baht','Ton']] = scaler[c].transform(wps)
    wpgs[c]=pd.melt(wpgs[c], id_vars=['Zone','Channel','Year','Month'],var_name='Type', value_name='Value')


# In[8]:


# Build App
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


# In[5]:


# Define callback to update graph
@app.callback(
    Output('graph', 'figure'),
    [Input("channel-dropdown", "value")]
)
def update_figure(c):
    return px.line(wpgs[c], x='Month', y='Value', facet_row='Type', color='Year')

# Run app and display result inline in the notebook
app.run_server(mode='external')
# In[ ]:


if __name__ == '__main__':
    app.run_server(debug=True)

