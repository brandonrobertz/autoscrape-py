# Autoscrape

![Artificial Informer Labs](https://github.com/brandonrobertz/autoscrape-py/blob/master/images/ai.png)

A project of [Artificial Informer Labs](https://artificialinformer.com).

This is an automated scraper of structured data from interactive web pages. You point this scraper at a site and it will be crawled, searched for forms and structured data will be extracted. No brittle, site-specific programming necessary.

*This is a work in progress.* The initial prototype version uses brute force with a set of configuration options. Machine learning and, finally, reinforcement learning models are being developed.

## Setup & Dependencies

You need to have geckodriver installed. You can do that here:

    https://github.com/mozilla/geckodriver/releases

Version 0.20.1 is recommended as of July, 2018.

Then set up your python virtual environment (Python 3.6 required) and install the pip dependencies:

    pip install -r requirements.txt
    # If you're developing on the scraper
    pip install -r requirements.dev.txt

## Running

### Environment Test Crawler

You can run a test to ensure your webdriver is set up correctly by running the `test` crawler:

    ./scrape.py --loglevel DEBUG --maxdepth 10 test [SITE_URL]

The `test` crawler will just do a depth-first click-only crawl of an entire website. It will not interact with forms or POST data.

### Manual Config-Based Scraper

There's also the `manual-control` scraper, which runs based on some
command line options to control crawling for search forms and
interacting with them. Currently, the config-based iterating model can
be ran like this:

    ./scrape.py \
        --loglevel DEBUG
        --maxdepth 10 \
        --next_match "next page" \
        --form_match "first name" \
        manual-control [SITE_URL]

In the above example, the scraper will crawl until it finds a form
that contains the text "first name", then begins to scrape it, clicking
on buttons/links containing "next page" until there are no more.

### Fully Automated Scrapers

More advanced scrapers are currently under active development.

The experimental machine learning-based `autoscraper-ml` crawler-scraper can be ran with this set of options:

    ./scrape.py autoscrape-ml \
        --loglevel DEBUG \
        --maxdepth 10 \
        --html_embeddings ./training_data/embeddings/webcode.300d.txt \
        --word_embeddings ./training_data/embeddings/glove.840B.300d.txt \
        [SITE_URL]

`autoscrape-ml` requires pre-trained HTML/JS character embeddings and word embeddings. See `training_data/embeddings/` for more information about that. We will make the embeddings public in the near future.

For a generic language model, we're using the GloVe [300D, 840B token Common Crawl embeddings](https://github.com/stanfordnlp/GloVe#download-pre-trained-word-vectors), which are available online.

You also need the classifier to be trained on a labeled web page dataset. More
information will be made available soon.

## Model Data

![Web code embeddings](https://github.com/brandonrobertz/autoscrape-py/blob/master/images/code_embeddings.png)

Visualization of our trained HTML & JavaScript code character-level language
model from 61G of StackOverflow data.

Once we have all our embeddings and training page data downloaded, we can
vectorize it using this convenience script:

    ./vectorize_data.py --loglevel DEBUG \
        --html_embeddings training_data/embeddings/webcode.300d.txt \
        --word_embeddings  training_data/embeddings/glove.840B.300d.txt \
        --output_file training_data/page_data.pickle \
        training_data/pages/html/

The resulting `page_data.pickle` will be a class with `X` and `y` attributes.

Once you have training data vectorized, you can train a model using the
`train.py` script:

    ./train.py --data training_data/page_data.pickle \
        --output training_data/page_data_kNN.model.pickle \
        --model kNN

The resulting model will be saved, in the above example, to
`training_data/page_data_kNN.model.pickle` which can be loaded and ran by 
`autoscraper-ml`.

