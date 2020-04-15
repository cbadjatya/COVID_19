import pandas as pd
import datetime
import requests
import numpy as np

date = datetime.date.today()
map_box_token = "pk.eyJ1IjoiY2hpbm1heTQ0MDAiLCJhIjoiY2s4d2htZ3FlMGU2aTNzbXdwZGQwZDZsayJ9.4Dm7PN7L6q5k4830GaiWUg"

url_excel = "https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-{}.xlsx"
url_csv = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv'

def get_total_data():
    """
    Download the latest csv file available at Johns Hopkins' github repository
    """
    # request = requests.get(url_csv.format(date.strftime("%m-%d-%Y")))
    # i=0
    # while(request.status_code != 200):
    #     i = i+1
    #     request = requests.get(url_csv.format((date - datetime.timedelta(i)).strftime("%m-%d-%Y")))
    # df_total = pd.read_csv(url_csv.format((date - datetime.timedelta(i)).strftime("%m-%d-%Y")))
    df_total = pd.read_csv("04-13-2020.csv")
    return df_total

def get_daily_data():
    """
    Download the latest excel file made available by ECDC
    """
    # request = requests.get(url_excel.format(date))
    # i=0
    # while(request.status_code != 200):
    #     i = i+1
    #     request = requests.get(url_excel.format(date - datetime.timedelta(i)))
    # daily_data = pd.read_excel(url_excel.format((date - datetime.timedelta(i))))
    daily_data = pd.read_excel("COVID-19-geographic-disbtribution-worldwide-2020-04-13.xlsx")
    daily_data = daily_data.sort_values(by='dateRep')
    return daily_data

df_daily = get_daily_data() #New Deaths and Cases observed in each country since the outbreak
df_total = get_total_data() #Total confirmed cases, recovered cases and deaths in each country and some regions

def df_total_country_wise():
    """
    Total Cases and Deaths for each country
    """
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
        entry["Active"] = df["Active"].sum()
        df_total_new = df_total_new.append(entry,ignore_index=True)
    return df_total_new

def get_daily_countrywise_cumulative_data():
    """
    cumulative data for each country. Each entry shows total cases and deaths observed in 'countryAndTerritories' till 'dateRep'.
    """
    df_new = pd.DataFrame(columns=df_daily.columns)
    countries = df_daily["countriesAndTerritories"].unique()
    for each in countries:
        df = df_daily.loc[df_daily["countriesAndTerritories"]==each]
        df.deaths = df.deaths.cumsum(axis=0)
        df.cases = df.cases.cumsum(axis=0)
        df_new = df_new.append(df)
    return df_new

def get_total_daily_data():
    """
    cumulative data for each date. Each entry shows total cases and deaths worldwide on that day.
    """
    data = df_daily
    dates = data['dateRep'].unique()
    cumulative = pd.DataFrame(columns=['Date','Total Cases','Total Deaths'])
    for each in dates:
        row = {
            'Date':each,
            'Total Cases':data.loc[data['dateRep']==each]['cases'].sum(),
            'Total Deaths':data.loc[data['dateRep']==each]['deaths'].sum(),
        }
        cumulative = cumulative.append(row,ignore_index=True)
    cumulative = cumulative.sort_values(by="Date")
    cumulative['Total Deaths'] = cumulative['Total Deaths'].cumsum()
    cumulative['Total Cases'] = cumulative['Total Cases'].cumsum()

    return cumulative
