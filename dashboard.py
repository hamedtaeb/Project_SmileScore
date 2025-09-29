# Import necessary libraries
import re
import os
import random
import sklearn
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.express as px
from scipy import stats as st
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc

# Load dataset
df = pd.read_csv('dataset/dataset.csv')

app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY]) 

# Add Navbar
navbar = dbc.NavbarSimple(
    brand="Global Happiness Dashboard",
    color="primary",
    dark=True,
    className="mb-4"
)

# App layout
app.layout = dbc.Container([
    navbar,

    # Introduction Card
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    html.H1(
                        "Welcome to Global Happiness Dashboard!",
                        className="text-center mt-4",
                        style={"color": "#20c997"}
                    )
                ),
                dbc.CardBody([
                    html.P(
                        "This dashboard is all about exploring what makes people happy around the world. "
                        "We look at things like income, social support, and health to see how they shape happiness. "
                        "With data, machine learning, and interactive charts, you can dive in, play with the numbers, "
                        "and discover the patterns that tell the story of global well-being.",
                        className="card-text fs-5", 
                        style={"text-align": "justify", "color": "#212529"},
                    )
                ])
            ])
        ], id="title-card", width=12),
    ]), 

    # Dropdown for country selection
    dbc.Row([
        dbc.Col([
            html.Label("Select Country:", 
                       className="fs-5", 
                       style={"color": "#212529"}),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in df['country'].unique()],
                value='United States',
                clearable=False,
                style={"width": "100%"}
            )
        ], width=4)
    ], className="mb-4"),

    # Graphs
    dbc.Row([
        dbc.Col([dcc.Graph(id='happiness-score-graph')], width=6),
        dbc.Col([dcc.Graph(id='income-vs-happiness-graph')], width=6)
    ]),
], fluid=True,
   style={"backgroundColor": "#e6f5f3", "minHeight": "100vh", "padding": "20px"}  # <-- add this
)


# Callbacks for interactivity
@app.callback(
    Output('happiness-score-graph', 'figure'),
    Input('country-dropdown', 'value')
)
def update_happiness_score_graph(selected_country):
    filtered_df = df[df['country'] == selected_country]
    fig = px.line(filtered_df, x='year', y='happiness_score', 
                  title=f'Happiness Score Over Years in {selected_country}',
                  labels={'happiness_score': 'Happiness Score', 'year': 'Year'})
    fig.update_traces(mode='markers+lines')
    return fig

@app.callback(
    Output('income-vs-happiness-graph', 'figure'),
    Input('country-dropdown', 'value')
)
def update_income_vs_happiness_graph(selected_country):
    filtered_df = df[df['country'] == selected_country]
    fig = px.scatter(filtered_df, x='gdp_per_capita', y='happiness_score', 
                     title=f'Income vs Happiness Score in {selected_country}',
                     labels={'gdp_per_capita': 'GDP per Capita', 'happiness_score': 'Happiness Score'},
                     trendline='ols')
    fig.update_traces(mode='markers')
    return fig

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=7124)