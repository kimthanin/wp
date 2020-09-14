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
for s in ['all'] + list(zone.keys()) + list(sloc.keys()):
    ympd[s] = pd.read_json(ympd[s], orient='records')


# months = ympd['all'].Month.unique()


# colbar
def colbar(z):
    zonel = list(zone.keys())
    zoner = ['all'] + zonel if z == 'all' else zone[z]
    print(zoner)
    print([{"label": s, "value": s} for s in zoner])

    return html.Div([
        html.Button(id='colbar-toggle', className="navbar-toggler"),
        dbc.Collapse(
            dbc.RadioItems(options=[{"label": s, "value": s} for s in zoner], id=f'{z}-input'),
            id='colbar-collapse', is_open=True
        )
    ])


# mcard, mtarget, mmill, mprice = {}, {}, {}, {}
# for m in months:
#     mill = ympd['all'].loc[(ympd['all'].Month == m) & (ympd['all'].YC == 2020), 'MillWeight'].iloc[0]
#     price = ympd['all'].loc[(ympd['all'].Month == m) & (ympd['all'].YC == 2020), 'Price'].iloc[0]
#
#     mmill[m] = dbc.Row([dbc.Label('MillWeight', size='sm'),
#                         dbc.Label(f'{mill:,.2f}', size='sm')], form=True)
#     mprice[m] = dbc.Row([dbc.Label('Price', size='sm'),
#                          dbc.Label(f'{price:,.2f}', size='sm')], form=True)
#     mtarget[m] = dbc.Row([dbc.Label('Target', size='sm'),
#                           dbc.Input(id=f'{m}-target', value=f'{mill:,.2f}', bs_size="sm")], form=True)
#     mcard[m] = html.Div([mmill[m], mprice[m], mtarget[m]])

def page_wdws(z):
    return dbc.Row([colbar(z), dbc.Col(id=f'{z}-wdsm')])


def wdsm(s):
    print(s, '''
        Top: Step_1_Forecast Quantity (Size=Average Transaction Price) | 
        Bottom: Step_2_Forecast Price (Size=Number of Transactions) | 
        Color: Year (Darker=Newer)''', end='')

    S = ympd[s].loc[ympd[s].Y == 'Year']
    fig1 = px.scatter(S, x='MillWeight', y='YP', color='YC', size='mean_x', symbol='Type',
                      color_continuous_scale='Blugrn', facet_col_spacing=0.005, facet_col='Month', height=240)
    fig1.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig1.for_each_yaxis(lambda a: a.update(dtick=1))
    fig1.for_each_yaxis(lambda a: a.update(title='', tickangle=90, dtick=1), row=1, col=1)
    fig1.for_each_xaxis(lambda a: a.update(title='', dtick=10000, showticklabels=False))  # showgrid=True, visible=False
    fig1.layout.update(coloraxis_showscale=False, showlegend=False, margin=dict(l=0, r=0, t=15, b=0))
    fig1.update_yaxes(autorange="reversed")  # matches=None

    S = ympd[s].loc[ympd[s].Y == 'Price']
    fig2 = px.scatter(S, x='MillWeight', y='YP', color='YC', size='count_x',
                      symbol='Type', color_continuous_scale='Blugrn', facet_col_spacing=0.005, facet_col='Month',
                      height=500, labels={'Type': ''})  # , facet_row='Y'
    fig2.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig2.for_each_yaxis(lambda a: a.update(title='', tickangle=90), row=1, col=1)
    fig2.for_each_xaxis(lambda a: a.update(title='', dtick=10000))
    fig2.layout.update(coloraxis_showscale=False, legend_orientation='h', margin=dict(l=0, r=0, t=0, b=0))

    return [dcc.Graph(figure=fig1),
            dcc.Graph(figure=fig2),
            # dbc.Row([
            #     dbc.Col([
            #         html.Button(
            #             html.P(m, id=f'{m}-label'),
            #             id=f'{m}-toggle', className="navbar-toggler"),
            #         dbc.Collapse(mcard[m], id=f'{m}-collapse', is_open=True)
            #     ]) for m in months
            ]
