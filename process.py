import datetime as dt
import json

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sktime.forecasting.theta import ThetaForecaster

with open('Sloc.json', 'r') as o:
    sloc = json.load(o)
with open('Zone.json', 'r') as o:
    zone = json.load(o)
with open('wp.json', 'r') as o:
    wp = json.load(o)

# Sensitivity Analysis
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
df = df.drop(df.loc[(df.Year == dt.datetime.now().year) & (df.Month == dt.datetime.now().month)].index)
df.Year = df.Year.astype('str')
df.Month = df.Month.astype('str')
months = [dt.date(dt.datetime.now().year, i, 1).strftime('%b') for i in range(1, 13)]
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
        ymi[s][t] = ym[s][t][ym[s][t].Year.isin(['2016', '2017', '2018', '2019', '2020'])].reset_index(drop=True)
        ymc[s][t] = ymi[s][t].groupby('Year').cumsum().merge(ymi[s][t], suffixes=('_c', ''),
                                                             left_index=True, right_index=True)
    ymp[s] = ymc[s]['Purchase_price_thb_ton'].merge(ymc[s]['MillWeight'])
    ymp[s]['Price'] = ymp[s]['Purchase_price_thb_ton'] / ymp[s]['MillWeight']
    ymp[s]['Price_c'] = ymp[s]['Purchase_price_thb_ton_c'] / ymp[s]['MillWeight_c']
    ymp[s].Year = ymp[s].Year.astype('str')
    ymp[s].Month = ymp[s].Month.astype('str')

    f, forecaster = {}, {}
    print(s, df.Month.unique())
    for m in df.Month.unique():
        print(m)

        if len(ymp[s].loc[ymp[s].Month == m]) > 1:

            # 2nd-Step: PQ-Regression
            f[m] = RandomForestRegressor()
            f[m].fit(ymp[s].loc[ymp[s].Month == m].MillWeight.values.reshape(-1, 1),
                     ymp[s].loc[ymp[s].Month == m]['Price'].values)

            # 1st-Step: TS-Forecasting
            hist = pd.Series(ymp[s].loc[ymp[s].Month == m, 'MillWeight'].astype(float).values)
            print(hist)
            forecaster[m] = ThetaForecaster(sp=1)
            forecaster[m].fit(hist)
            yp = forecaster[m].predict([1])

            if m in ymp[s].loc[ymp[s].Year == dt.datetime.now().year, 'Month']:
                ymp[s] = ymp[s].append(pd.Series({'Month': m,
                                                  'Year': str(dt.datetime.now().year + 1) + 'F',
                                                  'MillWeight': yp}), ignore_index=True)
            else:
                ymp[s] = ymp[s].append(pd.Series({'Month': m,
                                                  'Year': str(dt.datetime.now().year) + 'F',
                                                  'MillWeight': yp}), ignore_index=True)
                yp = forecaster[m].update_predict_single(yp, fh=[1])
                ymp[s] = ymp[s].append(pd.Series({'Month': m,
                                                  'Year': str(dt.datetime.now().year + 1) + 'F',
                                                  'MillWeight': yp}), ignore_index=True)

                x_pred = ymp[s].loc[(ymp[s].Year == str(dt.datetime.now().year) + 'F') &
                                    (ymp[s].Month == m), 'MillWeight'].values
                print(x_pred, 1, '\n')
                y_pred = f[m].predict(x_pred.reshape(1, -1))
                ymp[s].loc[ymp[s].Year == str(dt.datetime.now().year) + 'F', 'Price'] = y_pred

            x_pred = ymp[s].loc[(ymp[s].Year == str(dt.datetime.now().year + 1) + 'F') &
                                (ymp[s].Month == m), 'MillWeight'].values
            print(x_pred, 2, '\n')
            y_pred = f[m].predict(x_pred.reshape(1, -1))
            ymp[s].loc[ymp[s].Year == str(dt.datetime.now().year + 1) + 'F', 'Price'] = y_pred
            print(m, m)


def get_data_content():
    return wpmj, wpmsj, wpmjz, wpmsjzm, tls


def get_data_app():
    return df, list_all, ymp
