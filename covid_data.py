import datetime
import pandas as pd
import requests
import pycountry as pc

def get_data():
    date = datetime.date.today()

    url = ("https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-{}.xlsx").format(date)
    request = requests.get(url)
    if request.status_code == 200:
        df = pd.read_excel(url)
    else:
        url = ("https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-{}.xlsx").format(date - datetime.timedelta(1))
        df = pd.read_excel(url)

    date = df.iloc[0].dateRep.date()

    df = df.rename(columns = {
        'countriesAndTerritories':'Area',
        'deaths' : "Deaths",
        'cases' : 'Cases',
        'dateRep' : 'Date',
        'countryterritoryCode':'alpha3',
        })

    return df


def get_monthly_data(df):
    temp = df.copy()
    temp['month'] = temp['month'].apply(lambda x : str(x)) + "-" + temp['year'].apply(lambda x : str(x))
    months = temp['month'].unique().tolist()
    monthly = pd.DataFrame(columns=['Area','Month','Cases','Deaths','Id'])
    Areas = df['Area'].unique()
    for each in months:
        for area in Areas:
            row = {
                'Area': area,
                'Month': each,
                'Cases': temp.loc[(temp['Area']==area) & (temp['month']==each)]['Cases'].sum(),
                'Deaths':temp.loc[(temp['Area']==area) & (temp['month']==each)]['Deaths'].sum(),
                'alpha3': temp.loc[temp['Area']==area]['alpha3'].unique().tolist()[0]
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
            'alpha3':df.loc[df['Area']==each]['alpha3'].unique()[0]
        }
        total = total.append(row,ignore_index=True)
    total = total.sort_values(by='Cases', ascending=False)
    return total

def cumulative(data):

    dates = data['Date'].unique()
    cumulative = pd.DataFrame(columns=['Date','Cases','Deaths'])
    for each in dates:
        row = {
            'Date':each,
            'Cases':data.loc[data['Date']==each]['Cases'].sum(),
            'Deaths':data.loc[data['Date']==each]['Deaths'].sum(),
        }
        cumulative = cumulative.append(row,ignore_index=True)
    cumulative = cumulative.sort_values(by="Date")
    cumulative['Deaths'] = cumulative['Deaths'].cumsum()
    cumulative['Cases'] = cumulative['Cases'].cumsum()

    return cumulative
