import datetime
import pandas as pd
import requests
import pycountry as pc

def updateId(df):
    def updateId(Id):
        try:
            Id = pc.countries.get(alpha_2=Id).alpha_3
        except:
            pass
        return Id
    df['GeoId'] = df['GeoId'].apply(updateId)

def get_data():
    df = pd.DataFrame()
    date = datetime.date.today()
    url = ("https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-{}.xlsx").format(date)
    request = requests.get(url)
    if request.status_code == 200:
        df = pd.read_excel(url)
    else:
        date = date - datetime.timedelta(1)
        url = ("https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-{}.xlsx").format(date)
        request = requests.get(url)
        if request.status_code == 200:
            df = pd.read_excel(url)
    df = df.rename(columns = {'Countries and territories':'Area'})
    df['Area'] = df['Area'].apply(lambda x : x.upper())
    return [df,date]

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
    Areas = df['Area'].unique()
    for each in Areas:
        row = {
            'Area':each,
            'Cases': df.loc[df['Area']==each]['Cases'].sum(),
            'Deaths': df.loc[df['Area']==each]['Deaths'].sum(),
            'Id':df.loc[df['Area']==each]['GeoId'].unique()[0]
        }
        total = total.append(row,ignore_index=True)
    total = total.sort_values(by='Cases', ascending=False)
    return total

def cumulative(data):

    dates = data['DateRep'].unique()
    cumulative = pd.DataFrame(columns=['DateRep','Cases','Deaths'])
    for each in dates:
        row = {
            'DateRep':each,
            'Cases':data.loc[data['DateRep']==each]['Cases'].sum(),
            'Deaths':data.loc[data['DateRep']==each]['Deaths'].sum(),
        }
        cumulative = cumulative.append(row,ignore_index=True)
    cumulative = cumulative.sort_values(by="DateRep")
    cumulative['Deaths'] = cumulative['Deaths'].cumsum()
    cumulative['Cases'] = cumulative['Cases'].cumsum()

    return cumulative
