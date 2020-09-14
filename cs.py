import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
# import plotly.express as px
from dash.dependencies import Input, Output, State

from sb import sidebar_header
from wdsm import page_wdws

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
                dbc.NavLink("Page 1", href="/page-1", id="page-1-link"),
                dbc.NavLink("Page 2", href="/page-2", id="page-2-link"),
                dbc.NavLink("Page 3", href="/page-3", id="page-3-link")],
                vertical=True, pills=True),
            id="collapse")],
        id="sidebar"),
    html.Div(id="page-content")
])


# Callback WDSM
@app.callback([Output('wdsm1', 'figure'), Output('wdsm2', 'figure')],
              [Input('wdws_y', 'value'), Input('wdws_m', 'value'), Input('wdws_s', 'value')])
def update_wdsm(y1, m1, s1):
    from wdsm import wdsm
    fig1, fig2 = wdsm(y1, m1, s1)
    return [fig1, fig2]


# Callback Page
@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 4)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        return True, False, False
    return [pathname == f"/page-{i}" for i in range(1, 4)]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1"]:
        return page_wdws
    elif pathname == "/page-2":
        return html.P("This is the content of page 2. Yay!")
    elif pathname == "/page-3":
        return html.P("Oh cool, this is page 3!")
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


# Callback colbar
@app.callback(
    [Output("colbar-collapse", "is_open"), Output("colbar-label", "children")],
    [Input("colbar-toggle", "n_clicks")],
    [State("colbar-collapse", "is_open")],
)
def toggle_colbar_collapse(n, is_open):
    if n:
        if is_open:
            return [not is_open, None]
        else:
            return [not is_open, 'Select Data']
    else:
        return [is_open, 'Select Data']


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
