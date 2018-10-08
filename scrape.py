#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
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

        "c:0:True,i:0:atext,s:1:France"

        A single-input type can be one of three types:
        checkbox ("c"), input box ("i"), and option select
        ("s"). The type is separated by a colon, and the
        input index position is next. (Each input type has
        its own list, so a form with one input, one
        checkbox, and one option select, will all be at
        index 0.) The final command, sepearated by another
        colon, describes what to do with the input.

        Multiple inputs are separated by a comma, so you can
        interact with multiple inputs before submitting the
        form.

        To illustrate this, the above command does the following:
            - first input checkbox is checked (uncheck is False)
            - first input box gets filled with the string "first"
            - second select input gets the "France" option chosen

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
"""

from docopt import docopt

import autoscrape


if __name__ == "__main__":
    docopt_args = docopt(__doc__)

    BASEURL = docopt_args.pop("BASEURL")

    # strip the -- and convert - to _
    args = {}
    for option in docopt_args:
        args[option[2:].replace('-', '_')] = docopt_args[option]

    autoscrape.ManualControlScraper(BASEURL, **args).run()

    # elif args.scraper == "autoscrape-ml":
    #     kwargs["html_embeddings"] = args.html_embeddings or None
    #     kwargs["word_embeddings"] = args.word_embeddings or None
    #     autoscrape.MLAutoScraper(args.baseurl, **kwargs).run()

    # else:
    #     print("No scraper found for %s" % args.scraper)

