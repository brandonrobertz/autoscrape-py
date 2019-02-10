# Autoscrape

![Artificial Informer Labs](https://github.com/brandonrobertz/autoscrape-py/blob/master/images/ai.png)

A project of [Artificial Informer Labs](https://artificialinformer.com).

AutoScrape is an automated scraper of structured data from interactive web pages. You point this scraper at a site and it will be crawled, searched for forms and structured data can then be extracted. No brittle, site-specific programming necessary.

This is an implementation of the web scraping framework described in the paper, _Robust Web Scraping in the Public Interest with AutoScrape_ in [Proceedings of Computation + Journalism Symposium 2019](http://cplusj.org/).

Currently there are two methods of running AutoScrape:
- as a local CLI python script
- as a containerized system via the API

Installation and running instructions are provided for both below.

[![Quickstart Video](https://github.com/brandonrobertz/autoscrape-py/blob/master/images/quickstart-video.png)](https://www.youtube.com/watch?v=D0Mchcf6THE)

## Setup for Standalone Local CLI

### External Dependencies

You need to have geckodriver installed. You can do that here:

    https://github.com/mozilla/geckodriver/releases

Version 0.23.0 is recommended as of November, 2018 along with Firefox version  >= 0.63.

If you prefer to use Chrome, you will need the ChromeDriver (we've tested using v2.41). It can be found in your distribution's package manager or here:

    https://sites.google.com/a/chromium.org/chromedriver/downloads

Installing the remaining Python dependencies can be done using pip or pipenv:

### Pip Install Method

Next you need to set up your python virtual environment (Python 3.6 required) and install the Python dependencies:

    pip install -r requirements.txt

### Pipenv Method

AutoScrape also supports pipenv. You can install required dependencies by
running:

    pipenv install

## Running Standalone Scraper

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
        if the option --form-match STRING is specified,
        see below). Zero mean no limit. [default: 0]

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

    --only-links MATCH_STRING
        This option whitelists links which ought to be clicked.
        All other links will be ignored.

Interactive Form Search Options:
    --form-match SEARCH_STRING
        The crawler will identify a form to search/scrape if it
        contains the specified string. If matched, it will be
        interactively scraped using the below instructions.

    --input INPUT_DESCRIPTION
        Interactive search descriptor. This describes how to
        interact with a matched form. The inputs are
        described in the following format:

        "c:0:True,i:0:atext,s:1:France:d:0:1991-01-20"

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
    --output DIRECTORY_OR_URL
        If specified, this indicates where to save pages during a
        crawl. This directory will be created if it does not
        currently exist.  This directory will have several
        sub-directories that contain the different types of pages
        found (i.e., search_pages, data_pages, screenshots).
        This can also accept a URL (i.e., http://localhost:5000/files)
        and AutoScrape will POST to that endpoint with each
        file scraped.
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

    --disable-style-saving
        By default, AutoScrape saves the stylesheets associated
        with a scraped page. To save storage, you can disable this
        functionality by using this option.

EXAMPLES

./scrape.py \
  --form-match "first name" \
  --input "i:0:firstname,i:1:lastname" \
  --next-match "next page" \
  --output "firstname_lastname_scrape" \
  [BASEURL]

In the above example, the scraper will crawl until it finds a form
that contains the text "first name". At that point, it will type
"firstname" in the first text input box and "lastname" into the second
input box, then submits the form. Then it will wait for the submission
to be completed/loaded and will continue clicking on buttons/links
containing "next page" until there are no more. All data found during
the scrape will be saved to the ./firstname_lastname_scrape directory.
```

## Setup Containerized API Version

AutoScrape can also be ran as a containerized cluster environment, where
scrapes can be triggered and stopped via API calls and data can
be streamed to this server.

To run this you need [docker-ce](https://docs.docker.com/install/#server)
and [docker-compose](https://docs.docker.com/compose/install/). Once you
have these dependencies installed, simply run:

    docker-compose build --pull
    docker-compose up -t0 --abort-on-container-exit

This will build the containers and launch a API server
running on local port 5000. More information about the API calls
can be found in `autoscrape-server.py`.

If you have make installed, you can simply run `make start`.

NOTE: This is a work in progress prototype that will likely
be removed once AutoScrape is integrated into
[CJ Workbench](http://workbenchdata.com).

