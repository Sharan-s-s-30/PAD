import pandas as pd
import os
import subprocess
import stat
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from sklearn.preprocessing import LabelEncoder

file_path = os.path.join('cleaned_data', 'cleaned_autos.csv')

# Reading csv into raw dataframe
df = pd.read_csv(file_path, encoding="latin-1")
required_columns = ['price', 'yearOfRegistration', 'powerPS', 'kilometer', 'gearbox', 'brand', 'vehicleType']

df = df.dropna(subset=required_columns)
label_encoder = LabelEncoder()
df['gearbox'] = label_encoder.fit_transform(df['gearbox'])

df = pd.get_dummies(df, columns=['brand'], drop_first=True)

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Vehicle Price Analysis"
server = app.server


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True  # Suppress callback exceptions

# Define the layout with CSS
app.layout = html.Div([
    html.H1("Vehicle Price Analysis Dashboard", style={'text-align': 'center', 'color': '#333'}),
    dcc.Dropdown(
        id='brand-dropdown',
        options=[{'label': brand.replace('brand_', ''), 'value': brand} for brand in df.columns if 'brand_' in brand],
        multi=True,
        placeholder="Select brands",
        style={'width': '50%', 'margin': '0 auto', 'padding': '10px'}
    ),
    html.Div([
        html.Div([
            dcc.Graph(id='price-distribution', style={'border': '1px solid #ccc', 'padding': '10px'})
        ], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='average-price-trend', style={'border': '1px solid #aaa', 'padding': '10px'})
        ], style={'width': '48%', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'justify-content': 'space-around'}),
    html.Div([
        html.Div([
            dcc.Graph(id='count-by-brand', style={'border': '1px solid #999', 'padding': '10px'})
        ], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='kilometer-distribution', style={'border': '1px solid #555', 'padding': '10px', 'margin': '20px'})
        ], style={'width': '48%', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'justify-content': 'space-around'}),
    html.Div([
        html.Div([
            dcc.Graph(id='price-distribution-type', style={'border': '1px solid #555', 'padding': '10px', 'margin': '20px'})
        ], style={'width': '48%', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'justify-content': 'space-around'}),
], style={'font-family': 'Arial, sans-serif'})

# Define callbacks
@app.callback(
    Output('price-distribution', 'figure'),
    [Input('brand-dropdown', 'value')]
)
def update_price_distribution(selected_brands):
    if selected_brands:
        filtered_df = df[df[selected_brands].any(axis=1)]
    else:
        filtered_df = df
    fig = px.histogram(filtered_df, x='price', title='Price Distribution')
    fig.update_layout(plot_bgcolor='#eaf2f8', paper_bgcolor='#eaf2f8')
    return fig

@app.callback(
    Output('average-price-trend', 'figure'),
    [Input('brand-dropdown', 'value')]
)
def update_price_trend(selected_brands):
    if selected_brands:
        filtered_df = df[df[selected_brands].any(axis=1)]
    else:
        filtered_df = df
    trend_data = filtered_df.groupby('yearOfRegistration')['price'].mean().reset_index()
    fig = px.line(trend_data, x='yearOfRegistration', y='price', title='Average Price Trend Over Time')
    fig.update_layout(plot_bgcolor='#f2f4f4', paper_bgcolor='#f2f4f4')
    return fig

@app.callback(
    Output('count-by-brand', 'figure'),
    [Input('brand-dropdown', 'value')]
)
def update_count_by_brand(selected_brands):
    if selected_brands:
        filtered_df = df[df[selected_brands].any(axis=1)]
    else:
        filtered_df = df
    brand_columns = [col for col in filtered_df.columns if 'brand_' in col]
    count_data = filtered_df[brand_columns].sum().reset_index()
    count_data.columns = ['brand', 'count']
    count_data['brand'] = count_data['brand'].str.replace('brand_', '')
    fig = px.bar(count_data, x='brand', y='count', title='Count of Vehicles by Brand')
    fig.update_layout(plot_bgcolor='#d4e6f1', paper_bgcolor='#d4e6f1')
    return fig

@app.callback(
    Output('kilometer-distribution', 'figure'),
    [Input('brand-dropdown', 'value')]
)
def update_kilometer_distribution(selected_brands):
    if selected_brands:
        filtered_df = df[df[selected_brands].any(axis=1)]
    else:
        filtered_df = df
    fig = px.histogram(filtered_df, x='kilometer', title='Kilometer Distribution')
    fig.update_layout(plot_bgcolor='#fef9e7', paper_bgcolor='#fef9e7')
    return fig

@app.callback(
    Output('price-distribution-type', 'figure'),
    [Input('brand-dropdown', 'value')]
)
def update_price_distribution_type(selected_brands):
    if selected_brands:
        filtered_df = df[df[selected_brands].any(axis=1)]
    else:
        filtered_df = df
    fig = px.box(filtered_df, x='vehicleType', y='price', title='Price Distribution by Vehicle Type')
    fig.update_layout(plot_bgcolor='#faebd7', paper_bgcolor='#faebd7')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)