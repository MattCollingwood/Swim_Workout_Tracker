import dash
import dash_bootstrap_components as dbc
from dash import dcc, Input, Output, html, dash_table, callback
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go




# Loading Data
# Importing existing workouts
def load_data():
    data = pd.read_csv('assets/daily_swim_summary.csv') #loads the xml file
    data["date_original"] = data["date"]
    data["date"] = pd.to_datetime(data["date"])  # Convert to datetime
    data["year"] = data["date"].dt.year  # Extract year
    data["date"] = data["date"].dt.strftime("%Y-%m-%d")  # Format back to string
    
    data.set_index("date", inplace=True, drop=False)

    return data

data = load_data()

def load_aggregate_data():
    agg_data = pd.read_csv('assets/aggregated_swim_data.csv') #loads the xml file
    agg_data["date"] = agg_data["date"]
    agg_data.set_index("date", inplace=True, drop=False)

    return agg_data

agg_data = load_aggregate_data()





# Create the Web Application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

# App Layout and Design
app.layout = dbc.Container([
    #Title and Intro
    dbc.Row([
        dbc.Col(html.H1("Swim Workout Tracker"), width=15, className="text-center my-5")
    ]),
    dbc.Row([
        dbc.Col(html.H3("A data-driven swim training analytics platform that seamlessly syncs workout data from my Apple Watch and delivers real-time performance insights through an interactive Python dashboard."), width=200, className="text-center my-5")
    ]),
    # Yardage Tracker
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("📈Yardage Overview", className="card-title"),
                    dcc.Graph(figure=px.line(x="date", y="total_distance", data_frame=data, labels={
                        "date": "Workout Date",
                        "total_distance": "Total Distance (yards)"
                    }))
                ])
            ])
        ], width=12)
    ]),

    # Recent Workouts
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("🏊‍♂️Recent Workouts", className="card-title"),
                    html.Div([
                        dash_table.DataTable(
                            id="recent_workouts",
                            columns=[
                                {"name": "Date", "id": "date", "deletable": False, "selectable": True, "hideable": True},
                                {"name": "Total Distance", "id": "total_distance", "deletable": False, "selectable": True, "hideable": True, "type": "numeric", "format":{"specifier": ",.0f"}},
                                {"name": "Max Heart Rate", "id": "max_heart_rate", "deletable": False, "selectable": True, "hideable": True},
                                {"name": "Number of Lengths", "id": "num_lengths", "deletable": False, "selectable": True, "hideable": True},
                                {"name": "Stroke Type", "id": "swim_stroke", "deletable": False, "selectable": True, "hideable": True},
                                {"name": "Distance (Miles)", "id": "total_distance_miles", "deletable": False, "selectable": True, "hideable": True, "type": "numeric", "format": {"specifier": ".2f"}},
                                {"name": "Time (Minutes)", "id": "total_time_minutes", "deletable": False, "selectable": True, "hideable": True, "type": "numeric", "format": {"specifier": ".0f"}},
                            ] + [
                                {"name": i, "id": i, "deletable": True, "selectable": False}
                                for i in data.columns
                                if i not in ["date", "total_distance", "max_heart_rate", "num_lengths", "swim_stroke", "total_distance_miles", "total_time_minutes"]
                            ],
                            data=data.to_dict("records"),
                            hidden_columns=["message_index","event","event_type","start_time","total_elapsed_time","total_cycles","avg_heart_rate","avg_cadence","max_cadence","lap_trigger","first_length_index","avg_stroke_distance","sport","min_heart_rate","enhanced_avg_speed","time","Unnamed: 0", "workout_id", "backstroke", "butterfly", "breaststroke",'freestyle', "im", "mixed", "year"],
                            sort_action="native",
                            selected_columns=[],
                            selected_rows = [],
                            page_size = 5,
                            style_cell={"maxWidth": "12px"},
                            css=[{"selector": ".show-hide", "rule": "display: none"}]
                        )
                    ])
                ])
            ])
        ], width=12)
    ]),



    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("📅Select a Workout", className="card-title"),
                    dcc.Dropdown(
                        id="workout_filter",
                        options=[{"label": date, "value": date} for date in data["date"].unique()],
                        value=None,
                        placeholder="Select a Workout"
                    ),
                    html.H6("🔆Date", className="workout-subtitle"),
                    html.H5(id="workout_date", className="workout-dataline"), # filters the h5 tag by the date selected in the drop down
                    html.H6("📈Yardage", className="workout-subtitle"),
                    html.H5(id="workout_yardage", className="workout-dataline"), # filters the h5 tag value by the sum of the yardage based on the date selected in the drop down
                    html.H6("⏱Duration", className="workout-subtitle"),
                    html.H5(id="workout_duration", className="workout-dataline") # filters the h5 tag value by the sum of the total time based on the date selected in the drop down
                ], className="workout-card")
            ])
        ], width=6),

        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("📊Strokes", className="card-title"),
                    dcc.Graph(id="swim_strokes")
                ])
            ])
        ], width=6)
    ]),

    # Yearly Totals
    html.Div([
        dbc.Row([
            dbc.Col([
                html.H4("🧮Yearly Totals", className="yearly-title")
            ], width=12, className="mb-3", align="center")
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id="year_filter",
                    options=[{"label": "All Years", "value": "all"}] + 
                            [{"label": str(year), "value": year} for year in sorted(data["year"].unique())],
                    value="all",
                    placeholder="Select a year"
                )
            ], width=4, className="mb-3", align="center")     
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Workouts", className="yearly-subtitle"),
                        html.H5(str(len(data)), id="yearly_workouts", className="yearly-dataline")
                    ])
                ])
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Time Spent Swimming", className="yearly-subtitle"),
                        html.H5(f"{sum(data["total_elapsed_time"]/ 3600):,.2f} hours", id="yearly_time", className="yearly-dataline")
                    ])
                ])
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Distance", className="yearly-subtitle"),
                        html.H5(f"{sum(data["total_distance"]/1650):,.2f} miles", id="yearly_distance", className="yearly-dataline")
                    ])
                ])
            ], width=4)    
        ])
    ], className="yearly-totals"),
])

# Callbacks
@callback(
    Output('recent_workouts', "style_data_conditional"),
    Input("recent_workouts", 'selected_columns')
)
def update_table_style(selected_columns):
    return [{
        "if": { "column_id": i },
        'background_color': '#D2F3FF',
        "font-family": "sans-serif"
    } for i in selected_columns]

@callback( 
    Output('workout_date', "children"),
    Output('workout_yardage', "children"),
    Output('workout_duration', "children"), 
    Input('workout_filter', 'value')
)
def update_workout_filter(selected_date):
    if selected_date is None:
        return "Select a workout for details", "Select a workout for details", "Select a workout for details"

    #Filter data by selected date
    filtered_df = data[data["date"] == selected_date] 

    # Calculate values
    date_display = selected_date
    total_yardage = filtered_df["total_distance"].sum()
    total_duration = filtered_df["total_time_minutes"].sum()
    
    return date_display, f"{(total_yardage):,.0f} yards", f"{(total_duration):,.0f} minutes"


@callback(
    Output("swim_strokes", "figure"),
    Input("workout_filter", "value")
)

def update_swim_pie(selected_date):
    # Filter data based on selection
    if selected_date is None:
        filtered_df = agg_data.copy()
        title = "Overall Swim Stroke Breakdown"
    else:
        try:
            date_obj = pd.to_datetime(selected_date)
            formatted_date = date_obj.strftime("%m/%d/%Y")
        except:
            formatted_date = selected_date
        
        filtered_df = agg_data[agg_data["date"] == formatted_date]
        title = f"Swim Stroke Breakdown - {selected_date}"
        
    # Filter out rows with no stroke data
    filtered_df = filtered_df[(filtered_df["swim_stroke"].notna()) & (filtered_df["total_distance"] > 0)]
    
    # Check if any data
    if filtered_df.empty:
        fig = px.pie(
            names=["No Data"],
            values=[1],
            title=title
        )
        fig.update_traces(textinfo='none')
        return fig
    
    # Group by stroke and sum distances
    stroke_summary = filtered_df.groupby("swim_stroke")["total_distance"].sum().reset_index()
    
    # Create pie chart
    fig = px.pie(
        stroke_summary,
        names="swim_stroke",
        values="total_distance",
        title=title
    )

    return fig

@callback(
    Output("yearly_workouts", "children"),
    Output("yearly_time", "children"),
    Output("yearly_distance", "children"),
    Input("year_filter", "value")
)

def update_yearly_totals(selected_year):
    if selected_year == "all" or selected_year is None:
        filtered_df = data.copy()
    else:
        filtered_df = data[data["year"] == int(selected_year)]
    
    num_workouts = len(filtered_df)
    total_time = filtered_df["total_elapsed_time"].sum() / 3600
    total_distance = filtered_df["total_distance"].sum()/1650


    return (
        str(num_workouts),
        f"{total_time:,.2f} hours",
        f"{total_distance:,.2f} miles"
    )

# Run the App
if __name__ == "__main__":
    app.run(debug=True)