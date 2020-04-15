import covid_data

import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table

from dash.dependencies import Input, Output

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

server = app.server
app.title = 'COVID19 Tracker'

df_total = covid_data.df_total
df_daily = covid_data.df_daily
df_total_new = covid_data.df_total_country_wise()

bgcolor = "#f3f3f1"

marker_colors = {"Deaths":"black", "Confirmed":"red","Recovered":"green", "Active":"blue"}
map_colors = {
    "Deaths" : [marker_colors['Deaths']]*df_total_new['Deaths'].size,
    "Recovered" : [marker_colors['Recovered']]*df_total_new['Recovered'].size,
    "Confirmed" : [marker_colors["Confirmed"]]*df_total_new["Confirmed"].size,
    "Active": [marker_colors["Active"]]*df_total_new["Active"].size,
}

template = {'layout': {'paper_bgcolor': bgcolor, 'plot_bgcolor': bgcolor}}


def daily_plot_country_wise():
    """
    Plot total cases and deaths till date in top-30 countries
    """
    data = covid_data.get_daily_countrywise_cumulative_data()

    visible_list_cases = [True]*30
    visible_list_cases.extend([False]*30)
    visible_list_deaths = [False]*30
    visible_list_deaths.extend([True]*30)

    fig = go.Figure()

    data = data.sort_values(by='cases',ascending=False)
    top30 = (data["countriesAndTerritories"].unique())[:30]

    for each in top30:
        fig.add_trace(go.Scatter(
            x = data.loc[data['countriesAndTerritories']==each]['dateRep'],
            y = data.loc[data['countriesAndTerritories']==each]["cases"],
            name = each,
            mode = "lines"
            )
        )


    data = data.sort_values(by='deaths',ascending=False)
    top30 = (data["countriesAndTerritories"].unique())[:30]
    for each in top30:
        fig.add_trace(go.Scatter(
            x = data.loc[data['countriesAndTerritories']==each]['dateRep'],
            y = data.loc[data['countriesAndTerritories']==each]["deaths"],
            name = each,
            mode = "lines"
            )
        )

    fig.update_layout(
        xaxis=dict(
            title = "Date",
            titlefont_size=16,
            tickfont_size=14,
            showgrid = False
        ),
        yaxis = {
            'showgrid': False,
            'showline': False,
        },
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
        ),
        plot_bgcolor=bgcolor,
        paper_bgcolor = bgcolor,
        updatemenus = [
                dict(
                    active = 0,
                    buttons = list([
                        dict(
                            label = "Cases",
                            method = "update",
                            args=[{'visible':visible_list_cases, 'title' : 'New Cases'}]
                        ),
                        dict(
                            label = "Deaths",
                            method = "update",
                            args=[{'visible':visible_list_deaths,'title' : 'New Deaths'}]
                        )
                    ]
                ),
            )],
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig

def show_numbers(id):
    """
    Show latest Numbers
    """
    return{
        'data': [{
            'type': 'indicator',
            'value': df_total_new[id].sum(),
            'number': {
                'font': {
                    'color': marker_colors[id],
                }
            }
        }],
        'layout': {
            'template': template,
            'height': 150,
            'xaxis': {'visible': False},
            'yaxis': {'visible': False},
            'margin': {'l': 10, 'r': 10, 't': 10, 'b': 10}
        }
    }

def global_map(kind):
    df = df_total_new
    px.set_mapbox_access_token(covid_data.map_box_token)

    sizes = {
        "Deaths" : np.tanh(abs(np.array(df["Deaths"].tolist())/4000))*8000,
        "Confirmed" : np.tanh(abs(np.array(df["Confirmed"].tolist())/4000))*6000,
        "Recovered" : np.tanh(abs(np.array(df["Recovered"].tolist())/4000))*7000,
        "Active" : np.tanh(abs(np.array(df["Active"].tolist())/4000))*6000
    }

    fig=px.scatter_mapbox(df, lat="Lat", lon="Long_",
                              hover_name="Country_Region", hover_data=[kind], color = "Country_Region",
                               size = sizes[kind],
                          color_discrete_sequence = map_colors[kind], opacity=0.5,
                             height=400)
    fig.update_layout(mapbox_style="light",
                      mapbox=dict(
                        bearing=0,
                        center=go.layout.mapbox.Center(
                            lat=20,
                            lon=78
                        ),
                        pitch=0,
                        zoom=1
                        ),
                      showlegend=False,
                     )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

def make_total_datewise_plots():
    """
    Total deaths and cases worldwide on each date since outbreak
    """
    df = covid_data.get_total_daily_data()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x = df["Date"],
            y = df["Total Cases"],
            name = "Total Cases",
            mode = "markers+lines",
            marker = dict(
                color = "red"
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x = df["Date"],
            y = df["Total Deaths"],
            name = "Total Deaths",
            mode = "markers+lines",
            marker = dict(
                color = "black"
            )
        )
    )

    fig.update_layout(
        title = "Total Cases and Deaths (Daily)",
        xaxis=dict(
            title = "Date",
            titlefont_size=16,
            tickfont_size=14,
            showgrid = False
        ),
        yaxis = {
            'showgrid': False,
            'showline': False,
        },
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
        ),
        plot_bgcolor=bgcolor,
        paper_bgcolor = bgcolor,
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

app.layout = html.Div(
        id = "root",
        children=[
        html.Header(children=[
            html.H1(
                children=[
                    'COVID-19 Tracker',
                ]),
            ],
                className = "header"
        ),
            html.Div(
                children=[
                    html.Div(id = "total_confirmed",children=[
                        html.H4([
                            "Confirmed Cases",
                        ], className="container_title"),
                        dcc.Loading(
                            dcc.Graph(
                                className='indicator-graph',
                                figure=show_numbers("Confirmed"),
                                config={'displayModeBar': False},
                            ),
                            className='svg-container',
                            style={'height': 150},),
                        ],
                    className='three columns pretty_container',
                    ),
                html.Div(id = "total_deaths",children=[
                        html.H4([
                            "Total Deaths",
                        ], className="container_title"),
                        dcc.Loading(
                            dcc.Graph(
                                className='indicator-graph',
                                figure=show_numbers("Deaths"),
                                config={'displayModeBar': False},
                            ),
                            className='svg-container',
                            style={'height': 150},),
                        ],
                    className='three columns pretty_container',
                    ),
                html.Div(id = "total_recovered",children=[
                        html.H4([
                            "Recovered",
                        ], className="container_title"),
                        dcc.Loading(
                            dcc.Graph(
                                className='indicator-graph',
                                figure=show_numbers("Recovered"),
                                config={'displayModeBar': False},
                            ),
                            className='svg-container',
                            style={'height': 150},),
                        ],
                    className='three columns pretty_container'
                    ),
                    html.Div(id = "active",children=[
                            html.H4([
                                "Active",
                            ], className="container_title"),
                            dcc.Loading(
                                dcc.Graph(
                                    className='indicator-graph',
                                    figure=show_numbers("Active"),
                                    config={'displayModeBar': False},
                                ),
                                className='svg-container',
                                style={'height': 150},),
                            ],
                        className='three columns pretty_container'
                        )
            ]
        ),

        html.Div(children=[
            html.H4([
                "Locations",
            ], className="container_title"),
            dcc.Dropdown(
                id = 'ChooseMap',
                options = [
                    {'label':'Deaths','value':'Deaths'},
                    {'label':'Confirmed','value':'Confirmed'},
                    {'label':'Recovered','value':'Recovered'},
                    {'label':'Active','value':'Active'}
                ],
                value='Confirmed',
            ),
            dcc.Graph(
                id='GlobalMap',
            )],
              className='twelve columns pretty_container',
                style={
                    'width': '98%',
                    'margin-right': '0',
                },
                id="map-div"
        ),
        html.Div(children=[
            html.Div(
                children=[
                    html.H4([
                        "Top 30 Regions",
                    ], className="container_title"),
                    dcc.Graph(
                        id='top30',
                        figure=daily_plot_country_wise(),
                        config={'displayModeBar': False}
                    ),
                ],
                className='six columns pretty_container'
            ),
            html.Div(
                children=[
                    html.H4([
                        "Worldwide Plot",
                    ], className="container_title"),
                    dcc.Graph(
                        id='global-datewise',
                        config={'displayModeBar': False},
                        figure=make_total_datewise_plots(),
                    ),
                ],
                className='six columns pretty_container'
            ),
        ]),
    ],
)


@app.callback(
    Output('GlobalMap','figure'),
    [Input('ChooseMap','value')]
)
def make_map(value):
    return global_map(value)


# @app.callback(
#     Output('DateWise','figure'),
#     [Input('Country','value')]
# )
# def make_charts(value):
#     return get_daily_plot(df,value)



if __name__ == '__main__':
    app.run_server(debug=True)
