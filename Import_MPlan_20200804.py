#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd, numpy as np
#pd.options.display.float_format = '{:,.2f}'.format


# In[2]:


sql = 'SELECT * FROM [MPlanProd].[dbo].[View_Transaction_SFT_6049]'
con = (
    r'DRIVER=ODBC Driver 17 for SQL Server;'
    r'SERVER=172.31.228.90;'
    r'DATABASE=MPlanProd;'
    r'Trusted_Connection=no;'
    r'Uid=DataEng;'
    r'Pwd=Data@2020;'
)


# In[3]:


import pyodbc
cxn = pyodbc.connect(con)
df = pd.read_sql(sql, cxn)
', '.join(df.columns)


# In[4]:


df = df.loc[df.Size_inch=='ยูคาไม้ท่อน 2.0 นิ้ว']
df = df.loc[~df.SiteName.isin(['สามง่าม','วังวน','ตาก','บางกระทุ่ม', 'CC6'])]
df.loc[df.SiteName=='โรงสับไม้กำแพงเพชร', 'Sloc'] = 'CH11'
df.loc[df.SiteName=='โรงสับไม้ชุมพวง', 'Sloc'] = 'CH12'
df.loc[df.SiteName=='โรงสับไม้พระยืน', 'Sloc'] = 'CH13'
df['Zone'] = df['Sloc'].str[:2]


# In[5]:


#df.SiteName.value_counts()#.sum()


# In[6]:


#df.Sloc.value_counts()#.sum()


# In[7]:


df['dt'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
#df['dt'] = pd.to_datetime(df['dt'].astype(str) + ' ' + df['Time'].astype(str))
df.drop(['Year', 'Month', 'Day'], axis=1, inplace=True)


# In[8]:


ck=['Zone','Sloc','SiteName','Ticket_no','dt','Time','MillWeight','Price_ton', 'Purchase_price_thb_ton'] #WorkCentreName, 'Day','Month','Year', 'Time'
df = df[ck]


# In[9]:


SlocDICT = dict(df.groupby('SiteName')['Sloc'].max())
SlocDICT = dict([(value, key) for key, value in SlocDICT.items()])
ZoneDICT = df.groupby('Zone').agg({'Sloc': lambda x: list(np.unique(x))})['Sloc'].to_dict()


# In[10]:


import datetime as dt; ts = dt.datetime.now(); ts_str = ts.strftime("%Y_%m_%d_%H_%M_%S"); print(ts_str)
df.to_csv('View_Transaction_SFT_6049_'+ts_str+'.csv', index=False)

df = pd.read_csv('View_Transaction_SFT_6049_'+ts_str+'.csv', parse_dates=True)
# In[11]:


df_s = {}
for s in SlocDICT.keys():
    df_s[s] = df.loc[df.Sloc==s].groupby('dt').sum().reset_index()
    df_s[s]['Price_Daily'] = df_s[s]['Purchase_price_thb_ton']/df_s[s]['MillWeight']
    df_s[s].drop('Price_ton', axis=1 ,inplace=True)
    df_s[s] = df_s[s].to_json(orient = 'records')


# In[12]:


import json
with open('Sloc.json', 'w') as o: json.dump(SlocDICT, o)
with open('Zone.json', 'w') as o: json.dump(ZoneDICT, o)
with open('wp.json', 'w') as o: json.dump(df_s, o)
with open('wp.json', 'r') as o: wp = json.load(o)


# In[13]:


for s in SlocDICT.keys():
    wp[s] = pd.read_json(wp[s], orient = 'records')


# In[14]:


wp[s]


# In[15]:


SlocDICT


# In[16]:


ZoneDICT


# In[ ]:




