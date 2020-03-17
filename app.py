import xlrd
import pandas as pd
import numpy as np

import base64
import datetime
import io
import dash_table

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

                html.Div(id = 'data-file-output')  

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
                ], className = 'card-header'),

                html.Div([ 
                    html.H1()
                ], className = 'card-body',
                    id = 'output-data-upload')

            ], className = 'card border-secondary mb-3',
                style = {
                    'height':'700px',
                    'width':'400px',
                    'margin':'20px'
                })


        ], className = 'col-3')


    ], className = 'row')



 ])

def find_cost(pricelist, ingr_cost):
    cost = 0
    for i in range(ingr_cost.size):
        cost += (pricelist[i]*ingr_cost[i])
    return cost
 
def run_optimizer(recipe_df, constraints_df):

    #seperates each of the cases into seperate data frames
    df_seperators = (constraints_df.loc[constraints_df[constraints_df.columns[2]] == 'Constraints ID'].index)

    #compiles to constraint data frames into a list
    constraint_frames = list()
    for i in range(df_seperators.size):
        if i < ((df_seperators.size)-1):
            constraint_frames.append(constraints_df.loc[(df_seperators[i]+1):(df_seperators[i+1]-2)])
        else:
            constraint_frames.append(constraints_df.loc[df_seperators[i]:])

    costdf = recipe_df.iloc[:,2]
    ingredients = np.array((recipe_df['Ingredient']))
    seperated_recipes_df = recipe_df.drop(recipe_df.columns[[0,1,2]], axis=1)

    #creates the names for the different optimzed cases
    case_names = []
    for i in range(len(constraint_frames)):
        name = str('case' + str(i+1))
        case_names.append(name)


        
    return case_names[0]


#obtain files from front end
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            return html.Div([ 
                'You uploaded a CSV, could you upload an Excel file please?'
            ])
        elif 'xls' or 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            try:
                recipe_df = pd.read_excel(io.BytesIO(decoded), sheet_name = 'Cleaned-Milk').dropna()
                constraints_df = pd.read_excel(io.BytesIO(decoded), sheet_name = 'MM Milk constraints')
                data_len = str(run_optimizer(recipe_df, constraints_df))


            except Exception as e:
                print(e)
                return html.Div([ 
                    'There is somthing wrong with your file format, try again please'
                ])

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H5(data_len),
        html.H6(datetime.datetime.fromtimestamp(date)),
    ])


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])


def update_output(content, names, dates):
    if content is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(content, names, dates)]

        return children

if __name__ == '__main__':
    app.run_server(debug=True)

