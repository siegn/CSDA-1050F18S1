![Whisky Barrels](https://raw.githubusercontent.com/siegn/CSDA-1050F18S1/master/nsiegel/sprint_1/images/woodford_small.png)
# LCBO Whisky Similarity Analysis
**Sprint Two: Modelling**
*By Nelson Siegel*

* [Last Time On LCBO Whisky Similarity Analysis](#last-time-on-lcbo-whisky-similarity-analysis)
* [Notebook Descriptions](#notebook-descriptions)
    + [07-similarity.ipynb](#07-similarityipynb)
    + [08-result_exploration.ipynb](#08-result_explorationipynb)
* [Conclusion](#conclusion)

## Last Time On LCBO Whisky Similarity Analysis

If you have not reviewed Sprint 1, click [here](https://github.com/siegn/CSDA-1050F18S1/tree/master/nsiegel/sprint_1) now! Warning, spoilers for Sprint 1 ahead!

When we left our protagonist last sprint, he had:

1. Cleaned the list of Reddit whisky reviews.
2. Scraped Reddit reviews for review text.
3. Split review text into nose, taste, and finish sections.
4. Scraped product info from LCBO.
5. Matched up LCBO whiskies with Reddit whiskies.
6. Explored the collected data.

## Notebook Descriptions

### 07-similarity.ipynb

This notebook handles calculating which whiskies are similar to each other.

The first step is to aggregate the dataframe to a whisky level. This involves:

Taking the mean of ratings within a whisky.
Concacting all text from within a review.
While doing this we will also do some cleaning on the text and lemmatize it as well so that's its ready for the next step.

Next we will calcualte similarities.

To do this it trains a word2vec model on all of the whisky reviews.

Afterwards it uses word mover distance on all other whiskies to calculate a similarity score.

The output is a table in which each row contains two whisky ids and the similarity between them.

### 08-result_exploration.ipynb

This notebook demonstrates the whisky predictions by comparing an input whisky with the recommended whiskies it outputs. Take a look inside the notebook for some examples.

## Conclusion

I am happy with the results and the recommendations. Even after filtering out region and style names from the text the model recommends similar whiskies that fit the same category.