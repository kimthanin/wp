import numpy as np
import pandas as pd
import dash
import plotly.express as px
import dash_html_components as html
from dash.dependencies import Input, Output
from dash_core_components import Graph, Dropdown, Tab, Tabs
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sktime.forecasting.compose import ReducedRegressionForecaster


# Model
def wpmodel(wpg):
    model = RandomForestRegressor(random_state=0)
    ry = range(2015, 2021); rm = range(1, 13)
    dt = pd.concat([pd.DataFrame({'Month': rm}, index=[y] * len(rm))
                   .reset_index().rename(columns={'index': 'Year'}) for y in ry]) \
        .reset_index(drop=True)
    csd, csdp = {}, {}
    for c in wpg.Channel.unique():  # ['N1BK']
        dtcs = dt.drop(dt.loc[((dt.Year == 2020) & (dt.Month >= 8))].index) \
            .merge(wpg.loc[wpg.Channel == c], how='left', left_on=['Year', 'Month'], right_on=['Year', 'Month'])
        cs = dtcs.fillna(method='ffill').dropna()
        cspct = cs[['Ton', 'Baht']].pct_change().rename(columns={'Ton': 'TonPct', 'Baht': 'BahtPct'}) * 100
        csdiff = cs[['Ton', 'Baht']].diff().rename(columns={'Ton': 'TonDiff', 'Baht': 'BahtDiff'})
        cs = cs.merge(cspct, how='left', left_index=True, right_index=True)
        cs = cs.merge(csdiff, how='left', left_index=True, right_index=True)
        cs['E'] = cs.TonPct / cs.BahtPct
        cs['S'] = cs.TonDiff / cs.BahtDiff
        cs['EC'] = cs.E.clip(-1000, 1000).fillna(method='ffill')
        cs['SC'] = cs.E.clip(-1000, 1000).fillna(method='ffill')
        cs['Type'] = 'Actual'
        csd[c] = cs[['Year', 'Month', 'EC', 'Type']]
    for c in wpg.Channel.unique():
        a = len(csd[c].EC)
        if a > 20:
            csdp[c] = csd[c]
    for c in csdp.keys():
        print(c)
        y = csdp[c].EC.dropna(); num_step = 5; fh = np.arange(1, num_step + 1)  # forecasting horizon
        f = ReducedRegressionForecaster(model, window_length=12)  # monthly seasonal periodicity
        f.fit(y)
        y_pred = f.predict(fh)
        y_pred_df = pd.DataFrame(y_pred)
        y_pred_df.rename(columns={0: 'EC'}, inplace=True)
        y_pred_df['Type'] = 'Forecast'
        y_pred_df = dt.merge(y_pred_df, how='inner', left_index=True, right_index=True)
        csdp[c] = csdp[c].append(y_pred_df)
    return csdp


# Main
app = dash.Dash(__name__)
server = app.server
wpg = pd.read_csv('wpg.csv').drop(columns='Amount')
csdp = wpmodel(wpg)
scaler, wpgs = {}, {}
for c in wpg.Channel.unique():
    scaler[c] = {}
    scaler[c] = StandardScaler()
    wpgs[c] = wpg.loc[wpg.Channel == c].copy()
    wps = wpgs[c][['Baht', 'Ton']]
    scaler[c].fit(wps)
    wpgs[c][['Baht', 'Ton']] = scaler[c].transform(wps)
    wpgs[c] = pd.melt(wpgs[c], var_name='Type', value_name='Value',
                      id_vars=['Zone', 'Channel', 'Year', 'Month'])

# Build App
app.layout = \
    html.Div([
        Dropdown(id='SLOC', value=['N3NB', 'N3DT'],
                 placeholder='Select Storage Locations',
                 multi=True, clearable=True,
                 options=[{'label': c1, 'value': c1}
                          for c1 in wpg.Channel.unique()]),
        Tabs([
            Tab(label='Price/Quantity', children=[
                html.Div(id='PQ')
            ]),
            Tab(label='Sensitivity', children=[
                html.Div(id='SE')
            ]),
            Tab(label='Data Quality', children=[

            ]),
        ])
    ])


# Define callback to update graph
@app.callback(
    [Output('PQ', 'children'), Output('SE', 'children')],
    [Input("SLOC", "value")]
)
def update_figure(c_list):
    PQ, SE = [], []
    for c in c_list:
        PQ_fig = px.line(wpgs[c], x='Month', y='Value', color='Year',
                         facet_row='Type', category_orders={'Type': ['Baht', 'Ton']})
        PQ.append(Graph(figure=PQ_fig))

        SE_fig = px.bar(csdp[c], x='Month', y='EC', color='Type',
                        facet_row='Year')
        SE.append(Graph(figure=SE_fig))

    return PQ, SE


if __name__ == '__main__':
    # app.run_server(port=80,debug=True)
    app.run_server(port=80, host='0.0.0.0')
    # waitress-serve --listen="0.0.0.0:80" woodpricing:server