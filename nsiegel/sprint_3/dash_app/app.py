import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State, ClientsideFunction
import flask

import pickle
import glob
from textwrap import dedent
import plotly.graph_objs as go
import time

import pandas as pd

# load saved models and data

df = pd.read_parquet('/app/data/whisky_tfidf.parquet')
whiskyinfo = pd.read_parquet('/app/data/whiskyinfo.parquet')
similarities = pd.read_parquet('/app/data/similarities.parquet')
itemlinks = pd.read_parquet('/app/data/itemlinks.parquet')
reviewlist = pd.read_parquet('/app/data/reviewlist.parquet')

# chart colors
infocolor = 'rgb(106,192,222)'
lightinfocolor = 'rgb(220,241,248)'
primarycolor = 'rgb(44,136,180)'
successcolor = 'rgb(82,173,109)'
lightsuccesscolor = 'rgb(167,214,181)'
superlightsuccesscolor = 'rgb(222,239,227)'

similarityBgColor = lightinfocolor
similarityColor = primarycolor
similarityHeaderBgColor = primarycolor
similarityHeaderColor = 'white'

reviewBgColor = superlightsuccesscolor 
reviewColor = 'black'
reviewHeaderBgColor = lightsuccesscolor
reviewHeaderColor = 'black'

# temp till data loads
df2 = pd.DataFrame([[1, 2], [3, 4], [5, 6], [7, 8]], columns=["A", "B"])

# Create whisky list for dropdown
whiskies = [{'label' : whisky.Name, 'value' : whisky.itemnumber} for whisky in df.reset_index().itertuples()]

image_directory = 'wordclouds'
static_image_route = '/home/jupyter-nelson/CSDA-1050F18S1/nsiegel/sprint_3/dash_app/wordclouds/' # /app/wordclouds when publishing

# Functions

# Gets markdown with links to user reviews
def getReviews(itemnumber):
    return reviewlist.loc[itemnumber].rename(columns={'username':'Username','rating':'Rating','reviewLink':'Link'})[['Rating','Username','Link']]

# Get LCBO link for item
def getLCBOLink(itemnumber):
    return itemlinks[itemlinks['itemnumber']==itemnumber].link.get_values()[0]

# Function to find top matches and get info
def show_top_similarities(itemnumber, top_n=5):
    keepcolumns = ['id','Name','Style', 'Similarity', 'Rating','Price','Rating/$','ABV']
    return (similarities[(similarities['itemnumber'] == itemnumber) & 
             (similarities['itemnumber'] != similarities['itemnumber2'])]
                 .sort_values('sim', ascending=False)
                 .head(top_n)
                 .drop({'nose_sim','taste_sim','finish_sim','itemnumber'},axis=1)
                 .rename({'itemnumber2':'itemnumber','sim':'similarity'},axis=1)
                 .set_index('itemnumber')
                 .join(whiskyinfo)
                 .reset_index()
                 .rename({'itemname':'Name','style':'Style','similarity':'Similarity','rating_mean':'Rating',
                          'itemnumber':'id','price':'Price','rating_per_dollar_per_750':'Rating/$', 'alcoholpercentage':'ABV'},axis=1)
                 [keepcolumns]
    )

# Function to print whisky descriptions:
def getwhiskydesc(itemnumber):
    whisky = whiskyinfo.reset_index()[whiskyinfo.reset_index()['itemnumber']==itemnumber]
    if len(whisky.itemname.values) > 0:
        name = whisky.itemname.values[0]
        price = str(round(whisky.price.values[0],2))
        size = str(whisky.productsize.values[0])
        rating = str(round(whisky.rating_mean.values[0],2))
        rating_per_dollar_per_750 = str(round(whisky.rating_per_dollar_per_750.values[0],2))
        alcohol_percentage = str(round(whisky.alcoholpercentage.values[0],0))

        link = getLCBOLink(itemnumber)

        markdown = '''**Price:** $''' + price + '''  
                    **Size:** ''' + size + '''ml    
                    **Alcohol:** ''' + alcohol_percentage + '''%  ''' + '''  
                    **Rating:** ''' + rating + '''  
                    **Rating / $:** ''' + rating_per_dollar_per_750 
        if link is None:
            markdown += '''  
            **LCBO Link:** No longer listed at LCBO '''
        else:
            markdown += '''  
            **LCBO Link:** [**View on LCBO Site**](''' + str(link) + ''' "View on LCBO")'''

    else:
        name = 'Not Found'
        markdown = '''**Cannot Find ID:**''' + str(itemnumber)
    return name, markdown

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
    

navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    #dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                    dbc.Col(dbc.NavbarBrand("LCBO Whisky Similarity Analysis", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            ),
            href="https://github.com/siegn/CSDA-1050F18S1",
        ),

        dbc.NavItem(
            dbc.Button("About",
                id="collapse-button",
                className="mb-10",
                color="info"
            )
        )
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
               This page was created to answer two questions:

               * Given a whiskey that the user enjoys, how can we tell other whiskeys they will enjoy? The method used to determine is flavour similarity Word Mover Distance with Word2Vec on whisky review text.

               * Based on the prices available for these whiskies at the LCBO, what is the best value purchase the user could choose that they would enjoy the most for the least cost? To do this a Rating per Price is displayed.
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
            html.H5("LCBO Products", className="card-title"),
             dcc.Markdown(dedent('''
               Data was pulled from the LCBO api to get product information for all available whiskies.
                '''))
             ,
              html.H5("Reddit Reviews", className="card-title"),
             dcc.Markdown(dedent('''
                Reddit reviews were pulled from the [Reddit Whisky Network Review Archive] (https://docs.google.com/spreadsheets/d/1X1HTxkI6SqsdpNSkSSivMzpxNT-oeTbjFFDdEkXD30o), then full text was gathered using the [praw](https://praw.readthedocs.io/en/latest/) wrapper for the Reddit api.
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
                and the creation of the datasets this app uses, see my [github](https://github.com/siegn/CSDA-1050F18S1).
                '''))
        ]
    ),
]


selectedreviewcollapse =   dbc.Collapse(
                                html.Div(
                                    dash_table.DataTable(
                                        id='selected-reviews',
                                        columns=[{"name": i, "id": i} for i in df2.columns if i not in ['id']],
                                        data=df2.to_dict('records'),
                                        sort_action="native",
                                        page_action="native",
                                        page_current=0,
                                        page_size = 12,
                                        #row_selectable='single',
                                        style_as_list_view=True,
                                        style_cell={
                                            'backgroundColor':reviewBgColor,
                                            'color':reviewColor,
                                            'fontWeight':'bold'
                                        },
                                        style_header={
                                            'backgroundColor':reviewHeaderBgColor,
                                            'color':reviewHeaderColor,
                                            'fontweight':'bold'
                                        },
                                        style_cell_conditional=[
                                            {
                                                'if': {'column_id': 'Link'},
                                               # 'textAlign': 'left',
                                                'overflow':'clip',
                                                'maxWidth':35
                                            } for c in ['Name', 'Style']
                                        ]
                                    ), 
                                ),
                                id='selected_review_collapse', is_open = False
                            )
                        

suggestedreviewcollapse = dbc.Collapse(
                                html.Div(
                                    dash_table.DataTable(
                                        id='suggested-reviews',
                                        columns=[{"name": i, "id": i} for i in df2.columns if i not in ['id']],
                                        data=df2.to_dict('records'),
                                        sort_action="native",
                                        page_action="native",
                                        page_current=0,
                                        page_size = 12,
                                        #row_selectable='single',
                                        style_as_list_view=True,
                                        style_cell={
                                            'backgroundColor':reviewBgColor,
                                            'color':reviewColor,
                                            'fontWeight':'bold'
                                        },
                                        style_header={
                                            'backgroundColor':reviewHeaderBgColor,
                                            'color':reviewHeaderColor,
                                            'fontweight':'bold'
                                        },
                                        style_cell_conditional=[
                                            {
                                                'if': {'column_id': 'Link'},
                                               # 'textAlign': 'left',
                                                'overflow':'clip',
                                                'maxWidth':35
                                            } for c in ['Name', 'Style']
                                            ]
                                        ),
                                ),
                                id='suggested_review_collapse', is_open=False
                            )
                        

selected_card =  dbc.Card(
        [
            dbc.CardHeader('Name', className='card-title', id='selected-name'),
            dbc.Collapse(
                dbc.CardImg(src=None,top=True, id = 'selected-wordcloud'),
            id = 'selected_img_collapse', is_open = True
            ),
            dbc.CardBody(
                [
                    #html.H4('Name', className='card-title', id='selected-name'),
                    dcc.Markdown(''' #Markdown ''', id ='selected-markdown'),
                    dbc.Button("Reviews",
                        id="selected_review_button",
                        className="mb-10",
                        color="success"),
                    selectedreviewcollapse
                ],
            ),
        ],
        color = 'info', inverse=True,
        #style={'width':cardwidth}
)

suggested_card =  dbc.Card(
        [
            dbc.CardHeader('Name', className='card-title', id='suggested-name'),
            dbc.Collapse(
                dbc.CardImg(src=None,top=True, id = 'suggested-wordcloud'),
                id = 'suggested_img_collapse', is_open = True
                ),
            dbc.CardBody(
                [
                    dcc.Markdown(''' #Markdown ''', id ='suggested-markdown'),
                    dbc.Button("Reviews",
                        id="suggested_review_button",
                        className="mb-10",
                        color="success"),
                    suggestedreviewcollapse,
                ]
            ),
        ],
        color = 'info', inverse=True, 
        #style={'width':cardwidth}
)


selectwhisky = [ # Select Whisky
                        dbc.Card([
                            dbc.CardHeader('Select Whisky', className='card-title',style={'textAlign':'center','font-size':24,'color':'white'}),
                            dbc.CardBody(
                                [
                                   dcc.Dropdown(id = 'input-whisky', 
                                       options = whiskies,
                                       value = 248997, # Laphroaig 10
                                       style={'width':600},
                                       clearable = False
                                   ),
                                ]
                            ),
                        ], color='primary', #inverse=True
                        )
                    ]

similartableheader = [ # Similar Table Header
                        html.Div('   '),
                        html.H3('Most Similar Whiskies', style={'textAlign':'center'}),
                    ]

similarwhiskytable = [
                            dash_table.DataTable(
                                id='table',
                                columns=[{"name": i, "id": i} for i in df2.columns if i not in ['id']],
                                data=df2.to_dict('records'),
                                sort_action="native",
                                row_selectable='single',
                                selected_rows = [0],
                                #style_as_list_view=True,
                                style_cell={
                                    'backgroundColor':similarityBgColor,
                                    'color':similarityColor,
                                    'fontWeight':'bold'
                                },
                                style_header={
                                    'backgroundColor':similarityHeaderBgColor,
                                    'color':similarityHeaderColor,
                                    'fontweight':'bold'
                                },
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': c},
                                        'textAlign': 'left'
                                    } for c in ['Name', 'Style']
                                ]
                            )
                        ]



body = dbc.Container(
    [
        # Info cards
        dbc.Row([
            dbc.Collapse(   
                #dbc.CardColumns([
                dbc.Row([
                
                    dbc.Col(
                        dbc.Row([
                            dbc.Card(intro_card, color="dark", inverse=True),
                            html.Br()
                            ], justify = 'center'
                        ), width = 'auto', sm = 11, xl = 3, align='start'
                    ),
                    dbc.Col(
                        dbc.Row([
                            dbc.Card(data_card , color="dark"   , inverse=True), 
                            html.Br()
                            ], justify = 'center'
                            ),  sm = 11, xl = 2, align='start'
                        ), 
                    dbc.Col(
                        dbc.Row([
                            dbc.Card(info_card , color="dark", inverse=True),
                            html.Br()
                            ], justify = 'center'
                        ), width = 'auto', sm = 11,  xl = 3, align='start'
                    )
                
                ] , justify = 'around', align='start'),
                #    ]),
                    id = 'collapse1'
                )
            ],align='start', justify='around'

        ),
        html.Div(id='selected-hidden-target'),
        dcc.Loading(id="loading-1", children=[html.P(id="loading-output-1")], type="cube",fullscreen=True), #one of: 'graph', 'cube', 'circle', 'dot', 'default'
        dbc.Row([
            dbc.Col([
                dbc.Row(selectwhisky, justify='center'),
                dbc.Row(html.Br()),
                dbc.Row(html.H3('Most Similar Whiskies'), justify = 'center'),
                dbc.Row(similarwhiskytable, justify = 'center'),
                dbc.Row(html.Br()),
                ], sm = 12, md = 12, lg = 12, xl = 5, align='start',),

            dbc.Col([
                dbc.Row([
                    html.H3('Selected Whisky'),
                    ], align='center', justify='center'),
                dbc.Row([
                    selected_card,
                    ], align='center', justify='center'),
                dbc.Row(html.Br()),
                ], width='auto', sm = 11, md = 5, lg = 5, xl = 3, align='center'),
            dbc.Col([
                dbc.Row([
                    html.H3('Recommended Whisky'),
                    ], align='center', justify='center'),
                dbc.Row([
                    suggested_card,
                    ], align='center', justify='center'),
                dbc.Row(html.Br()),
                ], width='auto', sm = 11, md = 5, lg = 5, xl = 3, align='center'),
        ], justify='around')
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

# collapse callbacks
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

app.clientside_callback(
    ClientsideFunction('ui', 'replaceWithLinks'),
    Output('selected-hidden-target', 'children'),
    [Input('selected-reviews', 'derived_viewport_data'),
     Input('suggested-reviews', 'derived_viewport_data')]
)

@app.callback([
    Output("selected_review_collapse", "is_open"),
    Output("selected_img_collapse", "is_open")],
    [Input("selected_review_button", "n_clicks")],
    [State("selected_review_collapse", "is_open"),
     State("selected_img_collapse", "is_open")],
)
def toggle_selected_review_collapse(n, rev_open, img_open):
    if n:
        rev_open = not rev_open
        img_open = not img_open
    return rev_open, img_open

@app.callback(
    [Output("suggested_review_collapse", "is_open"),
     Output("suggested_img_collapse", "is_open")],
    [Input("suggested_review_button", "n_clicks")],
    [State("suggested_review_collapse", "is_open"),
     State("suggested_img_collapse", "is_open")],
)
def toggle_suggested_review_collapse(n, rev_open, img_open):
    if n:
        rev_open = not rev_open
        img_open = not img_open
    return rev_open, img_open


# Select row in table
# Update suggested whisky info
@app.callback([
    Output('suggested-name','children'),
    Output('suggested-markdown','children'),
    Output('suggested-reviews', 'columns'),
    Output('suggested-reviews', 'data'),
    Output('suggested-wordcloud','src')
    ],
    [Input('table','derived_viewport_row_ids'),
    Input('table', 'derived_viewport_selected_row_ids')
    ]
    )
def select_row(row_ids, selected_row_ids):
    if row_ids is None and selected_row_ids is None:  
        name = "Not Found"
        markdown = '''**Not found***'''
        imagename = None
        reviewcolumns =[{"name": i, "id": i} for i in df2.columns if i not in ['id']],
        reviewdata=df2.to_dict('records'),
    else:
        if len(selected_row_ids) == 0:
            #'No selection, selecting first!'
            selected_id = row_ids[0]
        elif selected_row_ids[0] not in row_ids:
            #'Invalid selection! Selecting first!'
            selected_id = row_ids[0]
        else:
            #('Already selected, keeping!')
            selected_id = selected_row_ids[0]

        # Grab name and markdown for this whisky
        name, markdown  = getwhiskydesc(selected_id)

        try:
            reviews = getReviews(selected_id)
        except:
            reviewcolumns =[{"name": i, "id": i} for i in df2.columns if i not in ['id']],
            reviewdata=df2.to_dict('records'),
        else:
            reviewcolumns = [{"name":i, "id":i} for i in reviews.columns if i != 'itemnumber']
            reviewdata = reviews.to_dict('records')

        imagename = static_image_route + '{}.png'.format(selected_id)

    return name, markdown, reviewcolumns, reviewdata, imagename

 #When the data in the table changes due to selecting a new whisky, select the top row.
 #update selected row
@app.callback(
    Output('table','selected_rows')
    ,
    [Input('table','data'),
    Input('table','derived_viewport_row_ids')]
    )
def data_updated(data, ids):
    if data is not None and ids is not None:
        # get list of ids in table data (ignoring sorting)
        datalist = [d.get('id') for d in data]
        # get id we actually want which is the first in derived viewport:
        firstid = ids[0]
        if firstid is not None:
            # now find index in datalist
            try:
                rownum = datalist.index(firstid)
            except:
                #data not caught up yet, just use 0
                rownum = 0
        else: rownum = 0
    else:
        rownum = 0

    return [rownum]
            

# Select whisky
# Update table and selected whisky info
@app.callback([
    Output("loading-output-1", "children"),
    Output('selected-name','children'),
    Output('selected-markdown','children'),
    Output('selected-wordcloud','src'),
    Output('selected-reviews', 'columns'),
    Output('selected-reviews', 'data'),
    Output('table','columns'),
    Output('table','data')
    ],
    [Input('input-whisky','value')])
def update_text(value):
    selitemnumber = value
    # selected info
    name, markdown  = getwhiskydesc(value)
    
    #) get suggestions
    suggestions = show_top_similarities(value)
    # Format table values nicely
    suggestions['Similarity']         = suggestions['Similarity']*100
    suggestions['Similarity']         = suggestions['Similarity'].map('{:,.2f}%'.format)
    suggestions['Rating']             = suggestions['Rating'].map('{:,.2f}'.format)
    suggestions['Price']              = suggestions['Price'].map('${:,.2f}'.format)
    suggestions['Rating/$']           = suggestions['Rating/$'].map('{:,.2f}'.format)
    suggestions['ABV']                = suggestions['ABV'].map('{:,.0f}%'.format)
    
    columns=[{"name": i, "id": i} for i in suggestions.columns if i != 'id']
    data=suggestions.to_dict('records')

    imagename = static_image_route + '{}.png'.format(value)

    reviews = getReviews(value)
    reviewcolumns = [{"name":i, "id":i} for i in reviews.columns if i != 'itemnumber']
    reviewdata = reviews.to_dict('records')
    
    return None, name, markdown, imagename, reviewcolumns, reviewdata, columns, data

@app.server.route('{}<image_path>.png'.format(static_image_route))
def serve_image(image_path):
    image_name = '{}.png'.format(image_path)
    return flask.send_from_directory(image_directory, image_name)


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')

