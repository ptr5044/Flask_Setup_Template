import xlrd
import pandas as pd
import numpy as np
import pulp
import math

import base64
import datetime
import io
import dash_table
import plotly.graph_objs as go

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
                    'Mars Recipe Optimizer',
                    style = {
                        'margin':'20px',

                    }
                ),

                html.P(
                    'This includes the simple recipe optimizer without price simulation.',
                    style = {
                        'padding-left':'20px',
                        'padding-right':'20px',
                        'padding-bottom':'15px',
                        'padding-top':'-5px'

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
                        'margin': '20px',
                        'position':'absolute',
                    },

                    # Allow multiple files to be uploaded
                    multiple=True
                ),

                html.P(
                    "Please make sure all uploads follow the template below, otherwise the app will not function!",
                    style = {
                        'padding-left':'20px',
                        'padding-top':'100px',
                        'padding-right':'30px',
                        'text-align':'justify'
                    }
                ),

                html.P(
                    "To modify the existing template, adjust recipes, ingredients, and constraints.  Be mindful to retain the current formatting.  For any questions/comments/concerns, contact Phillip Rubin at phillip.rubin@effem.com",
                    style = {
                        'padding-left':'20px',
                        'padding-right':'30px',
                        'text-align':'justify'
                    }
                ),

                html.A(
                    'Download Sample File',
                    id = 'download-link',
                    href = "https://teams.microsoft.com/_#/xlsx/viewer/teams/https:~2F~2Fteam.effem.com~2Fsites~2FRecipeOptimization~2FShared%20Documents~2FGeneral~2Fexample_template.xlsx?threadId=19:0b4cc01bbc0e494fbce614c89e97e319@thread.tacv2&baseUrl=https:~2F~2Fteam.effem.com~2Fsites~2FRecipeOptimization&fileId=4ace4ed9-6fa0-4e9d-acb2-42ab2926ee9c&ctx=files&rootContext=items_view&viewerAction=view",
                    style = {
                        'padding-top':'30px',
                        'padding-left':'20px',
                        'color':'white',
                        'font-size':'20px'
                    }
                )  

            ], className = 'card text-white bg-secondary mb-3',
                style = {
                    'height':'480px'
                })

        ], className = 'col-2',
            style = {
                'margin':'20px',
                'height':'700px'

            }
        ),

        #middle column
        html.Div([

            #upper row
            html.Div([ 

                #graph container
                html.Div([ 

                    html.Div([
                        'Existing Recipe Graph Output'
                    ], className = 'card-header'),

                    html.Div(id = 'output-graph-upload')

                ], className = 'card border-primary mb-3',
                    style = {
                        'height':'500px',
                        'width':'750px',
                        'margin':'20px'
                    }),

            ], className = 'row'),

            #lower row
            html.Div([ 

                #data container
                html.Div([ 

                    html.Div([
                        'Existing Recipe Data Output'
                    ], className = 'card-header'),

                    #output data frame
                    html.Div([ 
                        html.H1()
                    ], className = 'card-body',
                        id = 'output-data-upload')

                ], className = 'card border-secondary mb-3',
                    style = {
                        'height':'500px',
                        'width':'750px',
                        'margin':'20px'
                    }
                )


            ], className = 'row')

        ], className = 'col-4'),

        #left column
        html.Div([

            #upper row
            html.Div([ 

                #graph container
                html.Div([ 

                    html.Div([
                        'Optimized Case Graph Output'
                    ], className = 'card-header'),

                    html.Div(id = 'output-graph-upload2')

                ], className = 'card border-primary mb-3',
                    style = {
                        'height':'500px',
                        'width':'700px',
                        'margin':'20px'
                    }),

            ], className = 'row'),

            #lower row
            html.Div([ 

                #data container
                html.Div([ 

                    html.Div([
                        'Optimized Case Data Output'
                    ], className = 'card-header'),

                    #output data frame
                    html.Div([ 
                        html.H1()
                    ], className = 'card-body',
                        id = 'output-data-upload2')

                ], className = 'card border-secondary mb-3',
                    style = {
                        'height':'500px',
                        'width':'700px',
                        'margin':'20px'
                    }
                )


            ], className = 'row')

        ], className = 'col-4'),

    ], className = 'row',
        style = {
            'width':'2500px',
            'zoom': '75%'
        })

 ])



# I created the functions below a long time ago, they're pretty bad
# please make improvements as you see fit


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

    #parses first sheet into useful elements
    costdf = recipe_df.iloc[:,2]
    ingredients = np.array((recipe_df['Ingredient']))
    seperated_recipes_df = recipe_df.drop(recipe_df.columns[[0,1,2]], axis=1)

    #creates the names for the different optimzed cases
    case_names = []
    for i in range(len(constraint_frames)):
        name = str('case' + str(i+1))
        case_names.append(name)

    #collection df for final output
    all_optimized_recipes = pd.DataFrame()
    
    #sets dictionary for pulp to iterate through, if above 10 variables ingredients get out of order
    alfa = "abcdefghijklmnopqrstuvwxyz"
    adict = dict([ (x[1],x[0]) for x in enumerate(alfa) ])

    #runs the optimization for each constraint             
    for k in range(len(constraint_frames)):

        #each constraint frame is a different case
        df = constraint_frames[k]
        df = df.reset_index().drop("index", axis=1)
   
        #obtains number of ingredients
        ingredient_number = df.iloc[:, :-4].iloc[:, 3:].columns.size

        #creates problem for optimization to solve
        prob = pulp.LpProblem('CheapestRecipe', pulp.LpMinimize)
        
        #creates variables or ingredients for linear optimization
        decision_variables = []
        for i in range(ingredient_number):
            variable = str(alfa[i])
            variable = pulp.LpVariable(str(variable), cat= 'Continuous')
            decision_variables.append(variable)

        #creates problem to solve
        total_cost = ''      
        for i in range (costdf.size):
            formula = decision_variables[i] * costdf[i]
            total_cost += formula

        prob += total_cost

        #creates constraints for recipes
        for i in range(len(df.index)):
            constraint = ''
            
            #performs action for each variable or ingredient
            for c in range(ingredient_number):
                c += 3
                
                #if a cell has a digit, it is a constraint, ignores all NaN
                if math.isnan(df.iat[i,c]) == False:
                    var = (decision_variables[c-3])
                    
                    #checks digit value and multiplies variable by it
                    multiplier = float(df.iat[i,c])
                    constraint += (var * multiplier)
                    
            #indentifies int that constraint must abide by
            constraint_int = df.iat[i,len(df.columns)-1]
            
            #checks comparison operator to finish constraint
            constraint_compare = df.iat[i, len(df.columns)-2]
            if constraint_compare == '<=':
                prob += constraint <= constraint_int
            if constraint_compare == '>=':
                prob += constraint >= constraint_int
            if constraint_compare == '==' or constraint_compare == '=':
                prob += constraint == constraint_int

        prob.solve()

        print(prob)

        #writes recipe for solved optimization problem
        recipe = np.array([])
        for v in prob.variables():
            recipe = np.append(recipe, v.varValue)
        recipe = recipe[recipe != np.array(None)]

        


        #established dataframe constaining optimized recipe values
        optimum_case = pd.DataFrame(np.zeros((1, ingredients.size)))
        optimum_case.columns = ingredients
        optimum_case['cost'] = find_cost(np.array(costdf), recipe)
        optimum_case['Recipe Name'] = case_names[k]


        for e in range(ingredients.size):
            optimum_case.at[0, ingredients[e]] = recipe[e]

                
        #appends to original dataframe
        all_optimized_recipes = all_optimized_recipes.append(optimum_case)


    # seperated_recipes_df = seperated_recipes_df.drop(seperated_recipes_df.columns[0], axis = 1)


    #checks how many existing recipes there are
    all_existing_recipes = pd.DataFrame()

    for col in seperated_recipes_df.columns:
        existing_recipe = pd.DataFrame(np.zeros((1, ingredients.size)))
        existing_recipe.columns = ingredients

        #finds cost and ingredient amount for each existing recipe
        for g in range(len(seperated_recipes_df.index)):
            existing_recipe.iat[0, g] = seperated_recipes_df.iloc[g][col]
        existing_recipe['cost'] = find_cost(np.array(costdf), np.array(seperated_recipes_df[col]))
        existing_recipe['Recipe Name'] = col[-6:]
        all_existing_recipes = all_existing_recipes.append(existing_recipe)
 
        

    #organizes dataframe
    neworder = np.insert(ingredients, 0, 'Recipe Name', axis = 0)
    neworder = np.insert(neworder, 1, 'cost', axis = 0)

    all_optimized_recipes = all_optimized_recipes.reindex(columns=neworder)
    all_existing_recipes = all_existing_recipes.reindex(columns=neworder)

    return all_existing_recipes.round(2), all_optimized_recipes.round(2)


#obtain files from front end
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            return html.Div([ 
                'You uploaded a CSV, could you upload an Excel file please?'
            ]), html.Div([' '])
        elif 'xls' or 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            try:
                recipe_df = pd.read_excel(io.BytesIO(decoded), sheet_name = 0).dropna()
                constraints_df = pd.read_excel(io.BytesIO(decoded), sheet_name = 1)
                existing_output, optimized_output = run_optimizer(recipe_df, constraints_df)

                min_range = existing_output['cost'].min()-100
                max_range = existing_output['cost'].max()+50

                existing_bar_figure = go.Figure(data = [go.Bar(x = existing_output['Recipe Name'], y = existing_output['cost'], marker = {'color': existing_output['cost'], 'colorscale' : 'tealrose'})])
                existing_bar_figure.update_layout(title_text = 'Cost for Existing Recipes')
                existing_bar_figure.update_xaxes(title_text = 'Recipe Name', tickangle = 45)
                existing_bar_figure.update_yaxes(range = [min_range, max_range], title_text = 'Cost for 1000kg')

                optimized_bar_figure = go.Figure(data = [go.Bar(x = optimized_output['Recipe Name'], y = optimized_output['cost'], marker = {'color': optimized_output['cost'], 'colorscale' : 'cividis'})])
                optimized_bar_figure.update_layout(title_text = 'Cost for Optimized Cases')
                optimized_bar_figure.update_xaxes(title_text = 'Recipe Name', tickangle = 45)
                optimized_bar_figure.update_yaxes(range = [min_range, max_range], title_text = 'Cost for 1000kg')


            except Exception as e:
                print(e)
                return html.Div([ 
                    'There is somthing wrong with your file format, try again please'
                ]), html.Div([' '])
                

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ]), html.Div(' ')

    return html.Div([
        html.H6(
            'Ingredients for Existing Recipes',
            style = {
                'padding-bottom' : '10px'
            }
        ),

        dash_table.DataTable(
            data=existing_output.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in existing_output.columns]
        )
    ]), html.Div([
            dcc.Graph(
                figure = existing_bar_figure
            )
        ]),html.Div([
        html.H6(
            'Ingredients for Optimized Recipes',
            style = {
                'padding-bottom' : '10px'
            }
        ),

        dash_table.DataTable(
            data=optimized_output.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in optimized_output.columns]
        )
    ]),html.Div([
            dcc.Graph(
                figure = optimized_bar_figure
            )
        ])

@app.callback(
        [Output('output-data-upload', 'children'),
        Output('output-graph-upload', 'children'),
        Output('output-data-upload2', 'children'),
        Output('output-graph-upload2', 'children')],
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename'),
        State('upload-data', 'last_modified')])


def update_output(content, names, dates):
    if content is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(content, names, dates)]

        return children[0]
    else:

        return html.Div(""), html.H4(["Hi there! Upload your file to get started."], style = {'margin':'20px'}), html.Div(""), html.Div("")
    



if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050,debug=True)

# if __name__ == '__main__':
#     app.run_server(host='127.0.0.1', port=8050,debug=True)


