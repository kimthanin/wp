import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output, State

# import content
import process
import sb

df, list_all, ymp = process.get_data_app()
ymp['all']['Seasonal'] = 'Rainy'
ymp['all'].loc[ymp['all'].Month.isin(['1', '2', '3', '4', '11', '12']), 'Seasonal'] = 'Summer'
# ymp['all'].loc[ymp['all'].Year.isin(['2018']), 'Seasonal'] = '2018'
#ymp['all'].Month = ymp['all'].Month.astype('category')

app = dash.Dash(
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
)

# wdws

card_wdws = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4("Select Data", className="card-title"),
                dcc.Dropdown(id='wdws_y', value='all',
                             options=[{'label': y, 'value': y} for y in ['all'] + list(df.Year.unique())]),
                dcc.Dropdown(id='wdws_m', value='all',
                             options=[{'label': m, "value": m} for m in ['all'] + list(df.Month.unique())]),
                dcc.Dropdown(id='wdws_s', value='all',
                             options=[{'label': s, "value": s} for s in list_all]),
                dcc.Dropdown(id='wdws_c', value='Seasonal',
                             options=[{'label': c, "value": c} for c in ['Seasonal']])
            ]
        )
    ], color="light", outline=True
)

page_wdws = dbc.Row([card_wdws, dcc.Graph(id='wdws')])

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


# App Callback

@app.callback(Output('wdws', 'figure'),
              [Input('wdws_y', 'value'), Input('wdws_m', 'value'), Input('wdws_s', 'value'), Input('wdws_c', 'value')])
def ug_wdws(y, m, s, c):
    if (str(m) == 'all') & (str(y) == 'all'):
        fig = px.scatter(ymp[s], x='MillWeight', y='Price', facet_col='Year', facet_row=c, color='Month',  #
                         hover_name='Month', hover_data=['Year'],
        width=1200, height=700, color_continuous_scale=px.colors.sequential.Magenta)
        #fig.update_layout(coloraxis_colorbar=dict(dtick=1),
        #                  legend=dict(orientation="h", yanchor="top", xanchor="right"))
        fig.update(layout_coloraxis_showscale=False)
        fig.layout.update(showlegend=False)
        return fig
    elif str(m) == 'all':
        return px.scatter(ymp[s].loc[(ymp[s].Year == y)], x='MillWeight', y='Price', height=400)
    elif str(y) == 'all':
        return px.scatter(ymp[s].loc[(ymp[s].Month == m)], x='MillWeight', y='Price', height=400)
    else:
        return px.scatter(ymp[s].loc[(ymp[s].Year == y) & (ymp[s].Month == m)], x='MillWeight', y='Price', height=400)


# Layout Callback

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
    app.run_server(port=5005, debug=True)
