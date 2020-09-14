import datetime as dt
import json

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sktime.forecasting.theta import ThetaForecaster

import process

ymc, ymp = process.get_data_app()
ympd = {}

with open('Sloc.json', 'r') as o:
    sloc = json.load(o)
with open('Zone.json', 'r') as o:
    zone = json.load(o)

for s in ['all'] + list(zone.keys()) + list(sloc.keys()):
    f, forecaster = {}, {}
    for m in ymp[s].Month.unique():
        if len(ymp[s].loc[ymp[s].Month == m]) > 1:
            # 2nd-Step: PQ-Regression
            f[m] = RandomForestRegressor()
            f[m].fit(ymp[s].loc[ymp[s].Month == m].MillWeight.values.reshape(-1, 1),
                     ymp[s].loc[ymp[s].Month == m]['Price'].values)
            # 1st-Step: TS-Forecasting
            hist = ymp[s].loc[ymp[s].Month == m].sort_values(by='Year')
            hist = pd.Series(hist['MillWeight'].astype(float).values)
            forecaster[m] = ThetaForecaster(sp=1)
            forecaster[m].fit(hist)
            yp = forecaster[m].predict([1]).values[0]
            if m in ymp[s].loc[ymp[s].Year == str(dt.datetime.now().year), 'Month'].values:
                ymp[s] = ymp[s].append(pd.Series({'Month': m,
                                                  'Year': str(dt.datetime.now().year + 1) + 'F',
                                                  'MillWeight': yp}), ignore_index=True)
            else:
                ymp[s] = ymp[s].append(pd.Series({'Month': m,
                                                  'Year': str(dt.datetime.now().year) + 'F',
                                                  'MillWeight': yp}), ignore_index=True)
                yp = forecaster[m].update_predict_single(pd.Series(yp), fh=[1]).values[0]
                ymp[s] = ymp[s].append(pd.Series({'Month': m,
                                                  'Year': str(dt.datetime.now().year + 1) + 'F',
                                                  'MillWeight': yp}), ignore_index=True)

                x_pred = ymp[s].loc[(ymp[s].Year == str(dt.datetime.now().year) + 'F') &
                                    (ymp[s].Month == m), 'MillWeight'].values[0]
                y_pred = f[m].predict(x_pred.reshape(1, -1))
                ymp[s].loc[(ymp[s].Year == str(dt.datetime.now().year) + 'F') &
                           (ymp[s].Month == m), 'Price'] = y_pred

                for cm in ['mean_x', 'mean_y', 'count_x', 'count_y']:
                    ymp[s].loc[(ymp[s].Year == str(dt.datetime.now().year) + 'F') &
                               (ymp[s].Month == m), cm] = ymp[s].loc[ymp[s].Month == m, cm].mean()

            x_pred = ymp[s].loc[(ymp[s].Year == str(dt.datetime.now().year + 1) + 'F') &
                                (ymp[s].Month == m), 'MillWeight'].values[0]
            y_pred = f[m].predict(x_pred.reshape(1, -1))
            ymp[s].loc[(ymp[s].Year == str(dt.datetime.now().year + 1) + 'F') &
                       (ymp[s].Month == m), 'Price'] = y_pred

            for cm in ['mean_x', 'mean_y', 'count_x', 'count_y']:
                ymp[s].loc[(ymp[s].Year == str(dt.datetime.now().year + 1) + 'F') &
                           (ymp[s].Month == m), cm] = ymp[s].loc[ymp[s].Month == m, cm].mean()

for s in ['all'] + list(zone.keys()) + list(sloc.keys()):
    a = ymp[s].copy()
    a['Y'] = 'Year'
    a['YP'] = a['Year'].str.replace('F', '').astype(int) - 2000
    a['YC'] = a['YP']
    a['Type'] = '2016_2019_Actual'
    a.loc[a['Year'] == '2020', 'Type'] = '2020_Actual'
    a.loc[a['Year'] == '2020F', 'Type'] = '2020_Forecast'
    a.loc[a['Year'] == '2021F', 'Type'] = '2021_Forecast'
    b = ymp[s].copy()
    b['Y'] = 'Price'
    b['YP'] = b['Price']
    b['YC'] = b['Year'].str.replace('F', '').astype(int)
    b['Type'] = '2016_2019_Actual'
    b.loc[b['Year'] == '2020', 'Type'] = '2020_Actual'
    b.loc[b['Year'] == '2020F', 'Type'] = '2020_Forecast'
    b.loc[b['Year'] == '2021F', 'Type'] = '2021_Forecast'
    ympd[s] = b.append(a, ignore_index=True)
    ympd[s] = ympd[s].to_json(orient='records')

with open('ympd.json', 'w') as o:
    json.dump(ympd, o)
