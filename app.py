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
    html.Div([ 

        #left-hand column
        html.Div([

            #continer for dashboard name
            html.Div([

                html.H1(
                    'Recipe Optimization',
                    style = {
                        'margin':'20px'
                    }
                ),

                html.P(
                    'Descriptions Descriptions Descriptions',
                    style = {
                        'padding-left':'20px'
                    }
                )

            ], className = 'card text-white bg-primary mb-3',
                style = {
                    'height':'200px'
                },

            ),

            #container for csv upload/template download
            html.Div([ 

                html.H4(
                    'Upload Your File',
                    style = {
                        'margin':'20px'
                    }
                ),

                #file upload box
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '300px',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '30px',
                        'position':'absolute'
                    },

                    # Allow multiple files to be uploaded
                    multiple=True
                ),        
            ], className = 'card bg-light mb-3',
                style = {
                    'height':'480px'
                })

        ], className = 'col-3',
            style = {
                'margin':'20px',
                'height':'700px'

            }
        ),

        #middle column
        html.Div([

            #graph container
            html.Div([ 

                html.Div([
                    'Graph Output'
                ], className = 'card-header')

            ], className = 'card border-primary mb-3',
                style = {
                    'height':'700px',
                    'width':'600px',
                    'margin':'20px'
                })


        ], className = 'col-5'),

        #right column
        html.Div([ 

            #data container
            html.Div([ 

                html.Div([
                    'Data Output'
                ], className = 'card-header')

            ], className = 'card border-secondary mb-3',
                style = {
                    'height':'700px',
                    'width':'400px',
                    'margin':'20px'
                })


        ], className = 'col-3')


    ], className = 'row')



 ])

if __name__ == '__main__':
    app.run_server(debug=True)

