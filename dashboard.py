# Import necessary libraries
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import warnings
warnings.filterwarnings('ignore')

# Load dataset
df = pd.read_csv('dataset/dataset.csv')

# Convert 'year' to integer
df['year'] = df['year'].astype(int)

# Get latest year
latest_year = df['year'].max()

# Top 10 happiest countries
top_10 = df[df['year'] == latest_year].nlargest(10, 'happiness_score')
fig_top_10 = px.bar(
    top_10,
    x='happiness_score',
    y='country',
    orientation='h',
    title=f'Top 10 Happiest Countries in {latest_year}',
    color='country',
    labels={'happiness_score': 'Happiness Score', 'country': 'Country'},
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_top_10.update_yaxes(categoryorder='total ascending')

# Bottom 10 happiest countries
bottom_10 = df[df['year'] == latest_year].nsmallest(10, 'happiness_score')
fig_bottom_10 = px.bar(
    bottom_10,
    x='happiness_score',
    y='country',
    orientation='h',
    title=f'Bottom 10 Happiest Countries in {latest_year}',
    color='country',
    labels={'happiness_score': 'Happiness Score', 'country': 'Country'},
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_bottom_10.update_yaxes(categoryorder='total descending')

# Initialize Dash app with Minty theme
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY])

# Navbar
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
        ], width=12)
    ], className="mb-4"),

    # Single-country dropdown
    dbc.Row([
        dbc.Col([
            html.Label("Select Country for Individual Analysis:",
                       className="fs-5",
                       style={"color": "#212529", "textAlign": "center", "marginBottom": "10px"}),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in df['country'].unique()],
                value='United States',
                clearable=False,
                style={"width": "100%"}
            )
        ], width=4)
    ], className="mb-4"),

    # Single-country graphs
    dbc.Row([
        dbc.Col([dcc.Graph(id='happiness-score-graph')], width=12),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([dcc.Graph(id='income-vs-happiness-graph')], width=12),
    ], className="mb-4"),

    # Top 10 and Bottom 10 charts
    dbc.Row([
        dbc.Col([dcc.Graph(figure=fig_top_10, id='top-10-happiest-countries')], width=6),
        dbc.Col([dcc.Graph(figure=fig_bottom_10, id='bottom-10-happiest-countries')], width=6)
    ], className="mb-4"),

    # Multi-country + year-range selection
    dbc.Row([
        dbc.Col([
            html.H2("🕰️ Explore Happiness Trends Over Time",
                    style={"marginTop": "30px", "color": "#1c1c2e"}, className="text-center"),
            html.P("Select countries and years to see how happiness scores evolve.",
                   id='era-subtitle',
                   style={"marginBottom": "10px", "color": "#1c1c2e"}),

            # Year range slider
            dcc.RangeSlider(
                id='year-slider',
                min=df['year'].min(),
                max=df['year'].max(),
                step=1,
                marks={str(year): str(year) for year in range(df['year'].min(), df['year'].max()+1)},
                value=[df['year'].min(), df['year'].max()],
            ),

            # Multi-country dropdown
            dcc.Dropdown(
                id='multi-countries-dropdown',
                options=[{'label': c, 'value': c} for c in df['country'].unique()],
                value=['United States'],
                multi=True,
                style={"marginTop": "20px", "marginBottom": "20px", "width": "100%"}
            ),

            # Multi-country graph
            html.H3(
                'Happiness Score by Country',
                className='text-center',
                style={"color": "#1c1c2e", "marginTop": "20px"}
            ),
            dcc.Graph(id='happiness-trends-graph')
        ], width=12)
    ])
],
    fluid=True,
    style={"backgroundColor": "#e6f5f3", "minHeight": "100vh", "padding": "20px"}
)

# Callbacks for single-country graphs
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
    fig.update_layout(template="plotly_white")
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
    fig.update_layout(template="plotly_white")
    return fig

# Callback for multi-country + year-range graph
@app.callback(
    Output('happiness-trends-graph', 'figure'),
    Input('multi-countries-dropdown', 'value'),
    Input('year-slider', 'value')
)
def update_happiness_trends(selected_countries, selected_years):
    filtered_df = df[
        (df['country'].isin(selected_countries)) &
        (df['year'] >= selected_years[0]) &
        (df['year'] <= selected_years[1])
    ]
    if filtered_df.empty:
        return {}
    fig = px.line(filtered_df, x='year', y='happiness_score', color='country',
                  markers=True,
                  labels={'happiness_score': 'Happiness Score', 'year': 'Year'})
    fig.update_layout(template="plotly_white", title="Happiness Score Trends")
    return fig

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=7124)
