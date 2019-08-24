![Whisky Barrels](https://raw.githubusercontent.com/siegn/CSDA-1050F18S1/master/nsiegel/sprint_1/images/woodford_small.png)
# LCBO Whisky Similarity Analysis
**Overview**
*By Nelson Siegel*

  * [App](#app)
  * [Introduction](#introduction)
  * [Repository Structure](#repository-structure)
    + [[Sprint 1: Data Gathering and Analysis](https://github.com/siegn/CSDA-1050F18S1/tree/master/nsiegel/sprint_1)](#-sprint-1--data-gathering-and-analysis--https---githubcom-siegn-csda-1050f18s1-tree-master-nsiegel-sprint-1-)
    + [[Sprint 2: Modelling](https://github.com/siegn/CSDA-1050F18S1/tree/master/nsiegel/sprint_2)](#-sprint-2--modelling--https---githubcom-siegn-csda-1050f18s1-tree-master-nsiegel-sprint-2-)
    + [[Sprint 3: App](https://github.com/siegn/CSDA-1050F18S1/tree/master/nsiegel/sprint_3)](#-sprint-3--app--https---githubcom-siegn-csda-1050f18s1-tree-master-nsiegel-sprint-3-)
  * [Software Requirements](#software-requirements)
    + [Clone this Repository](#clone-this-repository)
    + [Setup Virtualenv](#setup-virtualenv)
    + [Launch Jupyter Notebooks](#launch-jupyter-notebooks)

## App

You can view the LCBO Whisky Similarity Analysis App [here](https://lcbo-whisky-similarity.herokuapp.com/).

## Introduction

The intent of this repository was to answer the following two questions:

1. Given a whiskey that the user enjoys, how can we tell other whiskeys they will enjoy? The method used to determine is flavour similarity Word Mover Distance with Word2Vec on whisky review text.

2. Based on the prices available for these whiskies at the LCBO, what is the best value purchase the user could choose that they would enjoy the most for the least cost? To do this a Rating per Price is displayed.

The results is a Dash app used to review the suggestions.

## Repository Structure

Inside the repository you can find Jupyter notebooks describing the techniques used, as well as the source code for the Dash app.

The repository is broken down into subsections:

### [Sprint 1: Data Gathering and Analysis](https://github.com/siegn/CSDA-1050F18S1/tree/master/nsiegel/sprint_1) 

This section contains information on where and how the data was gathered as well as some initial data analysis.

### [Sprint 2: Modelling](https://github.com/siegn/CSDA-1050F18S1/tree/master/nsiegel/sprint_2)

Sprint 2 contains the modelling, in which the datasets were matched up, then a Word2Vec model was trained and a similarity analysis completed using Word Mover Distance.

### [Sprint 3: App](https://github.com/siegn/CSDA-1050F18S1/tree/master/nsiegel/sprint_3)

Sprint 3 contains a notebook used to prep data for the app, as well as pregenerate wordclouds for each whisky. Included in this folder is the source code for the Dash app itself.

## Software Requirements

This was developed on a Linux system but should work on Windows as well as long as you have Python and the required libraries. Here are some instructions to get you set up and running quickly on a Linux system:

### Clone this Repository
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
