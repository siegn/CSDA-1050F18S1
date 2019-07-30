# LCBO Whisky Similarity Analysis
**Sprint One: Exploratory Data Analysis**
*By Nelson Siegel*

  * [Research Question](#research-question)
  * [Getting Started](#getting-started)
    + [Clone this repository:](#clone-this-repository-)
    + [Setup Virtualenv](#setup-virtualenv)
    + [Launch Jupyter Notebooks](#launch-jupyter-notebooks)
  * [Notebook Descriptions](#notebook-descriptions)
    + [01-clean\_review\_list.ipynb](#01-clean_review_listipynb)
      - [Summary](#summary)
      - [Data Cleaning](#data-cleaning)
      - [Submission IDs](#submission-ids)
      - [Save Data](#save-data)
    + [02-scrape\_reviews.ipynb](#02-scrape_reviewsipynb)
      - [Summary](#summary-1)
      - [Reddit API](#reddit-api)
      - [Scrape reviews](#scrape-reviews)
      - [Save Data](#save-data-1)
    + [03-split\_review\_text.ipynb](#03-split_review_textipynb)
      - [Summary](#summary-2)
      - [Extract Categories](#extract-categories)
      - [Save Data](#save-data-2)
    + [04-scrape\_lcbo\_products.ipynb](#04-scrape_lcbo_productsipynb)
      - [Summary](#summary-3)
      - [LCBO API](#lcbo-api)
      - [Scrape Products](#scrape-products)
      - [Consolidate Files](#consolidate-files)
      - [Clean Data](#clean-data)
      - [Save Data](#save-data-3)
    + [05-whisky\_name\_matchup.ipynb](#05-whisky_name_matchupipynb)
      - [Summary](#summary-4)
      - [Extract Keywords](#extract-keywords)
      - [Bi-Gram Keywords](#bi-gram-keywords)
      - [Extract Keywords Functions](#extract-keywords-functions)
      - [Extract Age](#extract-age)
      - [Fuzzy Matching](#fuzzy-matching)
      - [Filtering](#filtering)
      - [Save Data](#save-data-4)
    + [06-data\_exploration\.ipynb](#06-data_explorationipynb)
      - [Summary](#summary-5)
      - [Convenience Functions for Plots](#convenience-functions-for-plots)
      - [Clean Whisky Styles](#clean-whisky-styles)
      - [Reviews per Whisky](#reviews-per-whisky)
      - [Reviews per User](#reviews-per-user)
      - [Reviews by Rating](#reviews-by-rating)
      - [Top Rated Whiskies](#top-rated-whiskies)
  * [Conclusions](#conclusions)

## Research Question

There are two parts to this research question:

1. Given a whiskey that the user enjoys, how can we tell other whiskeys that they will also enjoy? The method used to determine this will be flavour similarity using document similarity classification on the whisky review descriptions.

2. Based on the prices available for these whiskies at the LCBO, what is the best value purchase the user could choose that they would enjoy the most for the least cost? This will be done by normalizing user reviews versus price.

## Getting Started
Here are instructions to get you set up and running quickly on a GNU/Linux system:
### Clone this repository:
```bash
git clone https://github.com/siegn/CSDA-1050F18S1.git
cd CSDA-1050F18S1
```

### Setup Virtualenv
Virtual environments are recommended to maintain libraries.
Alternatively, an [Anaconda](https://www.anaconda.com/distribution/) install is useful for this, but to get started quickly:
```bash
# create virtual environment
python3 venv whiskyenv
# activate virtual environment
source whiskyenv/bin/activate
# install requirements
pip install -r nsiegel/sprint_1/requirements.txt
```
### Launch Jupyter Notebooks
Jupyter Notebooks will let you view the notebooks in this file. It will have installed when installing the requirements above. 
Start it with:
```bash
# launch Jupyter Notebooks
jupyter notebook
```
Now open a browser and navigate to http://localhost:8000
You can now load the notebooks and follow through the descriptions below:


## Notebook Descriptions

### 01-clean\_review\_list.ipynb

#### Summary

This notebook loads the list of reddit whiskey reviews and performs some cleaning as well as extracting reddit submission IDs so that we can get the review contents from the reddit thread in a later notebook

#### Data Cleaning
The data cleaning completed involves:

- Fixing timestamps
- Fixing ratings
- Adjusting all data types 

#### Submission IDs
The submission IDs from the reddit links are extracted at this point. This is necessary for the next notebook which uses the Reddit API and these submission IDs to collect the review text.

#### Save Data
The data is saved to data/redditwhiskeydatabase.parquet

### 02-scrape\_reviews.ipynb

#### Summary
This notebook uses the reddit API to scrape review text and append them to the reddit review file.

#### Reddit API
To connect to reddit this notebook uses praw, a python wrapper for the reddit api. In order to use it you need to provide a secrets.py file to load in your reddit credentials. This file should have the following fields:

- clientid
- clientsecret
- clientusername
- clientpassword

#### Scrape reviews
The function to scrape reviews uses the praw library, logs in, and pulls the submission ID generated in the first file to go to the submission.

Once the submission is loaded the text in the original submission is combined with all comments by the same poster in the thread as sometimes the reviews are in comments and sometimes in the post.

#### Save Data
The data is saved to data/db_reviews.parquet

### 03-split\_review\_text.ipynb

#### Summary
This notebook splits up the review text into the categories we need: Nose, Taste, Finish. This works by splitting the text into lines and using some regular expressions.

#### Extract Categories
The extraction works by splitting the text into lines and following some regular expressions. It needs to take into account the situation where the text is on the next line so it handles that as well. Because it's a bit slow I've split this into a multiprocess that speeds it up quite a bit.

#### Save Data
The data is saved to data/db_reviews_split.parquet

### 04-scrape\_lcbo\_products.ipynb

#### Summary
This notebook scrapes all product info from the LCBO api. Since the api needs product IDs, this file just tries every ID between 0 and 120 million. As such, with the rate limiting as well, this will take quite a while to run.

#### LCBO API
The LCBO API is not documented anywhere and only takes product IDs, so we need to scrape all Ids blindly the first time.

#### Scrape Products
The scraping uses multiprocessing to make it quicker, but will still get hit by rate limiters on the LCBO end. If time is more limited, using proxies is an option.

The scraping splits up the scrapes into blocks of 10,000 items. This way if the process gets interrupted it can be easily resumed.

#### Consolidate Files

All files scraped are consolidated into one file.

#### Clean Data
The following data cleaning is done:
- Stripping $ from prices
- Splitting productsize into quantity and volume
- Convert N and Y values to True and False
- Fixing datatypes

#### Save Data
The data is saved to data/lcbo_productinfo.parquet,
then whisky products only are selected and saved to data/lcbo_whisky.parquet

### 05-whisky\_name\_matchup.ipynb

#### Summary
This notebook is to combine the reddit reviews with the LCBO product data. The difficulty in doing this comes from differing whisky names. To accomplish the join first we create a list of key phrases and extract them from the names. If whiskies have different key phrases, they do not match. Then we pull out the age of the whisky and compare that as well. Lastly, in terms of cases where there are still duplicates we use a fuzzy matching algorithm and take the highest rank.

#### Extract Keywords
To extract keywords we run all LCBO whiskey names through nltk to find nonenglish words, since we assume these are important.
Next, extra keywords are added and subtracted based on trial and error.

#### Bi-Gram Keywords
Some of the keywords need to match both in order, for example 'Highland Park'. These are entered as tuples.

#### Extract Keywords Functions
In order to speed up the keyword extraction, the function is split into multiple processes.

#### Extract Age
After the datasets are joined on keywords, Age is extracted using regular expressions that collect 2 digit numbers.

#### Fuzzy Matching
Fuzzy matching is calculated using library fuzzywuzzy. The Token Set calculation is used as it was found to be most accurate.

#### Filtering
Next, matches are removed if ages don't match, and if fuzzy matching values are too low.

#### Save Data
Data is saved to data/matches.parquet

### 06-data\_exploration\.ipynb

#### Summary
Now that we have our data set matched up we can do some exploratory analysis to see what we are working with.

#### Convenience Functions for Plots
Many of the things we'll choose for plots are going to be reused so it's nice to get a flexible function here that will:
- Provide different plot types
- Give nice plot sizes
- Format titles and labels
- Output image to a file

#### Clean Whisky Styles
Some of the analysis we do here depends on the Whisky styles provided, but there are some misspellings. This quick function cleans them up for us.

#### Reviews per Whisky
It's important to get an idea of how many reviews we have per Whisky:
https://github.com/siegn/CSDA-1050F18S1/blob/master/nsiegel/sprint_1/images/Histogram%20of%20Reviews%20per%20Whisky.png
![Reviews Per Whisky](https://raw.githubusercontent.com/siegn/CSDA-1050F18S1/master/nsiegel/sprint_1/images/Histogram%20of%20Reviews%20per%20Whisky.png)

And to look at the number of reviews per style:
![Reviews Per Style](https://raw.githubusercontent.com/siegn/CSDA-1050F18S1/master/nsiegel/sprint_1/images/Reviews%20by%20Style.png)

#### Reviews per User
Knowing how many reviews we have per user is very important because it helps us decide if we will use users to recommend whiskies or not. We want to have a significant number of reviews per user for this to work.

![Reviews Per User](https://raw.githubusercontent.com/siegn/CSDA-1050F18S1/master/nsiegel/sprint_1/images/Histogram%20of%20Reviews%20per%20User.png)

There are many users with very few reviews! In fact, 73% of users have less than 5 reviews. This means a user based recommendation system will be very flawed. Due to this I will instead focus of looking at flavour profile similarity.

#### Reviews by Rating
In order to see if our rating is useable, let's take a look at the spread:
![Reviews by Rating](https://raw.githubusercontent.com/siegn/CSDA-1050F18S1/master/nsiegel/sprint_1/images/Histogram%20of%20Reviews%20per%20Rating.png)
These reviews are heavily leaning towards the right. To use these we will want to normalize them first.

#### Top Rated Whiskies
Out of curiosity let's check the top rated whiskies:
![Top Rated Whiskies](https://raw.githubusercontent.com/siegn/CSDA-1050F18S1/master/nsiegel/sprint_1/images/Top%20Rated%20Whiskies.png)

## Conclusions
Based on this analysis there are some clear takeaways:

1. Using other users as a basis for recommendations will not be effective. I will instead focus on flavour similarity and overall rating.

2. User ratings are very heavily skewed to the right. I will normalize these values to get a better comparison.
