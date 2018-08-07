# Autoscrape

This is an automated scraper of structured data from interactive web pages. The goal is to be able to point this scraper at any site with interactive search forms, pages, etc., and both crawl the site and extract any structured data.

The initial prototype version will use brute force, then machine learning and, finally, reinforcement learning. Note that while we could use other (Scala, Clojure, Go) languages for this, Python was selected because of the large ML and RL ecosystem.

![Web code embeddings](https://github.com/brandonrobertz/autoscrape-py/blob/master/training_data/images/code_embeddings.png)

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

More advanced models are under development. Currently, the config-based iterating model can be ran like this:

    ./example.py --scraper manual-control \
        --loglevel DEBUG --maxdepth 10 \
        [SITE_URL]

And the experimental ML-based autoscraper can be ran with:

    ./example.py --scraper autoscrape-ml \
        --loglevel DEBUG --maxdepth 10 \
        --html_embeddings ./training_data/embeddings/webcode.300d.embeddings \
        --word_embeddings ./training_data/embeddings/glove.840B.300d.txt \
        [SITE HERE]

This model requires pre-trained HTML/JS character embeddings and word embeddings. We're using a custom character embedding for the web code model and the [300D, 840B token Common Crawl embeddings](https://github.com/stanfordnlp/GloVe#download-pre-trained-word-vectors) for the language model. You also need the classifier to be trained on a labeled web page dataset.

