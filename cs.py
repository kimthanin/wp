import datetime as dt
import json

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State

import wdsm, index
from sb import sidebar_header

# Server Config
meta = {"name": "viewport", "content": "width=device-width, initial-scale=1"}
sbcss = 'https://raw.githubusercontent.com/facultyai/dash-bootstrap-components/master/examples/multi-page-apps/\
responsive-collapsible-sidebar/assets/responsive-sidebar.css'
# https://raw.githubusercontent.com/kimthanin/wp/master/assets/responsive-sedbar.css
external_stylesheets = [dbc.themes.BOOTSTRAP, sbcss]
app = dash.Dash(__name__,
                suppress_callback_exceptions=True,
                external_stylesheets=external_stylesheets,
                meta_tags=[meta]
                )
server = app.server

# Main
app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div([
        sidebar_header,
        html.Div([
            html.P('Wood Pricing Strategy', className="lead"),
            html.P('Based on MPlan and Estimated Competition Environment')], id="blurb"),
        dbc.Collapse(
            dbc.Nav([
                dbc.NavLink('Index', href="/", id='index'),
                dbc.NavLink('all', href="/all", id='all'),
                dbc.NavLink('CH', href="/CH", id='CH'),
                dbc.NavLink('N1', href="/N1", id='N1'),
                dbc.NavLink('N2', href="/N2", id='N2'),
                dbc.NavLink('N3', href="/N3", id='N3'),
                dbc.NavLink('W1', href="/W1", id='W1')],
                vertical=True, pills=True),
            id="collapse")],
        id="sidebar"),
    html.Div(id="page-content")
])

with open('list_all.json', 'r') as o:
    list_all = json.load(o)
with open('Zone.json', 'r') as o:
    zone = json.load(o)
zonel = ['all'] + list(zone.keys())
months = [dt.date(dt.datetime.now().year, i, 1).strftime('%b') for i in range(1, 13)]
year = dt.datetime.now().year
years = [str(year), str(year + 1)]

# Callback Save
ci = {}
for s_ in list_all:
    ci[s_] = []
    for y_ in years:
        for t_ in ['target', 'mill', 'price']:
            for m_ in months:
                ci[s_] = ci[s_] + [Input(f'{s_}-{y_}-{m_}-{t_}', 'value')]

for s_ in list_all:
    @app.callback([Output(f'{s_}-toast', 'is_open'), Output(f'{s_}-toast', 'children')],
                  [Input(f'{s_}-save_target', 'n_clicks')] + ci[s_])
    def save_target(n, *ci_):
        dfy = {}
        i = 0
        for y_ in years:
            for t_ in ['target', 'mill', 'price']:
                dfy[y_][t_] = pd.DataFrame(ci_[i:i + 12], columns=t_)
                dfy[y_][t_]['Year'] = y_
                dfy[y_][t_]['Month'] = months
                i += 12
            dfytm = dfy[y_]['price'].merge(dfy['mill'][t_], left_on=['Year', 'Month'], right_on=['Year', 'Month'])
            dfy[y_]['tm'] = dfytm.merge(dfy[y_]['target'], left_on=['Year', 'Month'], right_on=['Year', 'Month'])
        dfy['ym'] = dfy[years[0]]['tm'].append(dfy[years[1]]['tm'])
        dfy['ym'].to_csv('/target/' + s_ + '.csv', index=False)
        return [True, 'Saved: ' + str(n)]

# Callback WDSM
for z in zonel:
    @app.callback(Output(f'{z}-wdsm', 'children'), Input(f'{z}-input', 'active_tab'))
    def update_wdsm(s):
        return wdsm.graph(s)


# Callback Index
@app.callback(Output(f'index-page', 'children'), Input(f'index-tab', 'active_tab'))
def update_index(s):
    return html.P(s)


# Callback Target
for s_ in list_all:
    for y_ in years:
        for m_ in months:
            @app.callback([Output(f'{s_}-{y_}-{m_}-label', 'children'), Output(f'{s_}-{y_}-{m_}-label', 'color'),
                           Output(f'{s_}-{y_}-{m_}-amount', 'children'), Output(f'{s_}-{y_}-{m_}-amount', 'color')],
                          [Input(f'{s_}-{y_}-{m_}-target', 'value'), Input(f'{s_}-{y_}-{m_}-mill', 'children')])
            def update_sym(target, mill):
                amount = round(float(mill.replace(',', '')) - float(target.replace(',', '')), 2)
                if amount < 0:
                    return ['Under Target', 'danger', amount, 'danger']
                else:
                    return ['Over Target', 'success', amount, 'success']


# Callback colbar
@app.callback(
    [Output("colbar-collapse", "is_open"), Output("colbar-toggle", "children")],
    [Input("colbar-toggle", "n_clicks")],
    [State("colbar-collapse", "is_open")],
)
def toggle_colbar_collapse(n, is_open):
    cbl = html.Div([html.P('Storage'), html.P('Location:')])
    if n:
        if is_open:
            return [not is_open, None]
        else:
            return [not is_open, cbl]
    else:
        return [is_open, cbl]


# Callback Collapse
@app.callback(
    Output("sidebar", "className"),
    [Input("sidebar-toggle", "n_clicks")],
    [State("sidebar", "className")],
)
def toggle_classname(n, classname):
    if n and classname == "":
        return "collapsed"
    return ""


@app.callback(
    Output("collapse", "is_open"),
    [Input("navbar-toggle", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# Callback Page
@app.callback([Output('index', "active")] + [Output(z, "active") for z in zonel],
              [Input("url", "pathname")])
def toggle_active_links(pathname):
    if pathname == "/":
        return True, False, False, False, False, False, False
    return [False] + [pathname == f'/{z_}' for z_ in zonel]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return index.page('all')  # html.Div('Index')
    if pathname == "/all":
        return wdsm.page('all')
    elif pathname == "/CH":
        return wdsm.page('CH')
    elif pathname == "/N1":
        return wdsm.page('N1')
    elif pathname == "/N2":
        return wdsm.page('N2')
    elif pathname == "/N3":
        return wdsm.page('N3')
    elif pathname == "/W1":
        return wdsm.page('W1')
    return dbc.Jumbotron([
        html.H1("404: Not found", className="text-danger"),
        html.P(f"The pathname {pathname} was not recognised...")
    ])


if __name__ == "__main__":
    app.run_server(port=5005, debug=False)
