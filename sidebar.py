

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)


import datetime as dt
import json
# Sensitivity Analysis

with open('Sloc.json', 'r') as o:
    sloc = json.load(o)
with open('Zone.json', 'r') as o:
    zone = json.load(o)
with open('wp.json', 'r') as o:
    wp = json.load(o)
wpm, wpmj, wpms, wpmsj = {}, {}, {}, {}
wpmjz, wpmsjz = pd.DataFrame(), pd.DataFrame()
for s in sloc.keys():
    wp[s] = pd.read_json(wp[s], orient='records')
    wp[s]['dt'] = pd.to_datetime(wp[s][['Year', 'Month', 'Day']])
    wpm[s] = wp[s].groupby(['Year', 'Month']).sum().reset_index().drop('Price_Daily', axis=1)
    wpm[s]['Price_Monthly'] = wpm[s]['Purchase_price_thb_ton'] / wpm[s]['MillWeight']
    wpm[s]['Day'] = 1
    wpm[s]['dt'] = pd.to_datetime(wpm[s][['Year', 'Month', 'Day']])
    wpm[s]['Sloc'] = s
for s in sloc.keys():
    sen = wpm[s][['MillWeight', 'Price_Monthly']].pct_change().apply(lambda x: round(x, 5)) * 100
    sen['sen'] = sen['MillWeight'] / sen['Price_Monthly']
    sen = sen.replace(np.inf, 1000).replace(-np.inf, -1000).clip(-100, 100)
    wpms[s] = sen.merge(wpm[s]['dt'], left_index=True, right_index=True)
    wpms[s]['Sloc'] = s
for z in zone.keys():
    a, b = pd.DataFrame(), pd.DataFrame()
    for s in zone[z]:
        a = a.append(wpm[s])
        b = b.append(wpms[s])
    wpmj[z] = a
    wpmsj[z] = b
    wpmsjz = wpmsjz.append(wpmsj[z])
    wpmjz = wpmjz.append(wpmj[z])
ss = wpmsjz.Sloc.unique()
dft = pd.DataFrame()
tl = wpmsjz.dt.unique()
for t in tl:
    dfs = pd.DataFrame(ss, columns=['Sloc'])
    dfs['dt'] = t
    dft = dft.append(dfs)
wpmsjzm = wpmsjz.merge(dft, left_on=['dt', 'Sloc'], right_on=['dt', 'Sloc'], how='outer')
wpmjz = wpmjz.merge(dft, left_on=['dt', 'Sloc'], right_on=['dt', 'Sloc'], how='outer')
tls = np.sort(tl)[::-1]

# Cumulative Analysis
df = pd.read_csv('View_Transaction_SFT_6049_2020_09_08_14_29_00.csv')
months = [dt.date(2008, i, 1).strftime('%b') for i in range(1, 13)]
list_all = ['all'] + list(zone.keys()) + list(sloc.keys())
ym, ymi, ymc, ymp = {}, {}, {}, {}
for s in list_all:
    if s == 'all':
        dfs = df
    elif len(s) == 2:
        dfs = df.loc[df.Zone == s]
    else:
        dfs = df.loc[df.Sloc == s]
    ym[s], ymi[s], ymc[s] = {}, {}, {}
    for t in ['Purchase_price_thb_ton', 'MillWeight']:
        ym[s][t] = dfs.groupby(['Year', 'Month'])[t].sum().reset_index()
        ymi[s][t] = ym[s][t][ym[s][t].Year >= 2016].reset_index(drop=True)
        ymc[s][t] = ymi[s][t].groupby('Year').cumsum().merge(ymi[s][t], suffixes=('_c', ''),
                                                             left_index=True, right_index=True)
    ymp[s] = ymc[s]['Purchase_price_thb_ton'].merge(ymc[s]['MillWeight'])
    ymp[s]['Price'] = ymp[s]['Purchase_price_thb_ton'] / ymp[s]['MillWeight']
    ymp[s]['Price_c'] = ymp[s]['Purchase_price_thb_ton_c'] / ymp[s]['MillWeight_c']
    ymp[s].Year = ymp[s].Year.astype('category')
    ymp[s].Month = ymp[s].Month.astype('category')

# the styles for the main content position it to the right of the sidebar and
CONTENT_STYLE = {"margin-left": "18rem", "margin-right": "2rem", "padding": "2rem 1rem"}  # add some padding.

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
        #color="dark",  # https://bootswatch.com/default/ for more card colors
        #inverse=True,  # change color of text (black or white)
        #outline=False  # True = remove the block colors from the background and header
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

card_wdws = dbc.Card([
    dbc.CardBody([
        html.H4("Select Center", className="card-title"),
        dcc.Dropdown(id='wdws_y', value='all',
                     options=[{'label': y, 'value': y} for y in list(df.Year.unique()) + ['all']]),
        dcc.Dropdown(id='wdws_m', value='all',
                     options=[{'label': m, "value": m} for m in list(df.Month.unique()) + ['all']]),
        dcc.Dropdown(id='wdws_s', value='all',
                     options=[{'label': s, "value": s} for s in list_all])
    ])
],
    color="dark",  # https://bootswatch.com/default/ for more card colors
    inverse=True,  # change color of text (black or white)
    outline=False  # True = remove the block colors from the background and header
)

page_wdws = dbc.Row([card_wdws, dcc.Graph(id='wdws')])

page_index = [dcc.Graph(figure=px.bar(wpmjz.loc[wpmsjzm.dt == t], x='Sloc', y='Purchase_price_thb_ton', color='Sloc',
                                      title=str(pd.to_datetime(t).year) + '_' + str(pd.to_datetime(t).month)))
              for t in tls[:24]]

page_sen = [dcc.Graph(figure=px.bar(wpmsjzm.loc[wpmsjzm.dt == t], x='Sloc', y='sen', color='Sloc',
                                    title=str(pd.to_datetime(t).year) + '_' + str(pd.to_datetime(t).month)))
            for t in tls[:24]]

# Main Page # the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}
sidebar = html.Div(
    [
        html.H2("Wood Pricing Strategy", className="display-4"),
        html.Hr(),
        dbc.Nav(
            [dbc.NavLink('Wood Demand / Wood Supply', href='/wdws', id='link_wdws'),
             dbc.NavLink('Purchasing Optimization', href='/', id='link_home'),
             dbc.NavLink('Sensitivity Forecasting', href='/sen', id='link_sen')],
            vertical=True, pills=True,
        ),
        html.P(
            "Choose Region", className="lead"
        ),
        dbc.Nav(
            [dbc.NavLink(z, href=f'/{z}', id=f'link_{z}') for z in zone.keys()],
            vertical=True, pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)
app.layout = html.Div([
    html.Div([dcc.Location(id="url"), sidebar, content])
])


@app.callback(Output('wdws', 'figure'), [Input('wdws_y', 'value'), Input('wdws_m', 'value'), Input('wdws_s', 'value')])
def ug_wdws(y, m, s):
    if (str(m) == 'all') & (str(y) == 'all'):
        return px.scatter(ymp[s], x='MillWeight', y='Price', height=400)
    elif str(m) == 'all':
        return px.scatter(ymp[s].loc[(ymp[s].Year == y)], x='MillWeight', y='Price', height=400)
    elif str(y) == 'all':
        return px.scatter(ymp[s].loc[(ymp[s].Month == m)], x='MillWeight', y='Price', height=400)
    else:
        return px.scatter(ymp[s].loc[(ymp[s].Year == y) & (ymp[s].Month == m)], x='MillWeight', y='Price', height=400)


@app.callback([Output('graph_CH', 'figure')], [Input('choice_CH', 'value')])
def ug_CH(v):
    return [px.scatter(wp[v], x='dt', y='Price_Daily', size='MillWeight', height=400)]


@app.callback([Output('graph_N1', 'figure')], [Input('choice_N1', 'value')])
def ug_N1(v):
    return [px.scatter(wp[v], x='dt', y='Price_Daily', size='MillWeight', height=400)]


@app.callback([Output('graph_N2', 'figure')], [Input('choice_N2', 'value')])
def ug_N2(v):
    return [px.scatter(wp[v], x='dt', y='Price_Daily', size='MillWeight', height=400)]


@app.callback([Output('graph_N3', 'figure')], [Input('choice_N3', 'value')])
def ug_N3(v):
    return [px.scatter(wp[v], x='dt', y='Price_Daily', size='MillWeight', height=400)]


@app.callback([Output('graph_W1', 'figure')], [Input('choice_W1', 'value')])
def ug_W1(v):
    return [px.scatter(wp[v], x='dt', y='Price_Daily', size='MillWeight', height=400)]


# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback([Output('link_home', 'active')] + [Output(f'link_{i}', 'active') for i in zone.keys()],
              [Input("url", "pathname")])
def toggle_active_links(pathname):
    return [pathname == '/'] + [pathname == f'/{i}' for i in zone.keys()]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == '/':
        return page_index
    if pathname == '/wdws':
        return page_wdws
    if pathname == '/sen':
        return page_sen
    for z in zone.keys():
        if pathname == '/' + z:
            return page[z]
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == "__main__":
    app.run_server(port=5000, debug=True)

# , color="continent" , title=str(value), hover_name=
