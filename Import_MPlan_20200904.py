import json

import numpy as np
import pandas as pd
import pyodbc

sql = 'SELECT * FROM [MPlanProd].[dbo].[View_Transaction_SFT_6049]'
con = (
    r'DRIVER=ODBC Driver 17 for SQL Server;'
    r'SERVER=172.31.228.90;'
    r'DATABASE=MPlanProd;'
    r'Trusted_Connection=no;'
    r'Uid=DataEng;'
    r'Pwd=Data@2020;'
)

cxn = pyodbc.connect(con)
df = pd.read_sql(sql, cxn)
', '.join(df.columns)

df = df.loc[df.Size_inch == 'ยูคาไม้ท่อน 2.0 นิ้ว']
df = df.loc[~df.SiteName.isin(['สามง่าม', 'วังวน', 'ตาก', 'บางกระทุ่ม', 'CC6'])]
df.loc[df.SiteName == 'โรงสับไม้กำแพงเพชร', 'Sloc'] = 'CH11'
df.loc[df.SiteName == 'โรงสับไม้ชุมพวง', 'Sloc'] = 'CH12'
df.loc[df.SiteName == 'โรงสับไม้พระยืน', 'Sloc'] = 'CH13'
df['Zone'] = df['Sloc'].str[:2]

SlocDICT = dict(df.groupby('SiteName')['Sloc'].max())
SlocDICT = dict([(value, key) for key, value in SlocDICT.items()])
ZoneDICT = df.groupby('Zone').agg({'Sloc': lambda x: list(np.unique(x))})['Sloc'].to_dict()

ck = ['Zone', 'Sloc', 'SiteName', 'Ticket_no', 'Year', 'Month', 'Day', 'MillWeight', 'Price_ton',
      'Purchase_price_thb_ton']
df = df[ck]

wp = {}
for s in SlocDICT.keys():
    df_ = df.loc[df.Sloc == s].groupby(['Year', 'Month', 'Day']).sum().reset_index()
    df_['Price_Daily'] = df_['Purchase_price_thb_ton'] / df_['MillWeight']
    df_.drop('Price_ton', axis=1, inplace=True)
    wp[s] = df_.to_json(orient='records')

with open('Sloc.json', 'w') as o: json.dump(SlocDICT, o)
with open('Zone.json', 'w') as o: json.dump(ZoneDICT, o)
with open('wp.json', 'w') as o: json.dump(wp, o)
with open('wp.json', 'r') as o: wp = json.load(o)
