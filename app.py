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

external_stylesheets = ['https://github.com/plotly/dash-app-stylesheets/blob/master/dash-technical-charting.css']
tabs_styles = {
    'height': '44px'
}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'COVID19'

server = app.server

df = covid_data.get_data()
date = df.iloc[0].Date.date()

totals = covid_data.get_total_data(df)

def get_daily_plot(df,area='ALL'):
    if(area=='ALL'):
        daily = pd.DataFrame(columns=['Date','Deaths','Cases'])
        for date in df['Date'].unique():
            row = {
                'Date':date,
                'Deaths':df.loc[df['Date']==date]['Deaths'].sum(),
                'Cases': df.loc[df['Date']==date]['Cases'].sum()
            }
            daily = daily.append(row,ignore_index=True)
        fig = go.Figure(
        data=[
            go.Bar(name='Deaths', x=daily['Date'], y=daily['Deaths']),
            go.Bar(name='Cases', x=daily['Date'], y=daily['Cases'])
            ]
        )
        fig.update_layout(title='Global Daily Data',barmode='group',plot_bgcolor='lightgrey',
                         legend=dict(
                                    x=0,
                                    y=1.0,
                                    bgcolor='rgba(255, 255, 255, 0)',
                                    bordercolor='rgba(255, 255, 255, 0)'
                                ),)
    else:
        daily = df.copy()
        fig = go.Figure(
        data=[
            go.Bar(name='Deaths', x=daily['Date'], y=daily.loc[daily['Area']==area]['Deaths']),
            go.Bar(name='Cases', x=daily['Date'], y=daily.loc[daily['Area']==area]['Cases'])
            ]
        )
        fig.update_layout(barmode='group',plot_bgcolor='lightgrey',
                         legend=dict(
                                    x=0,
                                    y=1.0,
                                    bgcolor='rgba(255, 255, 255, 0)',
                                    bordercolor='rgba(255, 255, 255, 0)'
                                ),)
    return fig

def countrywise_graph(df):
    fig = go.Figure(
    data=[
        go.Bar(name='Deaths', x=totals.head(20)['Area'], y=totals.head(20)['Deaths']),
        go.Bar(name='Cases', x=totals.head(20)['Area'], y=totals.head(20)['Cases'])
        ]
    )
    fig.update_layout(
        title='Area-wise status (20 most affected countries)',
        xaxis_tickfont_size=1,
        xaxis=dict(
            title = "Area",
            titlefont_size=16,
            tickfont_size=12,
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.15, # gap between bars of adjacent location coordinates.
        bargroupgap=0.1, # gap between bars of the same location coordinate.
        plot_bgcolor='lightgrey'
    )
    return fig

def global_map(df,kind):

    # df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv')

    data = covid_data.get_total_data(df)

    if(kind == 'Deaths'):
        size_kind = np.tanh(abs(np.array(data['Deaths'].tolist())/800))*600
    else:
        size_kind = np.tanh(abs(np.array(data.Cases.tolist())/20000))*600

    fig = px.scatter_geo(data, locations="alpha3", color="Area",
                         hover_name="Area", size=size_kind, hover_data=[kind],
                         projection="orthographic")
    fig.update_layout(
        title_text='COVID_19 World Map',
        height=900,
    )

    return fig

def cum_plot(data):
    cum = covid_data.cumulative(data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x = cum['Date'],
        y = cum['Deaths'],
        name = "Deaths",
        mode = "lines+markers"
        )
    )
    fig.add_trace(go.Scatter(
        x = cum['Date'],
        y = cum['Cases'],
        name = "Cases",
        mode = "lines+markers"
        )
    )
    fig.update_layout(
        title='Total Cases (Date-wise)',
        xaxis_tickfont_size=1,
        xaxis=dict(
            title = "Date",
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
        ),
        plot_bgcolor='lightgrey'
    )
    return fig

Areas = [
    {'label':i, 'value':i} for i in df['Area'].unique()
]
Areas.append({'label':'All', 'value':'ALL'})

app.layout = html.Div(children=[
        html.Div(
            dcc.Tabs(
                children=[
                    dcc.Tab(label = 'Global Map',children=[
                        html.Div( id = 'makeMap',
                            children=[
                                html.Div(
                                    html.H3("Global Data as of {}".format(date))
                                ),
                                dcc.Dropdown(
                                    id = 'ChooseMap',
                                    options = [
                                        {'label':'Deaths','value':'Deaths'},
                                        {'label':'Cases','value':'Cases'}
                                    ],
                                    value='Cases',
                                ),
                                dcc.Graph(
                                    id='GlobalMap',
                                )
                            ]
                        )
                    ]),
                    dcc.Tab(label = 'Charts',children=[
                        html.Div(children=[
                            dcc.Dropdown(id = 'Country',
                                options = Areas,
                                value = 'ALL',
                            ),
                            dcc.Graph(
                                id = 'DateWise',
                            ),
                        ],
                            style={'width': '49%', 'display': 'inline-block'}
                        ),
                        html.Div(
                            children=[
                                dcc.Graph(
                                    id = "cumulative",
                                    figure = cum_plot(df)
                                ),
                            ],
                            style={'width': '49%', 'display': 'inline-block'}
                        ),
                        dcc.Graph(
                            id = 'CountryWise',
                            figure = countrywise_graph(totals)
                        )
                    ]),
                    dcc.Tab(label='Table',children=[
                        dash_table.DataTable(
                            id = 'table',
                            columns = [{'name':i, 'id':i} for i in totals.columns],
                            data = totals.to_dict('records'),
                            style_cell={'textAlign': 'left'},
                            style_header={
                                'backgroundColor': 'white',
                                'fontWeight': 'bold'
                            },
                            style_cell_conditional=[
                                {
                                    'if': {'column_id': 'Region'},
                                    'textAlign': 'left'
                                },
                            ],
                            # style_as_list_view=True,
                            style_table={
                                    'maxHeight': '900px',
                                    'overflowY': 'scroll'
                                },
                        )
                    ])
                ],
                style = tabs_styles
            ),
        ),
],
)


@app.callback(
    Output('GlobalMap','figure'),
    [Input('ChooseMap','value')]
)
def make_map(value):
    return global_map(totals,value)


@app.callback(
    Output('DateWise','figure'),
    [Input('Country','value')]
)
def make_charts(value):
    return get_daily_plot(df,value)



if __name__ == '__main__':
    app.run_server(debug=True)
