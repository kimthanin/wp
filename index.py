import json

import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd

# Load Data
with open('Sloc.json', 'r') as o:
    sloc = json.load(o)
with open('Zone.json', 'r') as o:
    zone = json.load(o)
with open('ympd.json', 'r') as o:
    ympd = json.load(o)
with open('list_all.json', 'r') as o:
    list_all = json.load(o)
for s in list_all:
    ympd[s] = pd.read_json(ympd[s], orient='records')


# wdsm_page
def page(z):
    zonel = list(zone.keys())
    zoner = ['all'] + zonel if z == 'all' else zone[z]

    return html.Div([
        dbc.Row([
            dbc.Tabs([dbc.Tab(label=s, tab_id=s) for s in zoner], id=f'index-tab')
        ]),

        dbc.Row([
            dbc.Col([
                html.Button(html.P(z+'Input Sloc Admin Cost', style={'font-size': 'small'}),
                            className='navbar-toggler', id=f'index-toggle'),
                dbc.Collapse(html.P(z),
                             is_open=True, id=f'index-collapse')
            ], sm=2, md=4, lg=1),

            dbc.Col(id=f'index-page', sm=2, md=4, lg=1)

        ])
    ])
