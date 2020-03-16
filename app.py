import pandas as pd
import numpy as np

from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbs
from dash.dependencies import Input, Output, State

external_stylesheets = [dbs.themes.MINTY]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions']=True

app.layout = html.Div([
    
    #left-hand column
    html.Div([

        #continer for dashboard name
        html.Div([

            html.H1(
                'Dash/Flask Format',
                style = {
                    'margin':'20px'
                }
            ),

            html.H4(
                'Descriptions Descriptions Descriptions',
                style = {
                    'padding-left':'20px'
                }
            )

        ], className = 'card text-white bg-secondary mb-3',

        ),

        #container for csv upload/template download
        html.Div([ 

            #file upload box
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px',
                },

                # Allow multiple files to be uploaded
                multiple=True
            ),        
        ])

    ], style = {
            'margin':'50px'

        }
    ),

    #right column
    html.Div([

        #container for graph output
        html.Div([

        ]),

        #container for data output
        html.Div([ 

        ])

    ])


], className = 'row')

if __name__ == '__main__':
    app.run_server(debug=True)

