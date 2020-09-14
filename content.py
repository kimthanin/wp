import json

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots

import cumulative

# Sensitivity Analysis
with open('Sloc.json', 'r') as o:
    sloc = json.load(o)
with open('Zone.json', 'r') as o:
    zone = json.load(o)
with open('wp.json', 'r') as o:
    wp = json.load(o)

df, list_all, wpmj, wpmsj, wpmjz, wpmsjzm, tls = cumulative.get_data_content()

card_main = {}
for z in zone.keys():
    card_main[z] = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4("Select Center", className="card-title"),
                    dcc.Dropdown(id=f'choice_{z}',
                                 options=[{'label': f'{s}_{sloc[s]}', "value": s} for s in zone[z]],
                                 value=zone[z][0], clearable=False, style={"color": "#000000"}),
                    dbc.Input(placeholder="Please fill in the capacity constraint.", type="text"),
                    dbc.Button("Simulate", color="primary"),
                    html.H6("Recommended Action:", className="card-text"),
                    html.P('% Price Increase / Decrease', className="card-subtitle"),
                    # dbc.CardLink("GirlsWhoCode", href="https://girlswhocode.com/", target="_blank"),
                ]
            ),
        ],
        # color="dark",  # https://bootswatch.com/default/ for more card colors
        # inverse=True,  # change color of text (black or white)
        # outline=False  # True = remove the block colors from the background and header
    )

page = {}
for z in zone.keys():

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for s in range(len(zone[z])):
        fig.add_trace(
            px.scatter(wpmj[z], x='dt', y='Price_Monthly', size='MillWeight', color='Sloc', height=400).data[s],
            secondary_y=False)
        fig.add_trace(px.bar(wpmsj[z], x='dt', y='sen', color='Sloc').data[s], secondary_y=True)
    page[z] = html.Div([
        dcc.Graph(figure=fig),
        dbc.Row(
            [
                dbc.Col(card_main[z], width=3),
                dbc.Col(dcc.Graph(id=f'graph_{z}')
                        )
            ]
        )
    ])

page_index = [
    dcc.Graph(
        figure=px.bar(
            wpmjz.loc[wpmsjzm.dt == t],
            x='Sloc', y='Purchase_price_thb_ton', color='Sloc',
            title=str(pd.to_datetime(t).year) + '_' + str(pd.to_datetime(t).month)
        )
    ) for t in tls[:24]
]

page_sen = [dcc.Graph(figure=px.bar(wpmsjzm.loc[wpmsjzm.dt == t], x='Sloc', y='sen', color='Sloc',
                                    title=str(pd.to_datetime(t).year) + '_' + str(pd.to_datetime(t).month)))
            for t in tls[:24]]
