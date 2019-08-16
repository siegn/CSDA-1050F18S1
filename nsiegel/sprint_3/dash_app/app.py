import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State

import pickle
import glob
from textwrap import dedent
import plotly.graph_objs as go
import time

import pandas as pd

# load saved models and data
df = pd.read_parquet('../../sprint_2/data/whisky_tfidf.parquet')
df2 = pd.DataFrame([[1, 2], [3, 4], [5, 6], [7, 8]], columns=["A", "B"])
whiskyinfo = pd.read_parquet('../../sprint_2/data/whiskyinfo.parquet')
similarities = pd.read_parquet('../../sprint_2/data/similarities2.parquet')

# Create whisky list for dropdown
whiskies = [{'label' : whisky.Name, 'value' : whisky.itemnumber} for whisky in df.reset_index().itertuples()]

# Functions

# Function to find top matches and get info
def show_top_similarities(itemnumber, top_n=5):
    keepcolumns = ['itemnumber','name','style', 'similarity', 'rating','price','rating_per_dollar_per_750']
    return (similarities[(similarities['itemnumber'] == itemnumber) & 
             (similarities['itemnumber'] != similarities['itemnumber2'])]
                 .sort_values('sim', ascending=False)
                 .head(top_n)
                 .drop({'nose_sim','taste_sim','finish_sim','itemnumber'},axis=1)
                 .rename({'itemnumber2':'itemnumber','sim':'similarity'},axis=1)
                 .set_index('itemnumber')
                 .join(whiskyinfo)
                 .reset_index()
                 .rename({'rating_mean':'rating','itemname':'name','index':'itemnumber'},axis=1)
                 [keepcolumns]
                 #.drop({'RedditWhiskyIDs','reviewIDs','index_col'},axis=1)
                 #.rename({'nose_tfidf':'nose','taste_tfidf':'taste','finish_tfidf':'finish'},axis=1)
    )

# Function to print whisky descriptions:
def getwhiskydesc(itemnumber):
    whisky = whiskyinfo.reset_index()[whiskyinfo.reset_index()['itemnumber']==itemnumber]
    name = whisky.itemname.values[0]
    price = str(round(whisky.price.values[0],2))
    size = str(whisky.productsize.values[0])
    rating = str(round(whisky.rating_mean.values[0],2))
    rating_per_dollar_per_750 = str(round(whisky.rating_per_dollar_per_750.values[0],2))
    nose = whisky['nose'].apply(lambda x : ' '.join(x)).values
    taste = whisky['taste'].apply(lambda x : ' '.join(x)).values
    finish = whisky['finish'].apply(lambda x : ' '.join(x)).values
    
    mydict = {'name' : name, 
              'price': price,
              'size' : size,
              'rating' : rating,
              'rating_per' : rating_per_dollar_per_750,
              'nose' : nose,
              'taste' : taste,
              'finish' : finish
             }
    return mydict

# Function to show all suggestions and details of the top suggestion
def displaysuggestions(itemnumber, sort='rating_per_dollar_per_750', top_n = 5):
    columns = ['itemname',
              'similarity', 'rating_per_dollar_per_750','rating_mean','price','productsize',
              'style',
               'nose','taste','finish'
              ]
    results = show_top_similarities(itemnumber, top_n)[columns].sort_values(sort,ascending=False)
    # Print main results
    display(results)
    # Print info about search whisky
    printwhiskydesc(itemnumber)
    # Print info about top match whisky
    printwhiskydesc(results.reset_index().itemnumber.iloc[0])
    
# Whisky Selection Dropdown
whisky_selector = dbc.Row(
    [
        dbc.Col(
            dbc.NavbarBrand("Select Whisky:", className="ml-2"),
            width="auto",
        ),
        dbc.Col( dcc.Dropdown(id = 'input-whisky', 
                                    options = whiskies,
                                    value = 248997, # Laphroaig 10
                                    style={'width':600},
                                    clearable = False),

        width='auto'
        ),

    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)


navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    #dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                    dbc.Col(dbc.NavbarBrand("Whisky Similarity Analysis", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            ),
            href="https://github.com/siegn/CSDA-1050F18S1",
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        
        dbc.Collapse( dbc.NavItem(dbc.Button("About",
            id="collapse-button",
            className="mb-10",
            color="info"))
        , id="navbar-collapse", navbar=True),
        whisky_selector,
       
    ],
    color="primary",
    dark=True,
)

intro_card = [
    dbc.CardHeader("Introduction"),
    dbc.CardBody(
        [
            html.H5("About This Page", className="card-title"),
            dcc.Markdown(dedent('''
                Reddit posts from multiple subreddits and users were analysed in order to determine
                Which subreddits have a lot of posts from the same author.

                These were then analysed and investigated using community detection algorithms.
                By selecting a subreddit it will show you which community it is part of.

                The closer together and darker the lines the more strongly correlated the subreddits.
                '''),
                className="card-text",
            ),
        ]
    ),
]

data_card = [
    dbc.CardHeader("Data"),
    dbc.CardBody(
        [
            html.H5("Data", className="card-title"),
             dcc.Markdown(dedent('''
                Using data from pushshift tables "pushshift.rt_reddit.comments" and "pushshift.rt_reddit.submissions", 
                created by reddit user [Stuck_In_the_Matrix](https://www.reddit.com/r/bigquery/comments/8lfu6u/pushshift_will_now_be_integrating_bigquery_into/)
                '''))
             ,
              html.H5("Query", className="card-title"),
             dcc.Markdown(dedent('''
                The query was executed on BigQuery and is a modified version of the one created by
                 [Max Woolf](https://minimaxir.com/)
                '''))
        ]
    ),
]

info_card = [
    dbc.CardHeader("More Info"),
    dbc.CardBody(
        [
            html.H5("Source Code", className="card-title"),
            dcc.Markdown(dedent('''
                Created by Nelson Siegel.

                For Source Code for this Dash app as well as Jupyter notebooks explaining the process
                and the creation of the datasets this app uses, see my [github](https://github.com/siegn/redditgraph)
                '''))
        ]
    ),
]

all_cards = [
   
]

selected_card =  dbc.Card(
        [
            dbc.CardHeader('Name', className='card-title', id='selected-name'),
            dbc.CardBody(
                [
                    dcc.Markdown(''' #Markdown ''', id ='selected-markdown')
                ]
             
        )
        ],
    style={"width":"18rem"}
)


body = dbc.Container(
    [
        dbc.Row(
            [
            dbc.Col(
                dbc.Collapse(
                    dbc.Card(intro_card, color="success", inverse=True),
                    id='collapse1'
                ),
            ),
            dbc.Col(
                dbc.Collapse(
                    dbc.Card(data_card, color="info", inverse=True),
                    id='collapse2'
                ),
            ),
            dbc.Col(
                dbc.Collapse(
                    dbc.Card(info_card, color="warning", inverse=True),
                    id='collapse3'
                ),
            ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [   
                        dcc.Loading(id="loading-1", children=[html.P(id="loading-output-1")], type="graph",fullscreen=True),
                        selected_card
                    ],
                    width=True
                ),
                
            ]
        ),
        #dbc.Table.from_dataframe(df, striped=True, bordered=True,hover=True)
        html.Div("Hello"),
        html.Div(
                dash_table.DataTable(
                    id='table',
                    columns=[{"name": i, "id": i} for i in df2.columns],
                    data=df2.to_dict('records'),
                    sort_action="native"
                )
        )

       ],
    className="mt-4",fluid=True
)




# interface
#ext_css = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css']
external_stylesheets = [dbc.themes.YETI]
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets
)
df2 = pd.DataFrame([[1, 2], [3, 4], [5, 6], [7, 8]], columns=["A", "B"])



server = app.server
app.layout = html.Div([navbar,body])
#app.layout = html.Div([suggestiontable,navbar,body])
@app.callback(
    Output("collapse1", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse1", "is_open")],
)
def toggle_collapse1(n, is_open):
    if n:
        return not is_open
    return is_open

server = app.server
app.layout = html.Div([navbar,body])

@app.callback(
    Output("collapse2", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse2", "is_open")],
)
def toggle_collapse2(n, is_open):
    if n:
        return not is_open
    return is_open

server = app.server
app.layout = html.Div([navbar,body])

@app.callback(
    Output("collapse3", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse3", "is_open")],
)
def toggle_collapse3(n, is_open):
    if n:
        return not is_open
    return is_open


                

# Update output text when whisky selected
@app.callback([
    Output("loading-output-1", "children"),
    Output('selected-name','children'),
    Output('selected-markdown','children'),
    Output('table','columns'),
    Output('table','data')
    ],
    [Input('input-whisky','value')])
def update_text(value):
    whiskydict = getwhiskydesc(value)
    name = whiskydict.get('name')
    price = '$' + whiskydict.get('price')
    size = whiskydict.get('size') + 'ml'
    rating = whiskydict.get('rating') + '/100'
    ratingper = whiskydict.get('rating_per')
    
    markdown = '''**Price:** ''' + price + '''  
    **Size:** ''' + size + '''  
    **Rating:** ''' + rating + '''  
    **Rating / $:** ''' + ratingper
    
    # get suggestions
    suggestions = show_top_similarities(value)
    
    columns=[{"name": i, "id": i} for i in suggestions.columns]
    data=suggestions.to_dict('records')
    
    #print(text)
    return None, name, markdown, columns, data

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
