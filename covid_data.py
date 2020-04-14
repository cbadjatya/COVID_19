import pandas as pd
import datetime
import requests
import numpy as np

date = datetime.date.today()
map_box_token = "pk.eyJ1IjoiY2hpbm1heTQ0MDAiLCJhIjoiY2s4d2htZ3FlMGU2aTNzbXdwZGQwZDZsayJ9.4Dm7PN7L6q5k4830GaiWUg"

url_excel = "https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-{}.xlsx"
url_csv = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv'

daily_data = pd.DataFrame()
df_total = pd.DataFrame()

def get_data():
    global daily_data
    global df_total
    # request = requests.get(url_excel.format(date))
    # i=0
    # while(request.status_code != 200):
    #     i = i+1
    #     request = requests.get(url_excel.format(date - datetime.timedelta(i)))
    # daily_data = pd.read_excel(url_excel.format((date - datetime.timedelta(i))))
    #
    # request = requests.get(url_csv.format(date.strftime("%m-%d-%Y")))
    # i=0
    # while(request.status_code != 200):
    #     i = i+1
    #     request = requests.get(url_csv.format((date - datetime.timedelta(i)).strftime("%m-%d-%Y")))
    # df_total = pd.read_csv(url_csv.format((date - datetime.timedelta(i)).strftime("%m-%d-%Y")))
    df_total = pd.read_csv("04-13-2020.csv")
    daily_data = pd.read_excel("COVID-19-geographic-disbtribution-worldwide-2020-04-13.xlsx")


def update_total():
    df_total_new = pd.DataFrame(columns=df_total.columns)
    countries = df_total["Country_Region"].unique()
    entry = dict()
    for each in countries:
        df = df_total.loc[df_total["Country_Region"]==each]
        entry["Confirmed"] = df["Confirmed"].sum()
        entry["Deaths"] = df["Deaths"].sum()
        entry["Recovered"] = df["Recovered"].sum()
        entry["Country_Region"] = each
        entry["Last_Update"] = df["Last_Update"].unique()[0]
        entry["Lat"] = df["Lat"].unique()[0]
        entry["Long_"] = df["Long_"].unique()[0]
        entry["Combined_Key"] = each
        df_total_new = df_total_new.append(entry,ignore_index=True)
    return df_total_new

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
