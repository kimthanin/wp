import datetime as dt
import json

import numpy as np
import pandas as pd

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
    wp[s] = pd.read_json(wp[s], orient='records').rename(columns={'Monthi': 'Month'})
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
ts_str = '2020_09_13_16_06_52'
df = pd.read_csv('View_Transaction_SFT_6049_' + ts_str + '.csv', parse_dates=True)
df = df.drop(df.loc[(df.Year == dt.datetime.now().year) & (df.Month == dt.datetime.now().month)].index)
# df= df.Year.isin(['2016', '2017', '2018', '2019', '2020']).reset_index(drop=True)
df = df.loc[df.Year >= 2016].reset_index(drop=True)
# print(df.shape)
months = [dt.date(dt.datetime.now().year, i, 1).strftime('%b') for i in range(1, 13)]
df['Monthi'] = df['Month']
df['Month'] = df['Month'].apply(lambda x: months[int(x) - 1])
df.Year = df.Year.astype('str')
df.Month = df.Month.astype('str')
ym, ymi, ymc, ymp, ympd = {}, {}, {}, {}, {}
for s in ['all'] + list(zone.keys()) + list(sloc.keys()):
    if s == 'all':
        dfs = df.copy()
    elif len(s) == 2:
        dfs = df.loc[df.Zone == s].copy()
    else:
        dfs = df.loc[df.Sloc == s].copy()
    ym[s], ymi[s], ymc[s] = {}, {}, {}
    for t in ['Purchase_price_thb_ton', 'MillWeight']:
        tcount = dfs.groupby(['Year', 'Month', 'Monthi'])[t].count().reset_index()
        tmean = dfs.groupby(['Year', 'Month', 'Monthi'])[t].mean().reset_index()
        tmerge = tcount.merge(tmean, left_index=True, right_index=True, suffixes=('_m', ''))
        # tmerge.rename(columns={t+'_m':'mean', t:'count'}, inplace=True)
        tmerge = tmerge.rename(columns={t + '_m': 'mean', t: 'count'})[['mean', 'count']]
        ym[s][t] = dfs.groupby(['Year', 'Month', 'Monthi'])[t].sum().reset_index()
        ym[s][t] = ym[s][t].merge(tmerge, left_index=True, right_index=True, suffixes=('_cm', ''))
        # ymi[s][t]= ym[s][t][ym[s][t].Year.isin(['2016', '2017', '2018', '2019', '2020'])].reset_index(drop=True)
        # ymi[s][t]['Monthi'] = pd.to_datetime(ymi[s][t].Month, format='%b', errors='coerce').dt.month
        # ymi[s][t].sort_values(by='Monthi', inplace=True)
        ymi[s][t] = ym[s][t].sort_values(by='Monthi')
        ymc[s][t] = ymi[s][t].groupby('Year').cumsum().merge(ymi[s][t], left_index=True, right_index=True,
                                                             suffixes=('_c', ''))
        ymc[s][t].drop(columns=['Monthi_c', 'mean_c', 'count_c'], inplace=True)

    ymp[s] = ymc[s]['Purchase_price_thb_ton'].merge(ymc[s]['MillWeight'],
                                                    left_on=['Year', 'Month', 'Monthi'],
                                                    right_on=['Year', 'Month', 'Monthi'])
    ymp[s]['Price'] = ymp[s]['Purchase_price_thb_ton'] / ymp[s]['MillWeight']
    ymp[s]['Price_c'] = ymp[s]['Purchase_price_thb_ton_c'] / ymp[s]['MillWeight_c']



def get_data_content():
    return wpmj, wpmsj, wpmjz, wpmsjzm, tls


def get_data_app():
    return ymc, ymp
