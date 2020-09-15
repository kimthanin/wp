import datetime as dt
import json

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px

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

# mcard
months = [dt.date(dt.datetime.now().year, i, 1).strftime('%b') for i in range(1, 13)]
year = dt.datetime.now().year
years = [str(year), str(year + 1)]
mcol, mtarget, mmill, mprice, ry = {}, {}, {}, {}, {}
for s in list_all:
    mcol[s], mtarget[s], mmill[s], mprice[s], ry[s] = {}, {}, {}, {}, {}
    for y in years:
        mcol[s][y], mtarget[s][y], mmill[s][y], mprice[s][y] = {}, {}, {}, {}
        for m in months:
            mill = ympd[s].loc[(ympd[s].Month == m) & (ympd[s].YC == int(y)), 'MillWeight'].iloc[0]
            price = ympd[s].loc[(ympd[s].Month == m) & (ympd[s].YC == int(y)), 'Price'].iloc[0]
            mmill[s][y][m] = dbc.Row([
                dbc.Col(dbc.Label('MillWeight', size='sm')),
                dbc.Col(dbc.Label(f'{mill:,.2f}', size='sm'))
            ], form=True)
            mprice[s][y][m] = dbc.Row([
                dbc.Col(dbc.Label('Price', size='sm')),
                dbc.Col(dbc.Label(f'{price:,.2f}', size='sm'))
            ], form=True)
            mtarget[s][y][m] = dbc.Row([
                dbc.Col(dbc.Label('Target', size='sm')),
                dbc.Col(dbc.Input(id=f'{s}-{y}-{m}-target', bs_size="sm", value=f'{mill:,.2f}'))
            ], form=True)
            mcol[s][y][m] = dbc.Col([
                html.Button(html.P(m, style={'font-size': 'small'}),
                            id=f'{s}-{y}-{m}-toggle', className="navbar-toggler"),
                dbc.Collapse([mmill[s][y][m], mprice[s][y][m], mtarget[s][y][m],
                              dbc.Label('Target', size='sm', id=f'{s}-{y}-{m}-label')],
                             id=f'{s}-{y}-{m}-collapse', is_open=True)
            ], sm=4, md=2, lg=1)

        ry[s][y] = dbc.Card([
            dbc.CardHeader(y),  # html.P(y, style={'font-size': 'small'}),
            dbc.Row([mcol[s][y][m] for m in months])  # , no_gutters=True
        ])


# wdsm_page
def page(z):
    zonel = list(zone.keys())
    zoner = ['all'] + zonel if z == 'all' else zone[z]
    t = '''Top: Step_1_Forecast Quantity (Size=Average Transaction Size) |
           Bottom: Step_2_Forecast Price (Size=Number of Transactions) |
           Color: Year (Darker=Newer)'''
    return html.Div([
        dbc.Tabs([dbc.Tab(label=s, tab_id=s) for s in zoner], id=f'{z}-input'),
        html.P(t, style={'font-size': 'small'}),
        dbc.Row([
            dbc.Col(id=f'{z}-wdsm')
            ])
        ])


# wdsm_graph
def graph(s):
    S = ympd[s].loc[ympd[s].Y == 'Year']
    fig1 = px.scatter(S, x='MillWeight', y='YP', color='YC', size='count_y', symbol='Type',
                      color_continuous_scale='Blugrn', facet_col_spacing=0.005, facet_col='Month', height=240)
    fig1.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig1.for_each_yaxis(lambda a: a.update(dtick=1))
    fig1.for_each_yaxis(lambda a: a.update(title='', tickangle=90, dtick=1), row=1, col=1)
    fig1.for_each_xaxis(lambda a: a.update(title='', showticklabels=False))  # showgrid=True, visible=False, dtick=10000
    fig1.layout.update(coloraxis_showscale=False, showlegend=False,
                       margin=dict(l=0, r=0, t=15, b=0))  # , title_font=dict(size=14))
    fig1.update_yaxes(autorange="reversed")  # matches=None

    S = ympd[s].loc[ympd[s].Y == 'Price']
    fig2 = px.scatter(S, x='MillWeight', y='YP', color='YC', size='mean_y', symbol='Type',
                      color_continuous_scale='Blugrn', facet_col_spacing=0.005, facet_col='Month', height=500,
                      labels={'Type': ''})  # , facet_row='Y'
    fig2.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig2.for_each_yaxis(lambda a: a.update(title='', tickangle=90), row=1, col=1)
    fig2.for_each_xaxis(lambda a: a.update(title='', tickangle=90))  # , dtick=10000
    fig2.layout.update(coloraxis_showscale=False, legend_orientation='h', margin=dict(l=0, r=0, t=0, b=0))

    return [dcc.Graph(figure=fig1), dcc.Graph(figure=fig2), ry[s]['2020'], ry[s]['2021']]
