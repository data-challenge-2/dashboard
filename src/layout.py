# External imports
import dash_bootstrap_components as dbc
from dash import html, State, dcc

from components.map_tabs import map_tabs_layout, choropleth_map_layout
from components.side_nav import button, side_bar
from components.line_graph import line_graph_layout
from components.h_bar_chart import h_barchart_layout
from components.tooltip import tooltip_layout


# ====================================
# Create the layout
# ====================================

dash_layout = dbc.Container([
    html.Link(href='/assets/styles.css', rel='stylesheet'),
    dcc.Store(id='stored_data', data=[]),  # Store to hold selected boroughs
    dcc.Store(id='selected_borough', data=[]),
    dcc.Store(id='shared-data-store', data=[]),
    dcc.Store(id='shared-data-store-year', data=[]),
    dcc.Store(id='shared-data-store-lg', data=[]),  # Store for shared data
    dcc.Store(id='attribute-tt', data=''),
    dcc.Store(id='attribute', data=''),


    dcc.Store(id="previously-clicked-attribute-store", storage_type="session"),
    dcc.Store(id="agg-flag-store", storage_type="session"),
    dcc.Store(id="df-data-store", storage_type="session"),

    dbc.Row([
        dbc.Row(html.H1('Powered by the TU/e', className='top-panel')),
        dbc.Row(html.H1('𝓟oL𝛔cal', className='polocal-header', style={'margin-top': '24px'})),
        dbc.Row(dbc.Navbar([button, *map_tabs_layout], style={'margin-top': '-20px', 'padding': 0}),
                className="dbc-navbar", )
    ], className="mb-2"),
    dbc.Row([
        dbc.Col(side_bar, id='sidebar-column', width=0),
        dbc.Col([
            dbc.Row([dcc.RangeSlider(2015, 2021, 1,
                                     value=[2017, 2018],
                                     id='range-slider',
                                     marks={i: str(i) for i in range(2015, 2022, 1)},
                                     ), ], style={'padding': '5px'}),
            dbc.Row([
                dbc.Col(choropleth_map_layout, id='map-column'),
                dbc.Col(h_barchart_layout, id='h-barchart-column', className='graph-container'),
            ]),
        ]),
    ]),
    dbc.Row([
        dbc.Col(line_graph_layout),
    ]),
    dbc.Row([
        dbc.Col(tooltip_layout),
    ]),
], fluid=True, className='container')


