import datetime as dt

import pandas as pd
import pyodbc

ts = dt.datetime.now()
ts_str = ts.strftime("%Y_%m_%d_%H_%M_%S")
cnxn_str = (
    r'DRIVER=ODBC Driver 17 for SQL Server;'
    r'SERVER=172.31.228.90;'
    r'DATABASE=MPlanProd;'
    r'Trusted_Connection=no;'
    r'Uid=DataEng;'
    r'Pwd=Data@2020;'
)
con = pyodbc.connect(cnxn_str)
sql = "SELECT * FROM [MPlanProd].[dbo].[View_Transaction_SFT_6049]"
df = pd.read_sql(sql, con)
df = df.loc[df.Size_inch == 'ยูคาไม้ท่อน 2.0 นิ้ว']
ck=['SiteName', 'Sloc', 'Day','Month','Year', 'Time','MillWeight','Price_ton'] #WorkCentreName
df = df[ck]
df.to_csv('View_Transaction_SFT_6049_' + ts_str + '.csv', index=False)
print(dt.datetime.now() - ts, ts_str)
