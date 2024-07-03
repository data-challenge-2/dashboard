import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, State, dcc, Dash
import dash
import plotly.express as px
import os
from pathlib import Path
import pandas as pd

from .scripts.map_categories import map_categories_dict
from .scripts.geo_borough import import_geo_borough_data

data_directory = os.path.join(Path(os.getcwd()).parent.parent, "data")

# Import all data
geo_data, _ = import_geo_borough_data(data_directory, "geo_boroughs.geojson")
df_pas_original = pd.read_csv(os.path.join(data_directory, "pas_original.csv"))
df_pas_questions = pd.read_csv(os.path.join(data_directory, "pas_proportions.csv"))

df_outcomes = pd.read_csv(os.path.join(data_directory, "outcomes_pivot.csv")).drop(
    columns="Unnamed: 0"
)
df_age_rage = pd.read_csv(os.path.join(data_directory, "age_range.csv")).drop(
    columns="Unnamed: 0"
)
df_officer_def_ethnicity = pd.read_csv(
    os.path.join(data_directory, "officer_def_ethnicity.csv")
).drop(columns="Unnamed: 0")
df_legislation = pd.read_csv(os.path.join(data_directory, "legislation.csv")).drop(
    columns="Unnamed: 0"
)
df_search_object = pd.read_csv(os.path.join(data_directory, "search_object.csv")).drop(
    columns="Unnamed: 0"
)
df_ss_outcome = pd.read_csv(os.path.join(data_directory, "ss_outcome.csv")).drop(
    columns="Unnamed: 0"
)
df_crime_type = pd.read_csv(os.path.join(data_directory, "crime_type.csv")).drop(
    columns="Unnamed: 0"
)
df_last_outcome = pd.read_csv(os.path.join(data_directory, "ss_last_outcome.csv")).drop(
    columns="Unnamed: 0"
)
df_economic = pd.read_csv(os.path.join(data_directory, "economic.csv"))
df_ethnicity = pd.read_csv(os.path.join(data_directory, "ethnicity.csv"))
df_pas_agg = pd.read_csv(os.path.join(data_directory, "pas_original_aggregated.csv"))
df_ss_agg = pd.read_csv(os.path.join(data_directory, "stop_search_aggregated.csv"))
df_street_agg = pd.read_csv(os.path.join(data_directory, "street_aggregated.csv"))


def create_nested_dropdown(map_categories_dict: dict, key_path: list):
    successor = get_nested_value(map_categories_dict, key_path)
    successor_keys = None
    if isinstance(successor, dict):
        successor_keys = successor.keys()
    elif isinstance(successor, list):
        successor_keys = successor.copy()
    if successor_keys is None:
        return None

    new_dropdown_children = []
    for successor_key in successor_keys:
        successor_key_path = key_path.copy()
        successor_key_path.append(successor_key)
        children = create_nested_dropdown(map_categories_dict, successor_key_path)

        if children is None:
            ID, key = successor_key
            new_dropdown_children.append(
                html.Div(f"→ {key}", id=ID, className="menu-level2")
            )
        else:
            children = [
                html.Span(
                    f"▶ {successor_key}",
                    className="menu-level1-title",
                    id=successor_key,
                ),
                html.Div(children, className="menu-level1-content"),
            ]
            new_dropdown_children.append(
                html.Div(
                    id=f"{successor_key}_menu",
                    children=children,
                    className="menu-level1",
                )
            )
    return new_dropdown_children


def get_nested_value(d, key_path: list):
    if key_path is None:
        return None
    for key in key_path:
        if isinstance(d, dict):
            d = d.get(key)
        else:
            return None
    return d


def main_dropdowns(map_categories_dict: dict, key: str):
    x = [
        html.Span(key, className="menu-level0-title", id=key),
        html.Div(
            create_nested_dropdown(map_categories_dict, [key]),
            className="menu-level0-content",
        ),
    ]
    return dbc.Col(
        html.Div(id=f"{key}_menu", children=x, className="menu-level0"),
        style={"margin-right": "45px"},
    )


def find_button_attribute(attributes: tuple, button_id: str):
    sub_attribute = '"Good Job" local'
    for i, attribute in attributes:
        if i == button_id:
            sub_attribute = attribute
    return sub_attribute


map_tabs_layout = [
    main_dropdowns(map_categories_dict, key) for key in map_categories_dict
]
choropleth_map_layout = dcc.Graph(id="choropleth-map")

button_to_borough = {
    str(i): borough for i, borough in enumerate(df_pas_original["Borough"].unique())
}


@dash.callback(
    Output("choropleth-map", "figure"),
    Output("previously-clicked-attribute-store", "data"),
    Output("agg-flag-store", "data"),
    Output("shared-data-store", "data"),
    Output("shared-data-store-lg", "data"),
    Output("attribute-tt", "data"),  # so the tooltip knows which attribute is selected
    Output("attribute", "data"),
    [Input(str(i), "n_clicks") for i in range(153)] +
    [Input(f"{i}", "n_clicks") for i in ["PAS", "Confidence", "Trust", "Stop&Search", "StreetCrime", "CrimeOutcomes"]] +
    [Input("range-slider", "value")],
    State("previously-clicked-attribute-store", "data"),
    State("agg-flag-store", "data"),
    State("df-data-store", "data"),
    Input('attribute', 'data'),
    Input('attribute-tt', 'data'),
)
def update_map(*args):
    ctx = dash.callback_context

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    attribute_clicks = args[:153]
    aggregated_clicks = args[153:159]
    year_range = args[159]
    previously_clicked_attribute = args[160]
    agg_flag = args[161]
    # df_data = args[162]

    df_data = pd.DataFrame()
    df_data_lg = pd.DataFrame()

    attribute = args[163]
    sub_attribute = args[164]

    if button_id.isdigit():

        # Find out what attribute should be displayed in plot depending on IDs of type str(int).
        if button_id is None:
            df_data = df_pas_original.copy()
            sub_attribute = (
                '"Good Job" local'  # Default to Trust_score if no button is clicked
            )

        # PAS
        elif 0 <= int(button_id) <= 37:
            df_data = df_pas_original.copy()
            if 0 <= int(button_id) <= 4:
                attributes = map_categories_dict["PAS"]["Confidence"]
                sub_attribute = find_button_attribute(attributes, button_id)
                attribute = "PAS-Confidence"
            elif 5 <= int(button_id) <= 7:
                attributes = map_categories_dict["PAS"]["Trust"]
                sub_attribute = find_button_attribute(attributes, button_id)
                attribute = "PAS-Trust"
            elif 8 <= int(button_id) <= 9:
                attributes = map_categories_dict["PAS"]["Other"]
                sub_attribute = find_button_attribute(attributes, button_id)
                attribute = "PAS-Other"
            elif 10 <= int(button_id) <= 37:
                pas_granular_bool = True
                df_data = df_pas_questions.copy()
                attributes = map_categories_dict["PAS"]["PAS-Granular"]
                sub_attribute = find_button_attribute(attributes, button_id)
                attribute = "PAS-Granular"

        # Economic and Ethnicity
        elif 38 <= int(button_id) <= 55:
            if 38 <= int(button_id) <= 42:
                df_data = df_ethnicity.copy()
                attributes = map_categories_dict["Economic"]["Demographic"]
                sub_attribute = find_button_attribute(attributes, button_id)
                attribute = "Economic-Demographic"
            elif 43 <= int(button_id) <= 49:
                df_data = df_economic.copy()
                attributes = map_categories_dict["Economic"]["Industry types"]
                sub_attribute = find_button_attribute(attributes, button_id)
                attribute = "Economic-Industry"
            elif 50 <= int(button_id) <= 55:
                df_data = df_economic.copy()
                attributes = map_categories_dict["Economic"]["Employment"]
                sub_attribute = find_button_attribute(attributes, button_id)
                attribute = "Economic-Employment"

        # Stop&Search
        elif 56 <= int(button_id) <= 92:
            if 56 <= int(button_id) <= 60:
                df_data = df_age_rage.copy()
                attributes = map_categories_dict["Stop&Search"]["Age Range"]
                sub_attribute = find_button_attribute(attributes, button_id)
                attribute = "SS-Age"
            elif 61 <= int(button_id) <= 64:
                df_data = df_officer_def_ethnicity.copy()
                attributes = map_categories_dict["Stop&Search"][
                    "Officer Defined Ethnicity"
                ]
                sub_attribute = find_button_attribute(attributes, button_id)
                attribute = "SS-Ethnicity"
            elif 65 <= int(button_id) <= 69:
                df_data = df_legislation.copy()
                attributes = map_categories_dict["Stop&Search"]["Legislation"]
                sub_attribute = find_button_attribute(attributes, button_id)
                attribute = "SS-Legislation"
            elif 70 <= int(button_id) <= 77:
                df_data = df_search_object.copy()
                attributes = map_categories_dict["Stop&Search"]["Search Object"]
                sub_attribute = find_button_attribute(attributes, button_id)
                attribute = "SS-Object"
            elif 78 <= int(button_id) <= 92:
                df_data = df_ss_outcome.copy()
                attributes = map_categories_dict["Stop&Search"][
                    "Stop and Search Outcome"
                ]
                sub_attribute = find_button_attribute(attributes, button_id)
                attribute = "SS-Outcome"

        # StreetCrime
        elif 93 <= int(button_id) <= 130:
            if 93 <= int(button_id) <= 106:
                df_data = df_crime_type.copy()
                attributes = map_categories_dict["StreetCrime"]["Crime Type Street"]
                sub_attribute = find_button_attribute(attributes, button_id)
                attribute = "SC-Street"
            elif 107 <= int(button_id) <= 130:
                df_data = df_last_outcome.copy()
                attributes = map_categories_dict["StreetCrime"]["Last Outcome"]
                sub_attribute = find_button_attribute(attributes, button_id)
                attribute = "SC-Outcome"

        # Outcomes
        elif 131 <= int(button_id) <= 152:
            df_data = df_outcomes.copy()
            attributes = map_categories_dict["CrimeOutcomes"]
            sub_attribute = find_button_attribute(attributes, button_id)
            attribute = "CrimeOutcomes"
        else:
            sub_attribute = None

    else:
        if button_id == "PAS":
            df_data = df_pas_agg.copy()
            sub_attribute = "PAS"
            attribute = "PAS"
        elif button_id == "Confidence":
            df_data = df_pas_agg.copy()
            sub_attribute = "Confidence"
            attribute = "Confidence"
        elif button_id == "Trust":
            df_data = df_pas_agg.copy()
            sub_attribute = "Trust"
            attribute = "Trust"

        elif button_id == "Stop&Search":
            df_data = df_ss_agg.copy()
            sub_attribute = "Stop&Search"
            attribute = "SS"
        elif button_id == "StreetCrime":
            df_data = df_street_agg.copy()
            sub_attribute = "StreetCrime"
            attribute = "SC"
        elif button_id == "CrimeOutcomes":
            df_data = df_outcomes.copy()
            sub_attribute = "CrimeOutcomes"
            attribute = "CrimeOutcomes"
        else:
            sub_attribute = None

    if sub_attribute is None:
        df_data = df_pas_original.copy()
        sub_attribute = (
            '"Good Job" local'  # Default to Trust_score if no button is clicked
        )
    if attribute is None:
        attribute = "PAS-Confidence"

    df_data_lg = df_data.copy()

    start_year, end_year = year_range
    df_data = df_data[df_data["Year"].between(start_year, end_year)]

    fig = px.choropleth(
        data_frame=df_data,
        geojson=geo_data,
        locations="Borough",
        featureidkey="properties.name",
        color=sub_attribute,
        color_continuous_scale="viridis",
        projection="mercator",
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"l": 0, "b": 0, "t": 0, "r": 0}, width=800, height=600)
    fig.update_coloraxes(colorbar_len=0.5)

    return fig, button_id, agg_flag, df_data.to_dict("records"), df_data_lg.to_dict("records"), sub_attribute, attribute
