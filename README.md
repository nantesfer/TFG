# Sentiment analysis based in touristic reviews - README WIP
These are the scripts used for my Degree's Final Project.

## What's the idea behind them?
The idea behind these python scripts is to have an executing chain of scripts that create a MongoDB, gather data from Google Maps' API about touristic places in the island of Tenerife.
With that data stored in the DB, text reviews from users are extracted and analized with several algorithms in order to build a system able to "predict" ratings of those places. 

## What does each Python script do?
The different scripts are meant to do the following things:

- places.py: Creates a new DB and table, uses the Google Maps' API to request a JSON filled with all the information of the place we pass as parameter. Then, the JSON is stored in the DB.
- reviews.py: Created a new table, used to store each of the text reviews of every single place the API returned.
- freeling.py: This script initializes "freeling" (a tool used to get the canonical form and tag of each word in every review) and analyzes each review, word by word, and storing the canonical form of them and its tag in a new table.
