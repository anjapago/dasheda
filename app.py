# Based off of example at https://community.plotly.com/t/running-dash-app-in-docker-container/16067
# https://medium.com/@megah_f/build-a-covid-19-map-with-python-and-plotly-dash-91a9fe58dfde
# https://plotly.com/python/choropleth-maps/

import dash
import dash_core_components as dcc
import dash_html_components as html
import flask
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
                   
from urllib.request import urlopen
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server,external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

colors = { 'background' : 'white', 'text' : 'black' }

countries = []

code_df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv')

for country in code_df['CODE']:
    countries.append({ 'label': country.lower(), 'value': country.lower()})

app.layout = html.Div(
    style={'backgroundColor': colors['background']},
    className="container",
    children=[
        html.H1(
            children='Hello Dash',
            style={
                'textAlign': 'center',
                'color': colors['text'],
                'padding-bottom': '30'
            }
        ),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),

        # dcc.Graph(
        #     id='example-graph',
        #     figure={
        #         'data': [
        #             {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
        #             {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
        #         ],
        #         'layout': {
        #             'title': 'Dash Data Visualization'
        #         }
        #     }
        # )
        html.Div([html.Span("Metric to display : ", className="six columns",
                                           style={"text-align": "right", "width": "40%", "padding-top": 10}),
                                 dcc.Dropdown(id="value-selected", value='Confirmed',
                                              options=[{'label': "Confirmed ", 'value': 'Confirmed'},
                                                       {'label': "Recovered ", 'value': 'Recovered'},
                                                       {'label': "Deaths ", 'value': 'Deaths'},
                                                       {'label': "Active ", 'value': 'Active'}],
                                              style={"display": "block", "margin-left": "auto", "margin-right": "auto",
                                                     "width": "70%"},
                                              className="six columns")], className="row"),
        html.Div([html.Span("Dates Range : ", className="six columns",
                                           style={"text-align": "right", "width": "40%", "padding-top": 10}),
                                 dcc.Input(id="start-date",value="2019-12-15", type='text'),
                                 dcc.Input(id="end-date",value="2020-01-01", type='text')
                                 ], className="row"),
        html.Br(),
        html.Br(),
        html.Div(id='my-output'),
        dcc.Graph(id="my-graph"),
        dcc.Graph(id="earthquake-graph"),
    ]
)

def prepare_daily_report():
    current_date = (datetime.today() - timedelta(days=1)).strftime('%m-%d-%Y')
    df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/' + current_date + '.csv')

    df_country = df.groupby(['Country_Region']).sum().reset_index()
    df_country.replace('US', 'United States', inplace=True)
    df_country.replace(0, 1, inplace=True)

    code_df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv')
    df_country_code = df_country.merge(code_df, left_on='Country_Region', right_on='COUNTRY', how='left')

    df_country_code.loc[df_country_code.Country_Region == 'Congo (Kinshasa)', 'CODE'] = 'COD'
    df_country_code.loc[df_country_code.Country_Region == 'Congo (Brazzaville)', 'CODE'] = 'COG'
    
    return(df_country_code)

@app.callback(
    dash.dependencies.Output("my-graph", "figure"),
    [dash.dependencies.Input("value-selected", "value")]
)
def update_figure(selected):
    dff = prepare_daily_report()
    dff['hover_text'] = dff["Country_Region"] + ": " + dff[selected].apply(str)

    trace = go.Choropleth(locations=dff['CODE'],z=np.log(dff[selected]),
                          text=dff['hover_text'],
                          hoverinfo="text",
                          marker_line_color='white',
                          autocolorscale=False,
                          reversescale=True,
                          colorscale="RdBu",marker={'line': {'color': 'rgb(180,180,180)','width': 0.5}},
                          colorbar={"thickness": 10,"len": 0.3,"x": 0.9,"y": 0.7,
                                    'title': {"text": 'persons', "side": "bottom"},
                                    'tickvals': [ 2, 10],
                                    'ticktext': ['100', '100,000']})   
    return {"data": [trace],
            "layout": go.Layout(height=800,geo={'showframe': False,'showcoastlines': False,
                                                                      'projection': {'type': "miller"}})}

earthquakeData = pd.read_csv("http://ftp.maps.canada.ca/pub/nrcan_rncan/Earthquakes_Tremblement-de-terre/canadian-earthquakes_tremblements-de-terre-canadien/eqarchive-en.csv",
                   dtype={"latitude": float, "longitude": float})
earthquakeData = earthquakeData.dropna(subset=['date'])
earthquakeData = earthquakeData.where(earthquakeData['date'] >= "2019-01-01")

@app.callback(
    dash.dependencies.Output(component_id='my-output', component_property='children'),
    [dash.dependencies.Input(component_id='start-date', component_property='value'), dash.dependencies.Input(component_id='end-date', component_property='value')]
)
def update_output_div(start_date, end_date):
    return 'Output: {} {}'.format(start_date, end_date)

@app.callback(
    dash.dependencies.Output("earthquake-graph", "figure"),
    [dash.dependencies.Input(component_id='start-date', component_property='value'), dash.dependencies.Input(component_id='end-date', component_property='value')]
)
def update_country(start_date, end_date):

    data = earthquakeData.where(earthquakeData['date'] >= start_date)
    data = data.where(earthquakeData['date'] < end_date)

    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
        locationmode = 'USA-states',
        lon = data['longitude'],
        lat = data['latitude'],
        hoverinfo = 'text',
        text = data['place'],
        mode = 'markers',
        marker = dict(
            size = 2,
            color = 'rgb(255, 0, 0)',
            line = dict(
                width = 3,
                color = 'rgba(68, 68, 68, 0)'
            )
        )))
    
    return fig  #{"data": [trace],
                #"layout": go.Layout(height=800,geo={'showframe': False,'showcoastlines': False,
                #                                                          'projection': {'type': "miller"}})}

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
