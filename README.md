# Autoscrape

![Artificial Informer Labs](https://github.com/brandonrobertz/autoscrape-py/blob/master/images/ai.png)

A project of [Artificial Informer Labs](https://artificialinformer.com).

This is an automated scraper of structured data from interactive web pages. You point this scraper at a site and it will be crawled, searched for forms and structured data will be extracted. No brittle, site-specific programming necessary.

*This is a work in progress.* The initial prototype version uses brute force with a set of configuration options. Machine learning and, finally, reinforcement learning models are being developed.

This is an implementation of the web scraping framework described in the upcoming paper, _Robust Web Scraping in the Public Interest with AutoScrape_ in [Proceedings of Computation + Journalism Symposium 2019](http://cplusj.org/).

## Setup & Dependencies

You need to have geckodriver installed. You can do that here:

    https://github.com/mozilla/geckodriver/releases

Version 0.23.0 is recommended as of November, 2018.

If you prefer to use Chrome, you will need the ChromeDriver (we've tested using v2.41). It can be found in your distribution's package manager or here:

    https://sites.google.com/a/chromium.org/chromedriver/downloads

Next you need to set up your python virtual environment (Python 3.6 required) and install the Python dependencies:

    pip install -r requirements.txt
    # If you're developing on the scraper
    pip install -r requirements.dev.txt

## Running

### Environment Test Crawler

You can run a test to ensure your webdriver is set up correctly by running the `test` crawler:

    ./scrape.py --show-browser [SITE_URL]

The `test` crawler will just do a depth-first click-only crawl of an entire website. It will not interact with forms or POST data. Data will be saved to `./autoscrape-data/` (the default output directory).

### Manual Config-Based Scraper

Autoscrape has a manually controlled mode, similar to wget, except this
uses interactive capabilities and can input data to search forms, follow
"next page"-type buttons, etc.  This functionality can be used either
as a standalone crawler/scraper or as a method to build a training set
for the automated scrapers.

Autoscrape manual-mode full options:

```
AUTOSCRAPE - Interactively crawl, find searchable forms,
input data to them and scrape data on the results, from an
initial BASEURL.

Usage:
    scrape.py [options] BASEURL

Crawl-Specific Options:
    --maxdepth DEPTH
        Maximum depth to crawl a site (in search of form
        if the option "--form-match [string]" is specified,
        see below). [default: 10]

    --leave-host
        By default, autoscrape will not leave the host given
        in the BASEURL. This option lets the scraper leave
        the host.

    --link-priority SORT_STRING
        A string to sort the links by. In this case, any link
        containing "SORT_STRING" will be clicked before any other
        links.

    --ignore-links MATCH_STRING
        This option can be used to remove any links matching
        MATCH_STRING (can be a regex or just a string match)
        from consideration for clicking.

Interactive Form Search Options:
    --form-match SEARCH_STRING
        The crawler will identify a form to search/scrape if it
        contains the specified string. If matched, it will be
        interactively scraped using the below instructions.

    --input INPUT_DESCRIPTION
        Interactive search descriptor. This describes how to
        interact with a matched form. The inputs are
        described in the following format:

        "c:0:True,i:0:atext,s:1:France:d:0:01-20-1991"

        A single-input type can be one of three types:
        checkbox ("c"), input box ("i"), option select
        ("s"), and date inputs ("d", with inputs in the
        "MM-DD-YYYY" format). The type is separated by a
        colon, and the input index position is next. (Each
        input type has its own list, so a form with one
        input, one checkbox, and one option select, will all
        be at index 0.) The final command, sepearated by
        another colon, describes what to do with the input.

        Multiple inputs are separated by a comma, so you can
        interact with multiple inputs before submitting the
        form.

        To illustrate this, the above command does the following:
            - first input checkbox is checked (uncheck is False)
            - first input box gets filled with the string "first"
            - second select input gets the "France" option chosen
            - first date input gets set to Jan 20, 1991

    --next-match NEXT_BTN_STRING
        A string to match a "next" button with, after
        searching a form.  The scraper will continue to
        click "next" buttons after a search until no matches
        are found, unless limited by the --formdepth option
        (see below). [default: next page]

    --formdepth DEPTH
        How deep the scraper will iterate, by clicking
        "next" buttons. Zero means infinite depth.
        [default: 0]

    --form-submit-natural-click
        Some webpages make clicking a link element difficult
        due to JavaScript onClick events. In cases where a
        click does nothing, you can use this option to get
        the scraper to emulate a mouse click over the link's
        poition on the page, activating any higher level JS
        interactions.

    --form-submit-wait SECONDS
        How many seconds to force wait after a submit to a form.
        This should be used in cases where the builtin
        wait-for-page-load isn't working properly (JS-heavy
        pages, etc). [default: 5]

Webdriver-Specific and General Options:
    --load-images
        By default, images on a page will not be fetched.
        This speeds up scrapes on sites and lowers bandwidth
        needs. This option fetches all images on a page.

    --show-browser
        By default, we hide the browser during operation.
        This option displays a browser window, mostly
        for debugging purposes.

    --driver DRIVER
        Which browser to use. Current support for "Firefox",
        "Chrome", and "remote". [default: Firefox]

    --remote-hub URI
        If using "remote" driver, specify the hub URI to
        connect to. Needs the proto, address, port, and path.
        [default: http://localhost:4444/wd/hub]

    --loglevel LEVEL
        Loglevel, note that DEBUG is extremely verbose.
        [default: INFO]

Data Saving Options:
    --output-data-dir OUTPUT_DATA_DIR
        If specified, this indicates where to save pages during a
        crawl. This directory will be created if it does not
        currently exist.  This directory will have several
        sub-directories that contain the different types of pages
        found (i.e., search_pages, data_pages, screenshots).
        [default: autoscrape-data]

    --keep-filename
        By default, we hash the files in a scrape in order to
        account for dynamic content under a single-page app
        (SPA) website implmentation. This option will force
        the scraper to retain the original filename, from the
        URL when saving scrape data.

    --save-screenshots
        This option makes the scraper save screenshots of each
        page, interaction, and search. Screenshots will be
        saved to the screenshots folder of the output dir.

    --save-graph
        This option allows the scraper to build a directed graph
        of the entire scrape and will save it to the "graph"
        subdirectory under the output dir. The output file
        is a timestamped networkx pickled graph.

EXAMPLES

./scrape.py \
  --form-match "first name" \
  --input "i:0:firstname,i:1:lastname" \
  --next-match "next page" \
  --output-data-dir "firstname_lastname_scrape" \
  [BASEURL]

In the above example, the scraper will crawl until it finds a form
that contains the text "first name". At that point, it will type
"firstname" in the first text input box and "lastname" into the second
input box, then submits the form. Then it will wait for the submission
to be completed/loaded and will continue clicking on buttons/links
containing "next page" until there are no more. All data found during
the scrape will be saved to the ./firstname_lastname_scrape directory.
```

## Fully Automated Scrapers, Data & ML Models

![Web code embeddings](https://github.com/brandonrobertz/autoscrape-py/blob/master/images/code_embeddings.png)

NOTE: This is extremely experimental and is very much under active development.

`autoscrape-ml` requires two separate embedding models: a HTML/JS character embeddings and plain word embeddings. (You can check `training_data/embeddings/` for more information about the specifics.)

We trained our HTML & JavaScript code character-level language model from 61G of StackOverflow comment data. We will make the embeddings public in the near future. Until then, you need to train them yourself using something like word2vec on pre-split character data.

For a generic language model, we're using the GloVe [300D, 840B token Common Crawl embeddings](https://github.com/stanfordnlp/GloVe#download-pre-trained-word-vectors), which is freely available online.

We can gather training data with the `manual-control` scraper, using this
configuration optionset:

    ./scrape.py --loglevel DEBUG --maxdepth 2 \
        --output-data_dir ./training_data/pages/html/ \
        --form-match "first name" \
        --input "i:0:a;i:0:b;i:0:c" --formdepth 2 \
        --next-match "next page" \
        [SITE_URL]

The above will find, from [SITE_URL], interactive forms containing the
text "first name", will input the characters a, b, then c, into the form,
and will click buttons containing "next page" until it's two layers
deep. All training data derived from this crawl will be stored in the
directory `./training_data/pages/html/`.

Once we have all our embeddings, we need to take our example training web pages and vectorize them:

    ./vectorize_data.py --loglevel DEBUG \
        --html_embeddings training_data/webcode.300d.txt \
        --word_embeddings training_data/glove.840B.300d.txt \
        --output_file training_data/page_data.pickle \
        ./training_data/hand_gathered_page_data/html/


The resulting `page_data.pickle` will have `X` and `y` attributes.

Once you have training data vectorized, you can train a supervised
classification model using the `train.py` script:

    ./train.py --data training_data/page_data.pickle \
        --output training_data/page_data_kNN.model.pickle \
        --model kNN

The resulting model will be saved, in the above example, to
`training_data/page_data_kNN.model.pickle` which can be loaded and ran by
`autoscraper-ml`.



