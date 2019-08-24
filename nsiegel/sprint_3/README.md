![Whisky Barrels](https://raw.githubusercontent.com/siegn/CSDA-1050F18S1/master/nsiegel/sprint_1/images/woodford_small.png)
# LCBO Whisky Similarity Analysis
**Sprint Three: App**
*By Nelson Siegel*
  * [Last Time On LCBO Whisky Similarity Analysis](#last-time-on-lcbo-whisky-similarity-analysis)
  * [Goal of Sprint](#goal-of-sprint)
  * [Notebook Description](#notebook-description)
    + [10_prepare_app_data.ipynb](#10-prepare-app-dataipynb)
      - [WordCloud Images](#wordcloud-images)
      - [LCBO Links](#lcbo-links)
      - [Review Links](#review-links)
  * [Dash App](#dash-app)
    + [App Development](#app-development)
      - [Clientside Callbacks](#clientside-callbacks)
      - [App Data](#app-data)
      - [App Functions](#app-functions)
    + [App Deployment](#app-deployment)
    + [Viewing App](#viewing-app)
  * [Conclusion](#conclusion)
## Last Time On LCBO Whisky Similarity Analysis

If you have not reviewed Sprint 1, and 2, you can do so here:
* [Sprint 1: Data Gathering and Analysis](https://github.com/siegn/CSDA-1050F18S1/tree/master/nsiegel/sprint_1) 
* [Sprint 2: Modelling](https://github.com/siegn/CSDA-1050F18S1/tree/master/nsiegel/sprint_2)

*Warning, spoilers for Sprint 1 and 2 ahead!*

When we left our protagonist last sprint, he had:

1. Cleaned the list of Reddit whisky reviews.
2. Scraped Reddit reviews for review text.
3. Split review text into nose, taste, and finish sections.
4. Scraped product info from LCBO.
5. Matched up LCBO whiskies with Reddit whiskies.
6. Explored the collected data.
7. Trained a Word2Vec model on reveiew data.
8. Calculated similarities between whiskies using Word Mover Distance and the trained Word2Vec model.
9. Evaluated similarity results.

## Goal of Sprint
The goal of this sprint was to develop a more effective way of interacting with the data that can be exposed to users. To do this I developed a Dash App. The first step was to prep that data for the app using python Notebooks.

## Notebook Description

### 10_prepare_app_data.ipynb
To create the dash app, I need some specific formats of data that it can load in so it doesn't need to calculate everything on the fly. This notebook generates those datasets. Details follow:

#### WordCloud Images
Wordclouds give a rough idea of the falvours in a whisky so it's nice to be able to show this to users.
To generate wordcloud images the WordCloud library is used. These images are saved to dash_app/wordclouds folder so the dash app can access them.

#### LCBO Links
Surprisingly, the LCBO api doesn't actually give us links to their main page. To get them instead I'll make a search on their site and grab the result.

To speed up the link collection I split up the dataframe into a number of chunk equal to processors available on the machine. In the end this ran in about 10 seconds so I probably didn't need to bother.

This data is saved to the dash_app/data folder for later use by the app.

#### Review Links
To show users the links to reddit reviews, it's pretty easy since we already have the data. I'll just take out some columns that aren't needed and pre-sort.

This data is saved into the dash_app/data folder as well.

## Dash App

### App Development
Dash apps are written in python. The code for my app is available [here](https://github.com/siegn/CSDA-1050F18S1/blob/master/nsiegel/sprint_3/dash_app/app.py)

Some things that made the app development a lot easier are:
* [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) : These make layout way easier and allow it to adapt to different screen dimensions as well.
* [Dash Datatable](https://dash.plot.ly/datatable) : Makes working with tables in Dash a lot easier and effective.
* [Clientside Callbacks](https://community.plot.ly/t/dash-0-41-0-released/22131) : A relatively new feature in Dash that allowed me to overcome one of the limitations of the Dash Datatable, that it could not include clickable links. More details below.

#### Clientside Callbacks
Although extremely helpful, the Dash DataTable does not allow clickable links inside. Since I needed these for the reviews, I looked for a way to include it. By using clientside callbacks, I was able to implement javascript code that replaces links in tables with clickable links.
The javascript code loaded by the app is available [here](https://github.com/siegn/CSDA-1050F18S1/blob/master/nsiegel/sprint_3/dash_app/assets/app-ui.js).

#### App Data
The data needed to run the app includes the following, all available inside the dash_app/data folder:
* whisky_tfidf.parquet : Basic whisky dataframe used to generate selector.
* whiskyinfo.parquet : Details about a whisky such as price, ABV, etc.
* similarities.parquet : Table showing every whisky's similarity to every other whisky.
* itemlinks.parquet : Table that includes an LCBO link for each whisky.
* reviewlist.parquet : Table that includes reddit review information and links for each whisky.

#### App Functions
To allow the interface to work with the data, some functions are defined:
* getReviews : Given an itemnumber, returns all reddit review information to populate a table.
* getLCBOLink : Given an itemnumber returns a link to the LCBO website.
* show_top_similarities : Returns table data of top n similar whiskies to selected itemnumber.
* getwhiskydesc : Given an itemnumber, returns all info to display to the user in a markdown format.

### App Deployment
The app is then deployed onto heroku, which is a free host for Dash apps.

To do this, instructions were followed from [here](https://dash.plot.ly/deployment).

### Viewing App
The app can be viewed [here](https://lcbo-whisky-similarity.herokuapp.com/).

## Conclusion

I am happy with the results and the recommendations given, as well as the app interface. Exploring the data through the app reveals a few issues with data cleaning that I would like to address, such as a couple of whiskies appearing twice, or some reviews being matched to other whiskies.

I would also like to improve on the process by implementing a database and having scripts run incrementally to capture new reviews and products.