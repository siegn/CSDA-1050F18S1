# LCBO Whisky Recommondation Algorithm
**Sprint One: Exploratory Data Analysis**

## Research Question

There are two parts to this research question:

1. Given a whiskey that the user enjoys, how can we tell other whiskeys that they will also enjoy?

2. Based on the prices available for these whiskies at the LCBO, what is the best value purchase the user could choose that they would enjoy the most for the least cost?

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

### 03-scrape\_lcbo\_products.ipynb

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

### 04-whisky\_name\_matchup.ipynb

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
