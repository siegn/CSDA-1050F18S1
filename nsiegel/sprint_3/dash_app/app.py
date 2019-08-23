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

df = pd.read_parquet('../../sprint_2/data/whisky_tfidf.parquet')
whiskyinfo = pd.read_parquet('../../sprint_2/data/whiskyinfo.parquet')
similarities = pd.read_parquet('../../sprint_2/data/similarities2.parquet')
itemlinks = pd.read_parquet('data/itemlinks.parquet')
reviewlist = pd.read_parquet("data/reviewlist.parquet")

selreviewpage = 0
selreviewpagesize = 10
selitemnumber = 0

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
    keepcolumns = ['id','Name','Style', 'Similarity', 'Rating','Price','Rating Per Dollar','Alcohol Percentage']
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
                          'itemnumber':'id','price':'Price','rating_per_dollar_per_750':'Rating Per Dollar', 'alcoholpercentage':'Alcohol Percentage'},axis=1)
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
        #whisky_selector,
       
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


#cardwidth = 250

selected_card =  dbc.Card(
        [
            dbc.CardHeader('Name', className='card-title', id='selected-name'),
            dbc.CardImg(src=None,top=True, id = 'selected-wordcloud'),
            dbc.CardBody(
                [
                	#html.H4('Name', className='card-title', id='selected-name'),
                    dcc.Markdown(''' #Markdown ''', id ='selected-markdown'),
                    dbc.Button("View Reviews",
                        id="selected_review_button",
                        className="mb-10",
                        color="success"),
		                ] 
            ),
        ],
        #style={"width": "2rem"},
        color = 'info', inverse=True
    #style={"width":"18rem"}
)

suggested_card =  dbc.Card(
        [
            dbc.CardHeader('Name', className='card-title', id='suggested-name'),
            dbc.CardImg(src=None,top=True, id = 'suggested-wordcloud'),
            dbc.CardBody(
                [
                    dcc.Markdown(''' #Markdown ''', id ='suggested-markdown'),
                     dbc.Button("View Reviews",
                        id="suggested_review_button",
                        className="mb-10",
                        color="success"),
                         
                ]
            ),
        ],
        #style={"width": "18rem"},
        color = 'info', inverse=True
   # style={"width":"18rem"}
)

selected_reviews_card =  dbc.Card(
        [
            dbc.CardHeader('Reviews', className='card-title', id='selected-reviews-header'),
            #dbc.CardImg(src=None,top=True, id = 'suggested-wordcloud'),
            dbc.CardBody(
                [
                     dash_table.DataTable(
                                id='selected-reviews',
                                columns=[{"name": i, "id": i} for i in df2.columns if i not in ['id']],
                                data=df2.to_dict('records'),
                                sort_action="native",
                                page_action="native",
                                page_current=0,
                                page_size = 8,
                                #row_selectable='single',
                                style_as_list_view=True,
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': 'Link'},
                                       # 'textAlign': 'left',
                                        'overflow':'clip',
                                        'maxWidth':35
                                    } for c in ['Name', 'Style']
                                    ]
                                    )
                ]
            ),
        ],
        color = 'success', inverse=False
)

suggested_reviews_card =  dbc.Card(
        [
            dbc.CardHeader('Reviews', className='card-title', id='suggested-reviews-header'),
            #dbc.CardImg(src=None,top=True, id = 'suggested-wordcloud'),
            dbc.CardBody(
                [
                     dash_table.DataTable(
                                id='suggested-reviews',
                                columns=[{"name": i, "id": i} for i in df2.columns if i not in ['id']],
                                data=df2.to_dict('records'),
                                sort_action="native",
                                page_action="native",
                                page_current=0,
                                page_size = 8,
                                #row_selectable='single',
                                style_as_list_view=True,
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': 'Link'},
                                       # 'textAlign': 'left',
                                        'overflow':'clip',
                                        'maxWidth':35
                                    } for c in ['Name', 'Style']
                                    ]
                                    )
                ]
            ),
        ],
        color = 'success', inverse=False
)

body = dbc.Container(
    [
    	# Info cards
        dbc.Row(
            [
            dbc.Col([
	        	dbc.Collapse(	
		            dbc.CardDeck([
							dbc.Card(intro_card, color="success", inverse=True),
							dbc.Card(data_card , color="info"   , inverse=True),
							dbc.Card(info_card , color="warning", inverse=True),
			            ]),
						id = 'collapse1'
					)
	            ],align='start')
            ]
        ),
         html.Div(id='selected-hidden-target'),
        dbc.Row(
            [
                dbc.Col(
                    [   
                        dcc.Loading(id="loading-1", children=[html.P(id="loading-output-1")], type="graph",fullscreen=True),
                        html.H3('Selected Whisky', style={'textAlign':'center', 'textSize':25}),
                		selected_card,

                    ], width = 3 
                ),
            	dbc.Col([
				  # Selector
			        dbc.Row([ # Select Whisky
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
			        ],justify='center', align='start'),
                    html.Br(),
			        dbc.Row([ # Similar Table Header
			        	html.Div('   '),
            			html.H3('Most Similar Whiskies', style={'textAlign':'center'}),
			        ], justify = 'center', align='start'),
                    dbc.Row([# Table for similar whiskies
                        dbc.Col([
                            dash_table.DataTable(
                                id='table',
                                columns=[{"name": i, "id": i} for i in df2.columns if i not in ['id']],
                                data=df2.to_dict('records'),
                                sort_action="native",
                                row_selectable='single',
                                selected_rows = [0],
                                #style_as_list_view=True,
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': c},
                                        'textAlign': 'left'
                                    } for c in ['Name', 'Style']
                                ]
                            )
                        ])
        			], justify='center', align='end'),
            		html.Br(),
                    dbc.Row([ # Reviews
            			dbc.Col([
                       
                            dbc.Collapse(
                                selected_reviews_card, 
                                id='selected_review_collapse',
                                ),
                        ]),
                        dbc.Col([
                            dbc.Collapse(
                                suggested_reviews_card,
                                id='suggested_review_collapse',
                                ),
                        ])
            		],justify='around',align='stretch')
        		], width=6,),
                dbc.Col(
                    [
                    	html.H3('Recommended Whisky', style={'textAlign':'center'}),
                        dcc.Loading(id="loading-2", children=[html.P(id="loading-output-2")], type="graph",fullscreen=True),
                        suggested_card,
                    ], width=3
                   
                ),
               # dbc.Col([]),
                
            ] , align='stretch'
        ),
        #dbc.Table.from_dataframe(df, striped=True, bordered=True,hover=True)
        dbc.Row([
        	
        	])
         
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

#@app.callback(
#    Output("collapse2", "is_open"),
#    [Input("collapse-button", "n_clicks")],
#    [State("collapse2", "is_open")],
#)
#def toggle_collapse2(n, is_open):
#    if n:
#        return not is_open
#    return is_open

#server = app.server
#app.layout = html.Div([navbar,body])

app.clientside_callback(
    ClientsideFunction('ui', 'replaceWithLinks'),
    Output('selected-hidden-target', 'children'),
    [Input('selected-reviews', 'derived_viewport_data'),
     Input('suggested-reviews', 'derived_viewport_data')]
)

@app.callback(
    Output("selected_review_collapse", "is_open"),
    [Input("selected_review_button", "n_clicks")],
    [State("selected_review_collapse", "is_open")],
)
def toggle_selected_review_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("suggested_review_collapse", "is_open"),
    [Input("suggested_review_button", "n_clicks")],
    [State("suggested_review_collapse", "is_open")],
)
def toggle_suggested_review_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# Select row in table
# Update suggested whisky info
@app.callback([
    Output('suggested-name','children'),
    Output('suggested-reviews-header', 'children'),
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

    return name, name + ' REVIEWS', markdown, reviewcolumns, reviewdata, imagename

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
    Output('selected-reviews-header', 'children'),
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
    suggestions['Rating Per Dollar']  = suggestions['Rating Per Dollar'].map('{:,.2f}'.format)
    suggestions['Alcohol Percentage'] = suggestions['Alcohol Percentage'].map('{:,.0f}%'.format)
    
    columns=[{"name": i, "id": i} for i in suggestions.columns if i != 'id']
    data=suggestions.to_dict('records')

    imagename = static_image_route + '{}.png'.format(value)

    reviews = getReviews(value)
    reviewcolumns = [{"name":i, "id":i} for i in reviews.columns if i != 'itemnumber']
    reviewdata = reviews.to_dict('records')
    
    return None, name, name + ' REVIEWS', markdown, imagename, reviewcolumns, reviewdata, columns, data

@app.server.route('{}<image_path>.png'.format(static_image_route))
def serve_image(image_path):
    image_name = '{}.png'.format(image_path)
    return flask.send_from_directory(image_directory, image_name)


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')

