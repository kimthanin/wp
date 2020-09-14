import json

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
# import plotly.express as px
from dash.dependencies import Input, Output, State

from sb import sidebar_header
from wdsm import page_wdws

with open('Zone.json', 'r') as o:
    zone = json.load(o)
zonel = ['all'] + list(zone.keys())
# import process
# ymc, ymp = process.get_data_app()

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
            html.P("A responsive sidebar layout with collapsible navigation",
                   className="lead")], id="blurb"),
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
        return page_wdws('all')
    elif pathname == "/CH":
        return page_wdws('CH')
    elif pathname == "/N1":
        return page_wdws('N1')
    elif pathname == "/N2":
        return page_wdws('N2')
    elif pathname == "/N3":
        return page_wdws('N3')
    elif pathname == "/W1":
        return page_wdws('W1')
    return dbc.Jumbotron([
        html.H1("404: Not found", className="text-danger"),
        html.Hr(),
        html.P(f"The pathname {pathname} was not recognised...")
    ])


# Callback WDSM
for z in zonel:
    @app.callback(Output(f'{z}-wdsm', 'children'), Input(f'{z}-input', 'value'))
    def update_wdsm(s):
        from wdsm import wdsm
        return wdsm(s)


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
