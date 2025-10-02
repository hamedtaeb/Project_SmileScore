# Import necessary libraries
import os
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
server = app.server

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



        # Year selector (single year)
    dbc.Row([
        dbc.Col([
            html.Label("Select Year:", className="fs-5", style={"color": "#212529"}),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': int(y), 'value': int(y)} for y in sorted(df['year'].unique())],
                value=int(df['year'].max()),
                clearable=False,
                style={"width": "200px"}
            )
        ], width=3)
    ], className="mb-4"),

    # World Heatmap row
    dbc.Row([
        dbc.Col([dcc.Graph(id='world-heatmap')], width=12)
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

# Footer
app.layout.children.append(
    dbc.Row([
        dbc.Col(html.Footer('© Sep 2025 Jeel Faldu, Matheus Souza, Hamed Taeb, Victor Forman  / Project. Data Source: Kaagle Dataset', className='text-center text-muted py-2'), width=12)
    ])
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

@app.callback(
    Output('world-heatmap', 'figure'),
    Input('year-dropdown', 'value')
)
def update_world_heatmap(selected_year):
    # Filter and aggregate in case of duplicates
    dff = df[df['year'] == selected_year].groupby('country', as_index=False)['happiness_score'].mean()

    fig = px.choropleth(
        dff,
        locations='country',
        locationmode='country names',   # directly use country names
        color='happiness_score',
        hover_name='country',
        color_continuous_scale=['blue', 'white', 'red'],
        range_color=(df['happiness_score'].min(), df['happiness_score'].max()),
        projection='natural earth',
        title=f'Global Happiness Scores ({selected_year})'
    )

    fig.update_traces(marker_line_width=0.2)
    fig.update_layout(
        margin=dict(l=10, r=10, t=50, b=10),
        coloraxis_colorbar=dict(title='Happiness Score', ticks='outside')
    )
    return fig

# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7124))  
    app.run_server(debug=True, host='0.0.0.0', port=port)
