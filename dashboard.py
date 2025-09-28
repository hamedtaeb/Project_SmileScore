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

    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    html.H1(
                        "Welcome to Global Happiness Dashboard!",
                        className="text-center mt=4",
                        style={"color": "#20c997"}
                    )
                ),
                dbc.CardBody([
                    html.P(
                        "This dashboard is all about exploring what makes people happy around the world. " \
                        "We look at things like income, social support, and health to see how they shape happiness. " \
                        "With data, machine learning, and interactive charts, you can dive in, play with the numbers, "
                        "and discover the patterns that tell the story of global well-being.",
                        className="card-text fs-5", 
                        style={"text-align": "justify", "color": "#212529"},
                    )
                ])
            ])
        ], id="title-card", width=12)
    ])
], fluid=True)

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=7124)

