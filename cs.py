import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output, State

import process
import sb
from wdsm import ympd

external_stylesheets = [dbc.themes.BOOTSTRAP,
                        'assets/bWLwgP.css'
                        "assets/responsive-sedbar.css"]
app = dash.Dash(
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
)
server = app.server

sidebar_header = sb.sidebar_header()
sidebar = html.Div(
    [
        sidebar_header,
        html.Div(
            [
                html.Hr(),
                html.P(
                    "A responsive sidebar layout with collapsible navigation "
                    "links.",
                    className="lead",
                ),
            ],
            id="blurb",
        ),
        dbc.Collapse(
            dbc.Nav(
                [
                    dbc.NavLink("Page 1", href="/page-1", id="page-1-link"),
                    dbc.NavLink("Page 2", href="/page-2", id="page-2-link"),
                    dbc.NavLink("Page 3", href="/page-3", id="page-3-link"),
                ],
                vertical=True,
                pills=True,
            ),
            id="collapse",
        ),
    ],
    id="sidebar",
)

content = html.Div(id="page-content")
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

# wdws
ymc, ymp = process.get_data_app()
d_year = dbc.Row([
    dbc.Col(dbc.Label('Year')),
    dbc.Col(dcc.Dropdown(id='wdws_y', value='all', # + list(df.Year.unique(),
                         options=[{'label': y, 'value': y} for y in ['all']]))
], form=True)
d_month = dbc.Row([
    dbc.Col(dbc.Label('Month')),
    dbc.Col(dcc.Dropdown(id='wdws_m', value='all', # + list(df.Year.unique(),
                         options=[{'label': y, 'value': y} for y in ['all']]))
], form=True)
d_sloc = dbc.Row([
    dbc.Col(dbc.Label('SLOC')),
    dbc.Col(dcc.Dropdown(id='wdws_s', value='all',
                         options=[{'label': y, 'value': y} for y in ['all']]))
], form=True)

card_wdws = html.Div([d_year, d_month, d_sloc])

colbar = html.Div([
    html.Button(html.P('Select Data', id='colbar-label'), id='colbar-toggle', className="navbar-toggler"),
    dbc.Collapse(card_wdws, id='colbar-collapse', is_open=True)
])

page_wdws = dbc.Row([colbar,
                     dbc.Col([dcc.Graph(id='wdsm1'), dcc.Graph(id='wdsm2')], width=8)
                     ])


# App Callback
@app.callback([Output('wdsm1', 'figure'), Output('wdsm2', 'figure')],
              [Input('wdws_y', 'value'), Input('wdws_m', 'value'), Input('wdws_s', 'value')])
def ug_wdws(y, m, s):
    print(y, m, s, '''
    Top: Step_1_Forecast Quantity (Size=Average Transaction Price) | 
    Bottom: Step_2_Forecast Price (Size=Number of Transactions) | 
    Color: Year (Darker=Newer)''', end='')
    fig1 = px.scatter(ympd['all'].loc[ympd['all'].Y == 'Year'], x='MillWeight', y='YP', color='YC', size='mean_x',
                      symbol='Type', color_continuous_scale='Blugrn', facet_col_spacing=0.005, facet_col='Month',
                      height=240, width=1200)
    fig1.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig1.for_each_yaxis(lambda a: a.update(dtick=1))
    fig1.for_each_yaxis(lambda a: a.update(title='', tickangle=90, dtick=1), row=1, col=1)
    fig1.for_each_xaxis(lambda a: a.update(title='', dtick=10000, showticklabels=False))  # showgrid=True, visible=False
    fig1.layout.update(coloraxis_showscale=False, showlegend=False, margin=dict(l=0, r=0, t=15, b=0))
    fig1.update_yaxes(autorange="reversed")  # matches=None

    fig2 = px.scatter(ympd['all'].loc[ympd['all'].Y == 'Price'], x='MillWeight', y='YP', color='YC', size='count_x',
                      symbol='Type', color_continuous_scale='Blugrn', facet_col_spacing=0.005, facet_col='Month',
                      height=500, width=1200, labels={'Type': ''})  # , facet_row='Y'
    fig2.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig2.for_each_yaxis(lambda a: a.update(title='', tickangle=90), row=1, col=1)
    fig2.for_each_xaxis(lambda a: a.update(title='', dtick=10000))
    fig2.layout.update(coloraxis_showscale=False, legend_orientation='h', margin=dict(l=0, r=0, t=0, b=0))

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
    #app.run_server(port=5005, debug=True)
    # app.run_server(port=80,debug=True)
    app.run_server(port=80, host='0.0.0.0')
    # waitress-serve --listen="0.0.0.0:80" woodpricing:server
