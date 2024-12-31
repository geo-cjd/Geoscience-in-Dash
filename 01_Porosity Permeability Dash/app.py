from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import io
import base64

# Define the theme to use - we are using the 'Sandstone' theme from Bootswatch: https://bootswatch.com/sandstone/
external_stylesheets = [dbc.themes.BOOTSTRAP]

### App Code
# Define the app and use the previously defined external stylesheet
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Making our layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            [
                # Header text at top of column
                html.H2(
                    'Porosity-Permeability Dash', 
                    style={'margin-bottom':'30px','font-size':'28px', 'color':'white', 'fontWeight': 'bold'}
                ),

                # Data upload feature
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.U('Select Files')
                    ]),
                    style={'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '2px',
                        'textAlign': 'center',
                        'margin': '30px'
                    },
                    multiple=False # Prevents uploading of multiple files
                ),

                # File upload text
                html.Div(id='output-data-upload',
                         style={'textAlign':'center', 'margin-bottom':'30px'}),

                # Well selection dropdown
                dcc.Dropdown(
                    id='well-selection',
                    placeholder='Select a well:',
                    clearable=True,
                    searchable=True,
                    style={'margin-bottom':'30px', 'color':'black'}
                ),

                # Colour selection dropdown
                dcc.Dropdown(
                    id='colour-selection',
                    placeholder='Colour points by:',
                    clearable=True,
                    searchable=True,
                    style={'margin-bottom':'30px', 'color':'black'}
                ),

                # Size selection dropdown
                dcc.Dropdown(
                    id='size-selection',
                    placeholder='Size points by:',
                    clearable=True,
                    searchable=True,
                    style={'margin-bottom':'30px', 'color':'black'}
                ),

                # Links to code at base of sidebar
                html.Div(
                    dbc.Nav([
                        dbc.NavLink(
                            html.Img(
                                src='assets/github-mark-white.png',
                                alt='Source Code',
                                id='github-logo',
                                width=30,
                                height=30
                            ),
                            href='https://github.com/geo-cjd/Geoscience-in-Dash/tree/6d68f02f3b1ca222241a487fa44c9c36f7a216b2/01_Porosity%20Permeability%20Dash',
                            style={'textAlign':'center'}
                        )
                    ]),
                    style={
                        'position':'absolute',
                        'left':'10px',
                        'bottom':'50px',
                        'width':'100%',
                        'textAlign':'center'
                    }
                ),

                # Licensing statement
                html.Div(
                    html.P([
                        'Data are © GeoProvider ',
                         html.A('https://geoprovider.no/ ', href='https://geoprovider.no/'),
                         'and licensed by CC-BY 4.0'
                    ], style={'color':'white', 'fontSize':'11px'}),
                    style={
                        'position':'absolute',
                        'bottom':'10px',
                        'left':'25px',
                        'color':'white',
                    }
                )
            ],  

        width=3,  # Left column width
        style={'backgroundColor':'#343a40',
               'padding':'20px',
               'height':'100vh',
               'color':'white'
            }
    ),
    # Graph on right (new column)
        dbc.Col(
            dcc.Graph(id='graph-content', style={'height':'100%'}),
            width=9,
            style={
                'height':'100vh',
                'padding':'0'
            }
        )
    ]),
    dcc.Store(id='stored-data') # Store data passed to app
], fluid=True)

### FILE UPLOAD 

# Function to open and parse contents of .csv or .xlsx files
def parse_file(file_contents, filename):
    content_type, content_string =  file_contents.split(',')

    # Decode either .csv or .xlsx files
    decoded=base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df=pd.read_csv(io.StringIO(decoded.decode('utf=8')))
            df.dropna()
            
        elif 'xlsx' in filename:
            df=pd.read_excel(io.BytesIO(decoded))
            df.dropna()

        else:
            return None
    
    # Return error if file not processed
    except Exception as e:
            return html.Div(['Error processing file'])
    
    # Dataframe returned otherwise
    return df
    
@callback(
    [Output('stored-data', 'data'),
     Output('output-data-upload', 'children')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)

# Function to update output of text below file upload
def update_output(file_contents, filename):
    if file_contents is None:
        return None, "No file has been uploaded"

    df = parse_file(file_contents, filename)
    if df is None:
        return None, "Error processing uploaded file"
    
    return df.to_dict('records'), "Successful"

# Update dropdown from uploaded file
@callback(
    [Output('well-selection', 'options'),
     Output('colour-selection', 'options'),
     Output('size-selection', 'options')],
    [Input('stored-data', 'data')]
)

# Function to update dropdown options from loaded file and dataframe
def update_dropdown_options(data):
        if data is None:
            return [], [], [] # Could be improved - temporary workaround for now

        df = pd.DataFrame(data)
        well_options = [{'label': well, 'value': well} for well in df['Well'].unique()]
        column_options = [{'label': col, 'value': col} for col in df.columns if col not in ['CPH', 'KAH']]

   
    # Return well options and column options twice for both colour and size - latter probably needs redoing to have better variable identification
        return well_options, column_options, column_options

### GRAPHING

# Callback to Update the Graph
@callback(
    Output('graph-content', 'figure'),
    [Input('well-selection', 'value'),
     Input('colour-selection', 'value'),
     Input('size-selection', 'value'),
     Input('stored-data', 'data')]
)
def update_graph(well, color_col, size_col, data):
    if data is None:
        return {}  # Empty graph if no data is uploaded

    df = pd.DataFrame(data)

    # Filter by selected well
    if well:
        df = df[df['Well'] == well]

    # Create scatter plot with plotly express (px)
    fig = px.scatter(
        df,
        x='CPH',
        y='KAH',
        color=color_col if color_col else None,
        size=size_col if size_col else None,
        labels={'CPH': 'Porosity (%)', 'KAH': 'Permeability (mD)'},
        log_y=True
    )

    # Small updates to marker alpha and shape
    fig.update_traces(
        marker=dict(
            opacity=0.8,
            symbol='circle'
        )

    )
    return fig
    
if __name__ =='__main__':
    app.run(debug=True)


