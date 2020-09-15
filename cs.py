import datetime as dt
import json

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
# import plotly.express as px
from dash.dependencies import Input, Output, State

import wdsm
from sb import sidebar_header

with open('list_all.json', 'r') as o:
    list_all = json.load(o)
with open('Zone.json', 'r') as o:
    zone = json.load(o)
zonel = ['all'] + list(zone.keys())

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


# Callback Page
@app.callback(
    [Output('index', "active")] + [Output(z, "active") for z in zonel],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        return True, False, False, False, False, False, False
    return [False] + [pathname == f'/{z}' for z in zonel]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.Div('Index')
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


# Callback WDSM
for z in zonel:
    @app.callback(Output(f'{z}-wdsm', 'children'), Input(f'{z}-input', 'active_tab'))
    def update_wdsm(s):
        return wdsm.graph(s)

months = [dt.date(dt.datetime.now().year, i, 1).strftime('%b') for i in range(1, 13)]
year = dt.datetime.now().year
years = [str(year), str(year + 1)]
for s in list_all:
    for y in years:
        for m in months:
            @app.callback(Output(f'{s}-{y}-{m}-label', 'children'),
                          Input(f'{s}-{y}-{m}-target', 'value'))
            def update_sym(target):
                return target


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


if __name__ == "__main__":
    app.run_server(port=5005, debug=False)
    # app.run_server(port=80,debug=True)
    # app.run_server(port=80, host='0.0.0.0')
    # waitress-serve --listen="0.0.0.0:80" woodpricing:server
