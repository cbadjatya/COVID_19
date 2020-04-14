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

marker_colors = {"Deaths":"black", "Confirmed":"red","Recovered":"green"}
map_colors = {
    "Deaths" : [marker_colors['Deaths']]*df_total_new['Deaths'].size,
    "Recovered" : [marker_colors['Recovered']]*df_total_new['Recovered'].size,
    "Confirmed" : [marker_colors["Confirmed"]]*df_total_new["Confirmed"].size,
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
            'showline': True,
        },
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
        ),
        plot_bgcolor=bgcolor,
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
            )]
    )

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
    fig=px.scatter_mapbox(df, lat="Lat", lon="Long_",
                              hover_name="Combined_Key", hover_data=[kind], color = "Combined_Key",
                               size = np.tanh(abs(np.array(df[kind].tolist())/4000))*6000,
                          color_discrete_sequence = map_colors[kind],
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
            'showline': True,
        },
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
        ),
        plot_bgcolor=bgcolor,
    )
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
                            # html.Img(
                            #     id='show-indicator-modal',
                            #     src="assets/question-circle-solid.svg",
                            #     n_clicks=0,
                            #     className='info-icon',
                            # ),
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
                    className='six columns pretty_container',
                    ),
                html.Div(id = "total_deaths",children=[
                        html.H4([
                            "Total Deaths",
                            # html.Img(
                            #     id='show-indicator-modal',
                            #     src="assets/question-circle-solid.svg",
                            #     n_clicks=0,
                            #     className='info-icon',
                            # ),
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
                    className='six columns pretty_container',
                    ),
                html.Div(id = "total_recovered",children=[
                        html.H4([
                            "Recovered",
                            # html.Img(
                            #     id='show-indicator-modal',
                            #     src="assets/question-circle-solid.svg",
                            #     n_clicks=0,
                            #     className='info-icon',
                            # ),
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
                    className='six columns pretty_container'
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
                    {'label':'Recovered','value':'Recovered'}
                ],
                value='Confirmed',
            ),
            dcc.Graph(
                id='GlobalMap',
            )],
              className='twelve columns pretty_container',
                style={
                    'width': '100%',
                    'margin-right': '0',
                },
                id="map-div"
        ),
        # html.Div(
        #     dcc.Tabs(
        #         children=[
        #             dcc.Tab(label = 'Global Map',children=[
        #                 html.Div( id = 'makeMap',
        #                     children=[
        #                         html.Div(
        #                             html.H3("Global Data as of {}".format(date))
        #                         ),
        #                         dcc.Dropdown(
        #                             id = 'ChooseMap',
        #                             options = [
        #                                 {'label':'Deaths','value':'Deaths'},
        #                                 {'label':'Cases','value':'Cases'}
        #                             ],
        #                             value='Cases',
        #                         ),
        #                         dcc.Graph(
        #                             id='GlobalMap',
        #                         )
        #                     ]
        #                 )
        #             ]),
        #             dcc.Tab(label = 'Charts',children=[
        #                 html.Div(children=[
        #                     dcc.Dropdown(id = 'Country',
        #                         options = Areas,
        #                         value = 'ALL',
        #                     ),
        #                     dcc.Graph(
        #                         id = 'DateWise',
        #                     ),
        #                 ],
        #                     style={'width': '49%', 'display': 'inline-block'}
        #                 ),
        #                 html.Div(
        #                     children=[
        #                         dcc.Graph(
        #                             id = "cumulative",
        #                             figure = cum_plot(df)
        #                         ),
        #                     ],
        #                     style={'width': '49%', 'display': 'inline-block'}
        #                 ),
        #                 dcc.Graph(
        #                     id = 'CountryWise',
        #                     figure = countrywise_graph(totals)
        #                 )
        #             ]),
        #             dcc.Tab(label='Table',children=[
        #                 dash_table.DataTable(
        #                     id = 'table',
        #                     columns = [{'name':i, 'id':i} for i in totals.columns],
        #                     data = totals.to_dict('records'),
        #                     style_cell={'textAlign': 'left'},
        #                     style_header={
        #                         'backgroundColor': 'white',
        #                         'fontWeight': 'bold'
        #                     },
        #                     style_cell_conditional=[
        #                         {
        #                             'if': {'column_id': 'Region'},
        #                             'textAlign': 'left'
        #                         },
        #                     ],
        #                     # style_as_list_view=True,
        #                     style_table={
        #                             'maxHeight': '900px',
        #                             'overflowY': 'scroll'
        #                         },
        #                 )
        #             ])
        #         ],
        #     ),
        # ),
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
