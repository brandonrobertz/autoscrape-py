Autoscrape
==========

.. image:: https://pypip.in/v/autoscrape/badge.svg
        :target: https://pypi.python.org/pypi/autoscrape/

.. image:: https://pypip.in/license/autoscrape/badge.svg
        :target: https://pypi.python.org/pypi/autoscrape/


.. figure:: https://github.com/brandonrobertz/autoscrape-py/blob/master/images/ai.png
   :alt: Artificial Informer Labs

A project of `Artificial Informer Labs <https://artificialinformer.com>`__.

AutoScrape is an automated scraper of structured data from interactive
web pages. You point this scraper at a site and it will be crawled,
searched for forms and structured data can then be extracted. No
brittle, site-specific programming necessary.

This is an implementation of the web scraping framework described in the
paper, `Robust Web Scraping in the Public Interest with AutoScrape <https://bxroberts.org/files/autoscrape.pdf>`__ and presented at
`Computation + Journalism Symposium 2019 <http://cplusj.org/>`__.

Currently there are two methods of running AutoScrape:

- as a local CLI python script
- as a containerized system via the API and Web UI

Installation and running instructions are provided for both below.

|Quickstart Video|

Quickstart
----------

Two ways, easiest first.

::

    pip install autoscrape
    autoscrape -h

Or:

::

    git clone https://github.com/brandonrobertz/autoscrape-py
    cd autoscrape-py/
    python setup.py install
    autoscrape -h

Either way, you can now use ``autoscrape`` from the command line.

Usage Examples
--------------

Here are some straightforward use cases for AutoScrape and how you'd use
the CLI tool to execute them. These, of course, assume you have the
dependencies installed.

Crawler Backends
~~~~~~~~~~~~~~~~

There are two backends available for driving AutoScrape: ``selenium``
and ``requests``. The ``requests`` is based on the Python requests
library and is only capable of crawling sites. For any interaction with
forms or JavaScript powered buttons, you'll need to use the ``selenium``
backend.

You can control the backened with the ``--backend`` option:

::

    autoscrape \
      --backend requests \
      --output requests_crawled_site \
      'https://some.page/to-crawl'

Crawl
~~~~~

Crawl an entire website, saving all HTML and stylesheets (no
screenshots):

::

    autoscrape \
      --backend requests \
      --maxdepth -1 \
      --output crawled_site \
      'https://some.page/to-crawl'

Archive Page (Screenshot & Code)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Archive a single webpage, both code and full-content screenshot (PNG),
for future reference:

::

    autoscrape \
      --backend selenium \
      --full-page-screenshots \
      --load-images --maxdepth 0 \
      --save-screenshots --driver Firefox \
      --output archived_webpage \
      'https://some.page/to-archive'

Search Forms and Crawl Result Pages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Query a web form, identified by containing the text "I'm a search form",
entering "NAME" into the first (0th) text input field and select January
20th, 1992 in the second (1st) date field. Then click all buttons with
the text "Next ->" to get all results pages:

::

    autoscrape \
      --backend selenium \
      --output search_query_data \
      --form-match "I'm a search form" \
      --input "i:0:NAME,d:1:1992-01-20" \
      --next-match "Next ->" \
      'https://some.page/search?s=newquery'

Setup for Standalone Local CLI
------------------------------

External Dependencies
~~~~~~~~~~~~~~~~~~~~~

If you want to use the ``selenium`` backend for interactive crawling,
you need to have geckodriver installed. You can do that here:

::

    https://github.com/mozilla/geckodriver/releases

Your ``geckodriver`` needs to be compatible with your current version of
Firefox or you will get errors.

If you prefer to use Chrome, you will need the ChromeDriver (we've
tested using v2.41). It can be found in your distribution's package
manager or here:

::

    https://sites.google.com/a/chromium.org/chromedriver/downloads

Installing the remaining Python dependencies can be done using pip.

Pip Install Method
~~~~~~~~~~~~~~~~~~

Next you need to set up your python virtual environment (Python 3.6
required) and install the Python dependencies:

::

    pip install -r requirements.txt

Running Standalone Scraper
--------------------------

Environment Test Crawler
~~~~~~~~~~~~~~~~~~~~~~~~

You can run a test to ensure your webdriver is set up correctly by
running the ``test`` crawler:

::

    ./autoscrape --backend selenium --show-browser [SITE_URL]

The ``test`` crawler will just do a depth-first click-only crawl of an
entire website. It will not interact with forms or POST data. Data will
be saved to ``./autoscrape-data/`` (the default output directory).

Manual Config-Based Scraper
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Autoscrape has a manually controlled mode, similar to wget, except this
uses interactive capabilities and can input data to search forms, follow
"next page"-type buttons, etc. This functionality can be used either as
a standalone crawler/scraper or as a method to build a training set for
the automated scrapers.

Autoscrape manual-mode full options:

::

    AUTOSCRAPE - Interactively crawl, find searchable forms,
    input data to them and scrape data on the results, from an
    initial BASEURL.

    Usage:
        autoscrape [options] BASEURL

    General Options:
    --backend BACKEND
        The backend to use. Currently one of "selenium" or "requests".
        The requests browser is only capable of crawling, but is
        approximately 2-3.5x faster.
        [default: selenium]

    --loglevel LEVEL
        Loglevel, note that DEBUG is extremely verbose.
        [default: INFO]

    --quiet
        This will silence all logging to console.

    Crawl-Specific Options:
        --maxdepth DEPTH
            Maximum depth to crawl a site (in search of form
            if the option --form-match STRING is specified,
            see below). Setting to 0 means don't crawl at all,
            all operations are limited to the BASEURL page.
            Setting to -1 means unlimited maximum crawl depth.
            [default: 10]

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

        --result-page-links MATCH_STRINGS_LIST
            If specified, AutoScrape will click on any links matching
            this string when it arrives on a search result page.

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
            "YYYY-MM-DD" format). The type is separated by a
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

        --full-page-screenshots
            By default, we only save the first displayed part of the
            webpage. The remaining portion that you can only see
            by scrolling down isn't captured. Setting this option
            forces AutoScrape to scroll down and capture the entire
            web content. This can fail in certain circumstances, like
            in API output mode and should be used with care.

        --save-graph
            This option allows the scraper to build a directed graph
            of the entire scrape and will save it to the "graph"
            subdirectory under the output dir. The output file
            is a timestamped networkx pickled graph.

        --disable-style-saving
            By default, AutoScrape saves the stylesheets associated
            with a scraped page. To save storage, you can disable this
            functionality by using this option.

Setup Containerized API Version
-------------------------------

AutoScrape can also be ran as a containerized cluster environment, where
scrapes can be triggered and stopped via API calls and data can be
streamed to this server.

This requires the `autoscrape-www <https://github.com/brandonrobertz/autoscrape-www>`__ submodule to be pulled:

::

    git submodule init
    git submodule update

This will pull the browser-based UI into the `www/` folder.

You also need
`docker-ce <https://docs.docker.com/install/#server>`__ and
`docker-compose <https://docs.docker.com/compose/install/>`__. Once you
have these dependencies installed, simply run:

::

    docker-compose build --pull
    docker-compose up -t0 --abort-on-container-exit

This will build the containers and launch a API server running on local
port 5000. More information about the API calls can be found in
``autoscrape-server.py``.

If you have make installed, you can simply run ``make start``.

NOTE: This is a work in progress prototype that will likely be removed
once AutoScrape is integrated into `CJ Workbench <http://workbenchdata.com>`__.

.. |Quickstart Video| image:: https://github.com/brandonrobertz/autoscrape-py/blob/master/images/quickstart-video.png
   :target: https://www.youtube.com/watch?v=D0Mchcf6THE
