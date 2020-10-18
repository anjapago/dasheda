# Based off of example at https://community.plotly.com/t/running-dash-app-in-docker-container/16067
# https://medium.com/@megah_f/build-a-covid-19-map-with-python-and-plotly-dash-91a9fe58dfde
# https://plotly.com/python/choropleth-maps/

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import flask
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server,external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

colors = { 'background' : 'white', 'text' : 'black' }

countries = []

code_df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv')

for country in code_df['CODE']:
    countries.append({ 'label': country.lower(), 'value': country.lower()})


earthquakeData = pd.read_csv("http://ftp.maps.canada.ca/pub/nrcan_rncan/Earthquakes_Tremblement-de-terre/canadian-earthquakes_tremblements-de-terre-canadien/eqarchive-en.csv",
                   dtype={"latitude": float, "longitude": float})
earthquakeData = earthquakeData[~earthquakeData['date'].isnull()]
earthquakeData = earthquakeData[earthquakeData['date'] >= "2019-01-01"]
earthquakeData['distance'] = 0

app.layout = html.Div(
    style={'backgroundColor': colors['background']},
    className="container",
    children=[
        html.H1(
            children='EarthQuakes',
            style={
                'textAlign': 'center',
                'color': colors['text'],
                'padding-bottom': '30'
            }
        ),

        html.Div(children='''
            Dash: An App For Assessing Your Risk Of Earthquakes.
        ''',
            style={
                'textAlign': 'center',
                'color': colors['text'],
                'padding-bottom': '30'
            }),

        html.Div(children="Dates Range 2019 : ", style={"textAlign": "center", "padding-top": 10}),
                                 

        dcc.RangeSlider(
                id='my-range-slider',
                min=1,
                max=12,
                value=[1, 12],
                step=None,
                marks={
                    1: {'label': 'Jan'},
                    2: {'label': 'Feb'},
                    3: {'label': 'Mar'},
                    4: {'label': 'Apr'},
                    5: {'label': 'May'},
                    6: {'label': 'Jun'},
                    7: {'label': 'Jul'},
                    8: {'label': 'Aug'},
                    9: {'label': 'Sep'},
                    10: {'label': 'Oct'},
                    11: {'label': 'Nov'},
                    12: {'label': 'Dec'},
                },
                included=False
            ),

        html.Div([html.Span("Location: ", className="six columns",
                                           style={"text-align": "right", "width": "40%", "padding-top": 10}),
                 dcc.Input(id="location",value="Edmonton, AB, Canada", type='text', debounce=True)
                 ], className="row"),
        html.Div([html.Span("Latitude: ", className="six columns",
                                           style={"text-align": "right", "width": "40%", "padding-top": 10}),
                  dcc.Input(id="latitude",value="0", type='number')
                  ], className="row"),
        html.Div([html.Span("Longitude: ", className="six columns",
                                           style={"text-align": "right", "width": "40%", "padding-top": 10}),
                  dcc.Input(id="longitude",value="0", type='number')
                  ], className="row"),
        html.Div([html.Span("Count: ", className="six columns",
                                           style={"text-align": "right", "width": "40%", "padding-top": 10}),
                  dcc.Input(id="count",value="10", type='number')
                  ], className="row"),

        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in earthquakeData.columns],
            data = earthquakeData.head(n = 0).to_dict('records'),
        ),

        dcc.Graph(id="earthquake-graph"),
    ]
)

geolocator = Nominatim(scheme='http', user_agent="android_application")

location_dict = {}

# We have been having trouble with the geolocator library
# It works in a jupyter notebook but only sometimes works in this image
# To make the demo work, we have circumvented the library temporarily
backup_dict = { "Edmonton, AB, Canada": (53.535411, -113.507996) }

def get_location(location):
    if not location in location_dict:
        try:
            loc = geolocator.geocode(location)
            location_dict[location] = (loc.latitude, loc.longitude)
        except:
            try:
                location_dict[location] = backup_dict[location]
            except:
                location_dict[location] = (53.535411, -113.507996)

    return location_dict[location]

@app.callback(
    [dash.dependencies.Output(component_id='latitude', component_property='value'),
     dash.dependencies.Output(component_id='longitude', component_property='value')],
    [dash.dependencies.Input(component_id='location', component_property='value')]
)
def update_lat_long(location):
    latitude, longitude = get_location(location)
    return (latitude, longitude)

@app.callback(
    dash.dependencies.Output("table", "data"),
    [dash.dependencies.Input(component_id='my-range-slider', component_property='value'),
     dash.dependencies.Input(component_id='latitude', component_property='value'),
     dash.dependencies.Input(component_id='longitude', component_property='value'),
     dash.dependencies.Input(component_id='count', component_property='value')]
)
def update_table(rng, latitude, longitude, count):

    start_date, end_date = range_to_dates(rng)

    latitude = float(latitude)
    longitude = float(longitude)

    count = int(count)
    if count > 20:
        count = 20
    
    data = earthquakeData[earthquakeData['date'] >= start_date]
    data = data[earthquakeData['date'] <= end_date]
    
    dist_func = lambda x : geodesic((x[0], x[1]) ,(latitude, longitude)).kilometers

    data['distance'] = data[['latitude', 'longitude']].apply(dist_func, axis=1) # (((data['latitude'] - latitude) ** 2) + ((data['longitude'] - longitude) ** 2)).apply(math.sqrt)
    data.sort_values("distance", inplace = True)
    return data.head(count).to_dict('records')

@app.callback(
    dash.dependencies.Output("earthquake-graph", "figure"),
    [dash.dependencies.Input(component_id='my-range-slider', component_property='value')]
)
def update_map(rng):

    start_date, end_date = range_to_dates(rng)

    data = earthquakeData[earthquakeData['date'] >= start_date]
    data = data[earthquakeData['date'] < end_date]

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
    
    return fig

def range_to_dates(rng):
    if rng[0] < 10:
        rng[0] = "0" + str(rng[0])
    else:
        rng[0] = str(rng[0])

    if rng[1] < 10:
        rng[1] = "0" + str(rng[1])
    else:
        rng[1] = str(rng[1])

    return ('2019-{}-01'.format(rng[0]), '2019-{}-01'.format(rng[1]))

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
