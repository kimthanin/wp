import json

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
with open('Sloc.json', 'r') as o:
    sloc = json.load(o)
with open('Zone.json', 'r') as o:
    zone = json.load(o)
# the styles for the main content position it to the right of the sidebar and
CONTENT_STYLE = {"margin-left": "18rem", "margin-right": "2rem", "padding": "2rem 1rem"}  # add some padding.

card_graph = dbc.Card(dcc.Graph(id='my_bar', figure={}), body=True, color="secondary")


def card_main(pathname):
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4("Learn Dash with Charming Data", className="card-title"),
                    html.H6("Lesson 1:", className="card-subtitle"),
                    html.P("Choose the year you would like to see on the bubble chart.", className="card-text"),
                    dcc.Dropdown(id='user_choice', options=[{'label': z, "value": z} for z in zone[pathname[1:]]],
                                 value=zone[pathname[1:]][0], clearable=False, style={"color": "#000000"}),
                    dbc.Button("Press me", color="primary"),
                    dbc.CardLink("GirlsWhoCode", href="https://girlswhocode.com/", target="_blank"),
                ]
            ),
        ],
        color="dark",  # https://bootswatch.com/default/ for more card colors
        inverse=True,  # change color of text (black or white)
        outline=False  # True = remove the block colors from the background and header
    )


def page(pathname):
    return html.Div([dbc.Row([dbc.Col(card_main(pathname), width=3), dbc.Col(card_graph, width=6)])])


# Main Page
# the style arguments for the sidebar. We use position:fixed and a fixed width
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
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P(
            "A simple sidebar layout with navigation links", className="lead"
        ),
        dbc.Nav(
            [dbc.NavLink('Home', href='/', id='link_home')] +
            [dbc.NavLink(Zone[0], href='/' + Zone[0], id='link_' + Zone[0]) for Zone in zone.items()],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)
content = html.Div(id="page-content", style=CONTENT_STYLE)
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback([Output('link_home', 'active')] + [Output(f'link_{i}', 'active') for i in zone.keys()],
              [Input("url", "pathname")])
def toggle_active_links(pathname):
    # if pathname == "/":
    # Treat page 1 as the homepage / index
    #    return True, False, False
    return [pathname == '/'] + [pathname == f'/{i}' for i in zone.keys()]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == '/':
        return page('/CH')
    for Zone in zone.items():
        if pathname == '/' + Zone[0]:
            return page(pathname)
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


@app.callback(Output("my_bar", "figure"), [Input("user_choice", "value")])
def update_graph(value):
    fig = px.scatter(df.query("year=={}".format(str(value))), x="gdpPercap", y="lifeExp",
                     size="pop", color="continent", title=str(value),
                     hover_name="country", log_x=True, size_max=60).update_layout(showlegend=True, title_x=0.5)
    return fig


if __name__ == "__main__":
    app.run_server(port=8888)
