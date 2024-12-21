from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

# Define the theme to use - we are using the 'Sandstone' theme from Bootswatch: https://bootswatch.com/sandstone/
external_stylesheets = [dbc.themes.BOOTSTRAP]

### Data Loading & Cleaning
# Load the dataframe
df = pd.read_excel(r"C:\Users\conno\Python\PythonforGeoscience\GitHub\Geoscience-in-Dash\01_Porosity Permeability Dash\assets\Realpore Data_Trimmed.xlsx")

# Drop null rows in the porosity (CPH) column
df.dropna(subset='CPH', inplace=True)

### App Code
# Define the app and use the previously defined external stylesheet
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Making our layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            [
                html.H2(
                    'Well Selection', 
                    className='text-light'
                ),

                dcc.Dropdown(
                    df.Well.unique(), 
                    id='well-selection'
                ),
            ],  
        width=2,  # Left column width for dropdown
        style={'backgroundColor':'#343a40',
               'padding':'20px',
               'height':'100vh',
               'color':'black'
            }
    ),
    # Graph
        dbc.Col(
            dcc.Graph(id='graph-content',
            style={'height':'100%'}
        ),
            width=10,
            style={
                'height':'100vh',
                'padding':'0'
            }
        )
                # Center and right column width for the graph
    ])
], fluid=True)  # Use `fluid=True` for responsive behavior


# Callback to update the graph when the well is changed
@callback(
    Output('graph-content', 'figure'),
    Input('well-selection', 'value')
)

# Related function to update graph, using porosity as X col, and permeability as y col, with log-y axis
def update_graph(value):
    dff=df[df.Well==value]
    fig = px.scatter(dff, 
                      x='CPH', 
                      y='KAH',
                      labels={'CPH':'Porosity (%)', 'KAH':'Permeability (mD)'},
                      log_y=True)#
    
    fig.update_traces(
        marker=dict(
            size=10,
            color='black',
            opacity=0.8,
            symbol='circle'
        )

    )

    return fig

if __name__ =='__main__':
    app.run(debug=True)


