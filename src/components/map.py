from dash import Dash, html, dcc, callback, Output, Input, dash_table
import pandas as pd
from urllib.request import urlopen
import json
import plotly.express as px
import dash_bootstrap_components as dbc

# Example data
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                   dtype={"fips": str})


map_layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Row(
                        html.Div([
                            html.H4('Political candidate voting pool analysis'),
                            html.P("Select a candidate:"),
                            dcc.RadioItems(
                                id='candidate',
                                options=["Joly", "Coderre", "Bergeron"],
                                value="Coderre",
                                inline=True
                            ),
                            dcc.Graph(id="graph"),
                        ]),
                        style={"width": "400px", "margin-left": 0},
                    ),
                ),
                dbc.Col(
                    dbc.Row(
                        html.Div([
                            html.H4('Political candidate voting pool analysis')
                        ]),
                        style={"width": "400px", "margin-left": 0},
                    ),
                ),
            ],
            justify="center",
        ),
    ],
),




"""map_layout = html.Div([
        html.H4('Political candidate voting pool analysis'),
        html.P("Select a candidate:"),
        dcc.RadioItems(
            id='candidate',
            options=["Joly", "Coderre", "Bergeron"],
            value="Coderre",
            inline=True
        ),
        dcc.Graph(id="graph"),
    ])"""



# -------------------------------------------------------------
# Callbacks to update the map depending on chosen attribute
# -------------------------------------------------------------
@callback(
    Output("graph", "figure"),
    Input("candidate", "value"))
def display_choropleth(candidate):
    df = px.data.election() # replace with your own data source
    geojson = px.data.election_geojson()
    fig = px.choropleth(
        df, geojson=geojson, color=candidate,
        locations="district", featureidkey="properties.district",
        projection="mercator", range_color=[0, 6500])
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig