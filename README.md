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
        [BASEURL]

Full listing of options

    scrape.py [OPTION]... BASEURL
     
        Interactively crawl, find searchable forms, input data to them
        and scrape the data on a webpage, from an initial BASEURL.
     
    Crawl-specific options
        --maxdepth 10
            Maximum depth to crawl a site (in search of form if the
            option "--form-match [string]" is specified, see below).
        
        --leave-host False
            Whether the crawl can leave the base URL host.
        
        --link-priority "search"
            A string to sort the links by. In this case, any link
            containing "search" will be clicked before any other links.
        
    Interactive form search options
        --form-match "Search Form"
            The crawler will identify a form to search/scrape if it
            contains the specified string. (In this case it will identify
            a form containing the text "Search Form".) If matched, it will be
            interactively scraped using the below instructions.
        
        --input "c:0:True,i:0:atext,s:1:France"
            Interactive search descriptor. This describes how to interact with
            a matched form. The inputs are described in the following format:
            a single-input type can be one of three types: checkbox ("c"),
            input box ("i"), and option select ("s"). The type is separated
            by a colon, and the input index position is next. (Each input
            type has its own list, so a form with one input, one checkbox,
            and one option select, will all be at index 0.) The final command,
            sepearated by another colon, describes what to do with the input.
                Multiple inputs are separated by a comma, so you can interact
            with multiple inputs before submitting the form.
            
            To illustrate this, the above command does the following:
                - the first input checkbox is checked (uncheck is False)
                - the first input box gets filled with the string "first"
                - the second select input gets the "France" option chosen
        
        --next-match "next page"
            A string to match a "next" button with, after searching a form.
            The scraper will continue to click "next" buttons after a search
            until no matches are found, unless limited by the --formdepth
            option (see below).
       
        --formdepth 0
            How deep the scraper will iterate, by clicking "next" buttons.
        
        --form-submit-natural-click False
            Some webpages make clicking a link element difficult due to
            JavaScript onClick events. In cases where a click does nothing,
            you can use this option to get the scraper to emulate a mouse
            click over the link's poition on the page, activating any higher
            level JS interactions.
        
        --form-submit-wait 5
            How many seconds to force wait after a submit to a form.
            This should be used in cases where the builtin
            wait-for-page-load isn't working properly (JS-heavy pages, etc).
     
    Webdriver-specific and general settings
        --load-images False
            By default, images on a page will not be fetched. This speeds
            up scrapes on sites and lowers bandwidth needs.
        
        --headless True
            This hides the browser while it is bring automatically ran. If
            you need to debug a scrape, set this to False.
        
        --driver "Firefox"
            Which browser to use. Current support for "Firefox" and "Chrome".
         
        --loglevel "INFO"
             Loglevel, note that DEBUG is extremely verbose
     
    Data saving
        --output-data-dir "scrape_data"
            Where to save pages during a crawl. This directory will
            be created if it does not currently exist. This directory
            will have several sub-directories that contain the different
            types of pages found (i.e., search_pages, data_pages, screenshots).

## Data & ML Models

![Web code embeddings](https://github.com/brandonrobertz/autoscrape-py/blob/master/images/code_embeddings.png)

`autoscrape-ml` requires two separate embedding models: a HTML/JS character embeddings and plain word embeddings. (You can check `training_data/embeddings/` for more information about the specifics.)

We trained our HTML & JavaScript code character-level language model from 61G of StackOverflow comment data. We will make the embeddings public in the near future. Until then, you need to train them yourself using something like word2vec on pre-split character data.

For a generic language model, we're using the GloVe [300D, 840B token Common Crawl embeddings](https://github.com/stanfordnlp/GloVe#download-pre-trained-word-vectors), which is freely available online.

We can gather training data with the `manual-control` scraper, using this
configuration optionset:

    ./scrape.py --loglevel DEBUG --maxdepth 2 \
        manual-control \
        --output_data_dir ./training_data/pages/html/ \
        --form_input_range abc --input_minlength 1 \
        --formdepth 2 \
        -- next_match "next page" --form_match "first name"
        [SITE_URL]

The above will find, from [SITE_URL], interactive forms containing the
text "first name", will input the characters a, b, then c (single
length permutation, from the `input_minlength` option), into the form,
and will click buttons containing "next page" until it's two layers
deep. All training data derived from this crawl will be stored in the
directory `./training_data/pages/html/`.

Once we have all our embeddings, we need to take our example training web pages
and vectorize them:

    ./vectorize_data.py --loglevel DEBUG \
        --html_embeddings training_data/embeddings/webcode.300d.txt \
        --word_embeddings  training_data/embeddings/glove.840B.300d.txt \
        --output_file training_data/page_data.pickle \
        training_data/pages/html/

The resulting `page_data.pickle` will have `X` and `y` attributes.

Once you have training data vectorized, you can train a supervised
classification model using the `train.py` script:

    ./train.py --data training_data/page_data.pickle \
        --output training_data/page_data_kNN.model.pickle \
        --model kNN

The resulting model will be saved, in the above example, to
`training_data/page_data_kNN.model.pickle` which can be loaded and ran by
`autoscraper-ml`.



