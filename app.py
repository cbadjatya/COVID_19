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
app.title = 'COVID19'

server = app.server

df = covid_data.get_data()
df_total_new = covid_data.update_total()

bgcolor = "#f3f3f1"

marker_colors = {"Deaths":"black", "Confirmed":"red","Recovered":"green"}
map_colors = {
    "Deaths" : [marker_colors['Deaths']]*df_total_new['Deaths'].size,
    "Recovered" : [marker_colors['Recovered']]*df_total_new['Recovered'].size,
    "Confirmed" : [marker_colors["Confirmed"]]*df_total_new["Confirmed"].size,
}
# totals = covid_data.get_total_data(df)

# def get_daily_plot(df,area='ALL'):
#     if(area=='ALL'):
#         daily = pd.DataFrame(columns=['Date','Deaths','Cases'])
#         for date in df['Date'].unique():
#             row = {
#                 'Date':date,
#                 'Deaths':df.loc[df['Date']==date]['Deaths'].sum(),
#                 'Cases': df.loc[df['Date']==date]['Cases'].sum()
#             }
#             daily = daily.append(row,ignore_index=True)
#         fig = go.Figure(
#         data=[
#             go.Bar(name='Deaths', x=daily['Date'], y=daily['Deaths']),
#             go.Bar(name='Cases', x=daily['Date'], y=daily['Cases'])
#             ]
#         )
#         fig.update_layout(title='Global Daily Data',barmode='group',plot_bgcolor='lightgrey',
#                          legend=dict(
#                                     x=0,
#                                     y=1.0,
#                                     bgcolor='rgba(255, 255, 255, 0)',
#                                     bordercolor='rgba(255, 255, 255, 0)'
#                                 ),)
#     else:
#         daily = df.copy()
#         fig = go.Figure(
#         data=[
#             go.Bar(name='Deaths', x=daily['Date'], y=daily.loc[daily['Area']==area]['Deaths']),
#             go.Bar(name='Cases', x=daily['Date'], y=daily.loc[daily['Area']==area]['Cases'])
#             ]
#         )
#         fig.update_layout(barmode='group',plot_bgcolor='lightgrey',
#                          legend=dict(
#                                     x=0,
#                                     y=1.0,
#                                     bgcolor='rgba(255, 255, 255, 0)',
#                                     bordercolor='rgba(255, 255, 255, 0)'
#                                 ),)
#     return fig

# def countrywise_graph(df):
#     fig = go.Figure(
#     data=[
#         go.Bar(name='Deaths', x=totals.head(20)['Area'], y=totals.head(20)['Deaths']),
#         go.Bar(name='Cases', x=totals.head(20)['Area'], y=totals.head(20)['Cases'])
#         ]
#     )
#     fig.update_layout(
#         title='Area-wise status (20 most affected countries)',
#         xaxis_tickfont_size=1,
#         xaxis=dict(
#             title = "Area",
#             titlefont_size=16,
#             tickfont_size=12,
#         ),
#         legend=dict(
#             x=0,
#             y=1.0,
#             bgcolor='rgba(255, 255, 255, 0)',
#             bordercolor='rgba(255, 255, 255, 0)'
#         ),
#         barmode='group',
#         bargap=0.15, # gap between bars of adjacent location coordinates.
#         bargroupgap=0.1, # gap between bars of the same location coordinate.
#         plot_bgcolor='lightgrey'
#     )
#     return fig

template = {'layout': {'paper_bgcolor': bgcolor, 'plot_bgcolor': bgcolor}}

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

def global_map(df,kind):
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

# def cum_plot(data):
#     cum = covid_data.cumulative(data)
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(
#         x = cum['Date'],
#         y = cum['Deaths'],
#         name = "Deaths",
#         mode = "lines+markers"
#         )
#     )
#     fig.add_trace(go.Scatter(
#         x = cum['Date'],
#         y = cum['Cases'],
#         name = "Cases",
#         mode = "lines+markers"
#         )
#     )
#     fig.update_layout(
#         title='Total Cases (Date-wise)',
#         xaxis_tickfont_size=1,
#         xaxis=dict(
#             title = "Date",
#             titlefont_size=16,
#             tickfont_size=14,
#         ),
#         legend=dict(
#             x=0,
#             y=1.0,
#             bgcolor='rgba(255, 255, 255, 0)',
#         ),
#         plot_bgcolor='lightgrey'
#     )
#     return fig

# Areas = [
#     {'label':i, 'value':i} for i in df['Area'].unique()
# ]
# Areas.append({'label':'All', 'value':'ALL'})

app.layout = html.Div(
        id = "root",
        children=[
        html.Div([
            html.H1(children=[
                'COVID 19 Tracker',
            ], style={'text-align': 'left'}),
        ]),
        html.Div(
            children=[
                html.Div(children=[
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
                html.Div(children=[
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
                html.Div(children=[
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
                    className='six columns pretty_container', id="indicator-div"
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
            )
        ], className='twelve columns pretty_container',
            style={
                'width': '98%',
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
    return global_map(df_total_new,value)


# @app.callback(
#     Output('DateWise','figure'),
#     [Input('Country','value')]
# )
# def make_charts(value):
#     return get_daily_plot(df,value)



if __name__ == '__main__':
    app.run_server(debug=True)
