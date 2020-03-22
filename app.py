import covid_data

import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

external_stylesheets = ['https://github.com/plotly/dash-app-stylesheets/blob/master/dash-technical-charting.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = covid_data.get_data()

covid_data.updateId(df)

def get_daily_plot(df,area='CHINA'):
    if(area=='ALL'):
        daily = pd.DataFrame(columns=['Date','Deaths','Cases'])
        for date in df['DateRep'].unique():
            row = {
                'Date':date,
                'Deaths':df.loc[df['DateRep']==date]['Deaths'].sum(),
                'Cases': df.loc[df['DateRep']==date]['Cases'].sum()
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
            go.Bar(name='Deaths', x=daily['DateRep'], y=daily.loc[daily['Area']==area]['Deaths']),
            go.Bar(name='Cases', x=daily['DateRep'], y=daily.loc[daily['Area']==area]['Cases'])
            ]
        )
        fig.update_layout(title = area,barmode='group',plot_bgcolor='lightgrey',
                         legend=dict(
                                    x=0,
                                    y=1.0,
                                    bgcolor='rgba(255, 255, 255, 0)',
                                    bordercolor='rgba(255, 255, 255, 0)'
                                ),)
    return fig

def countrywise_graph(df):
    total = covid_data.get_total_data(df)
    fig = go.Figure(
    data=[
        go.Bar(name='Deaths', x=total['Area'], y=total['Deaths']),
        go.Bar(name='Cases', x=total['Area'], y=total['Cases'])
        ]
    )
    fig.update_layout(
        title='Areawise status',
        xaxis_tickfont_size=1,
        xaxis=dict(
            title = "Area",
            titlefont_size=16,
            tickfont_size=7,
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
    df = covid_data.get_total_data(df)
    fig = go.Figure(data=go.Choropleth(
        locations = df['Id'],
        z = df[kind],
        text = df['Area'],
        autocolorscale=False,
        reversescale=True,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        colorbar_title = kind,
        colorscale = 'Greens',
    ))

    fig.update_layout(
        title_text='COVID_19 World Map',
        height=1000,
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
        ),
    )

    return fig


Areas = [
    {'label':i, 'value':i} for i in df['Area'].unique()
]
Areas.append({'label':'All', 'value':'ALL'})


app.layout = html.Div(children=[
    dcc.Tabs(
        children=[
            dcc.Tab(label = 'GeoMap',children=[
                html.Div( id = 'makeMap',
                    children=[
                        html.Div(
                            html.H1("Global map with latest data")
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
            dcc.Tab(label = 'charts',children=[
                dcc.Dropdown(id = 'Country',
                    options = Areas,
                    value = 'CHINA',
                ),
                dcc.Graph(
                    id = 'DateWise',
                ),
                dcc.Graph(
                    id = 'CountryWise',
                    figure = countrywise_graph(df)
                )
            ])
        ]
    ),
])


@app.callback(
    Output('GlobalMap','figure'),
    [Input('ChooseMap','value')]
)
def make_map(value):
    return global_map(df,value)


@app.callback(
    Output('DateWise','figure'),
    [Input('Country','value')]
)
def make_charts(value):
    return get_daily_plot(df,value)



if __name__ == '__main__':
    app.run_server(debug=True)
