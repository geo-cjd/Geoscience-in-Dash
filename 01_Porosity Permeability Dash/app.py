from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

# Define the theme to use - we are using the 'Sandstone' theme from Bootswatch: https://bootswatch.com/sandstone/
external_stylesheets = [dbc.themes.BOOTSTRAP]

# Load the dataframe
df = pd.read_excel(r'Realpore Data_Trimmed.xlsx')

# Define the app and use the previously defined external stylesheet
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Making our layout
app.layout =dbc.Container([
    html.H1(children='Porosity-Permeability Dash', style={'textAlign':'center'}),
    dcc.Dropdown(df.Well.unique(), id='well-selection'),
    dcc.Graph(id='graph-content')
])

# Callback to update the graph when the well is changed
@callback(
    Output('graph-content', 'figure'),
    Input('well-selection', 'value')
)

# Related function to update graph, using porosity as X col, and permeability as y col, with log-y axis
def update_graph(value):
    dff=df[df.Well==value]
    return px.scatter(dff, x='CPH', y='KAH')

if __name__ =='__main__':
    app.run(debug=True)