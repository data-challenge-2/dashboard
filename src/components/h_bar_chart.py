# # Imports
# from dash import dcc, Input, Output, callback
# import pandas as pd
# import plotly.express as px
# import os
# import dash_bootstrap_components as dbc
# from pathlib import Path
# import dash_bootstrap_components as dbc
# from dash import html, callback, Input, Output, State, callback_context, dcc
# import plotly.express as px
# #from .scripts.import_data import df_data, geo_data4
# from dash.exceptions import PreventUpdate
#
# h_barchart_layout = dcc.Graph(id="h_barchart")
#
# data_directory = os.path.join(Path(os.getcwd()).parent.parent, 'data')
# df_granular_pas = pd.read_csv(os.path.join(data_directory, 'pas_data_ward_level/PAS_ward_level_FY_20_21.csv'))
# df_grouped = df_granular_pas.groupby(['Borough', 'Q1']).size().unstack().fillna(0)
#

import dash.dependencies as dd
from dash import html, callback, Input, Output, State, callback_context, dcc
import plotly.express as px
import pandas as pd
import os
from pathlib import Path
import plotly.graph_objects as go


# from .scripts.import_data import df_pas_granular as df_granular_pas

data_directory = os.path.join(Path(os.getcwd()).parent.parent, "data")
df_granular_pas = pd.read_csv(os.path.join(data_directory, "pas_granular.csv"))

h_barchart_layout = dcc.Graph(id="h_barchart")


df_grouped = (
    df_granular_pas.groupby(["Borough", "Ss Agree Neither Agree Nor Disagree"])
    .size()
    .unstack()
    .fillna(0)
)

from dash import callback, Output, Input, State
import plotly.express as px
import plotly.colors


@callback(
    Output("h_barchart", "figure"),
    Input("shared-data-store", "data"),
    Input("selected_borough", "data"),
    Input("attribute-tt", "data"),
    State("h_barchart", "figure"),
    prevent_initial_call=True,
)
def update_h_barchart(data, selected_borough, attribute, current_figure):
    if data is None or not data:
        return current_figure

    df_filtered = pd.DataFrame(data)

    # print(df_filtered.columns)
    # Sum the counts for each borough across all unique variables
    # df_filtered['Count'] = df_filtered.drop(columns=['Borough']).sum(axis=1)
    # df_filtered = df_filtered[['Borough', 'Count']]
    # df_filtered = df_filtered.groupby('Borough', 'Year')
    # print(df_filtered.columns)

    # Initialize colors
    default_color = "#00008B"  # Color for unselected boroughs
    selected_color = "#50C878"  # Green color for selected boroughs

    # Determine color scheme based on selection
    if selected_borough:
        df_filtered["selected"] = df_filtered["Borough"].apply(
            lambda x: x in selected_borough
        )
        df_filtered = df_filtered.sort_values(
            by=["selected", attribute], ascending=[False, False]
        )

        print(df_filtered["Borough"].unique())
        print(selected_borough)
        print(df_filtered["selected"].nunique())

        # Create the bar chart with selected boroughs colored and others default
        fig = go.Figure()

        for index, row in df_filtered.iterrows():
            color = selected_color if row["selected"] else default_color
            print("barchartcolor", color)
            fig.add_trace(
                go.Bar(
                    y=[row["Borough"]],
                    x=[row[attribute]],
                    name=row["Borough"],
                    orientation="h",
                    marker=dict(color=color),
                )
            )
    else:
        # No borough selected, all boroughs get the default color
        df_filtered = df_filtered.sort_values(by=attribute, ascending=False)
        fig = px.bar(
            df_filtered,
            y="Borough",
            x=attribute,
            orientation="h",
            color_discrete_sequence=[default_color],
        )

    fig.update_layout(
        barmode="stack",
        title="",
        xaxis_title="Count",
        yaxis_title="Borough",
        yaxis={"categoryorder": "total ascending"},
        margin={"l": 100, "b": 50, "t": 50, "r": 0},
        width=700,
        height=600,
        showlegend=False,  # Turn off the legend
        plot_bgcolor="rgba(0, 0, 0, 0)",  # Make the plot background transparent
        paper_bgcolor="rgba(0, 0, 0, 0)",  # Make the paper background transparent
    )
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    return fig


@callback(
    Output("selected_borough", "data"),
    [Input("choropleth-map", "clickData"), Input("h_barchart", "clickData")],
    State("selected_borough", "data"),
    prevent_initial_call=True,
)
def update_selected_borough(map_click_data, bar_click_data, selected_borough):
    if selected_borough is None:
        selected_borough = []

    ctx = callback_context
    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"]
        if prop_id == "choropleth-map.clickData" and map_click_data:
            clicked_borough = map_click_data["points"][0]["location"]
        elif prop_id == "h_barchart.clickData" and bar_click_data:
            clicked_borough = bar_click_data["points"][0]["y"]
        else:
            clicked_borough = None

        if clicked_borough:
            if clicked_borough in selected_borough:
                selected_borough.remove(clicked_borough)
            else:
                selected_borough.append(clicked_borough)

    return selected_borough
