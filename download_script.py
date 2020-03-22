import datetime
import pandas as pd
import requests

def get_data():
    date = datetime.date.today()
    url = ("https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-{}.xlsx").format(date)
    request = requests.get(url)
    if request.status_code == 200:
        return pd.read_excel(url)
    date = date - datetime.timedelta(1)
    url = ("https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-{}.xlsx").format(date)
    request = requests.get(url)
    if request.status_code == 200:
        return pd.read_excel(url)

def get_monthly_data(df):
    temp = df.copy()
    temp['Month'] = temp['Month'].apply(lambda x : str(x)) + "-" + temp['Year'].apply(lambda x : str(x))
    months = temp['Month'].unique().tolist()
    monthly = pd.DataFrame(columns=['Area','Month','Cases','Deaths','Id'])
    for each in months:
        for area in Areas:
            row = {
                'Area': area,
                'Month': each,
                'Cases': temp.loc[(temp['Area']==area) & (temp['Month']==each)]['Cases'].sum(),
                'Deaths':temp.loc[(temp['Area']==area) & (temp['Month']==each)]['Deaths'].sum(),
                'Id': temp.loc[temp['Area']==area]['GeoId'].unique().tolist()[0]
            }
            monthly = monthly.append(row,ignore_index=True)
    return monthly

def get_total_data(df):
    total = pd.DataFrame(columns = ['Area','Cases','Deaths','Id'])
    Areas = daily['Area'].unique()
    for each in Areas:
        row = {
            'Area':each,
            'Cases': daily.loc[daily['Area']==each]['Cases'].sum(),
            'Deaths': daily.loc[daily['Area']==each]['Deaths'].sum(),
            'Id':daily.loc[daily['Area']==each]['GeoId'].unique()[0]
        }
        total = total.append(row,ignore_index=True)
    return total
