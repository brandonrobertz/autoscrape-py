# Autoscrape

This is an automated scraper of structured data from interactive web pages. The goal is to be able to point this scraper at any site with interactive search forms, pages, etc., and both crawl the site and extract any structured data.

The initial prototype version will use brute force, then machine learning and, finally, reinforcement learning. Note that while we could use other (Scala, Clojure, Go) languages for this, Python was selected because of the large ML and RL ecosystem.

## Setup & Running

You need to have geckodriver installed. You can do that here:

    https://github.com/mozilla/geckodriver/releases

Version 0.20.1 is recommended as of July, 2018.

Then set up your python virtual environment (Python 3.6 required) and install the pip dependencies:

    pip install -r requirements.txt
    # If you're developing on the scraper
    pip install -r requirements.dev.txt

You can run the example script like so:

    ./example.py --loglevel DEBUG --maxdepth 10 SITE_HERE

That will just do a depth-first click-only crawl of an entire website. It will not interact with forms or POST data.
