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

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY]) 

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    html.H5(
                        "Welcome to Global Happiness Dashboard!",
                        className="card-title text-center",
                        style={"color": "#2dd4bf"}
                    )
                ),
                dbc.CardBody([
                    html.P(
                        "Explore global happiness trends based on factors like GDP, social support, and life expectancy.",
                        className="card-text text-center"
                    )
                ])
            ])
        ], id="title-card", width=12)
    ])
], fluid=True)

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=7124)

