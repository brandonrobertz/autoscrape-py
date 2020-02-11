# -*- coding: UTF-8 -*-
"""
AUTOSCRAPE - Interactively crawl, find searchable forms,
input data to them and scrape data on the results, from an
initial BASEURL.

Usage:
    autoscrape [options] BASEURL

General Options:
    --backend BACKEND
        The backend to use. Currently one of "selenium", "requests" or
        "warc".  The requests browser is only capable of crawling, but
        is approximately 2-3.5x faster. WARC is for emulating browsing
        through Common Crawl archival data.
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

    --only-links MATCH_STREING
        A whitelist of links to follow. All others will
        be ignored. Can be a string or a regex with
        multiple strings to match separated by a pipe
        (|) character.

    --ignore-links MATCH_STRING
        This option can be used to remove any links matching
        MATCH_STRING (can be a regex or just a string match)
        from consideration for clicking. Accepts the same
        argument format as --only-links.

    --link-priority SORT_STRING
        A string to sort the links by. In this case, any link
        containing "SORT_STRING" will be clicked before any other
        links. In most cases you probably want to use the
        whitelist, --only-links, option.

    --ignore-extensions IGNORE_EXTENSIONS
        Don't click on or download URLs pointing to files with
        these extensions.

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

    --browser-binary PATH_TO_BROWSER
        Path to a specific browser binary. If left blank
        selenium will pull the browser found on your path.

    --remote-hub URI
        If using "remote" driver, specify the hub URI to
        connect to. Needs the proto, address, port, and path.
        [default: http://localhost:4444/wd/hub]

WARC Options:
    --warc-directory PATH_TO_WARCS
        Path to the folder containing GZipped WARC files. These can be
        downloaded from Common Crawl. Required when using the "warc"
        backend.

    --warc-index-file PATH_TO_LEVELDB
        Path to the level DB database holding the URL-to-file
        index: URL => (filename, record_number)
        This will be generated from the WARCS in the --warc-directory
        speficied if it's not already. Required when using the "warc"
        backend.

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
"""
import logging

from docopt import docopt

import autoscrape


logger = logging.getLogger('AUTOSCRAPE')


def main():
    docopt_args = docopt(__doc__)

    BASEURL = docopt_args.pop("BASEURL")

    # strip the -- and convert - to _
    args = {}
    for option in docopt_args:
        args[option[2:].replace('-', '_')] = docopt_args[option]

    # configure stdout logging
    docopt_args["stdout"] = True
    if "quiet" in args:
        quiet = args.pop("quiet")
        args["stdout"] = not quiet

    scraper = autoscrape.ManualControlScraper(BASEURL, **args)

    logger.debug("AutoScrape starting with arguments: %s" % (docopt_args))
    scraper.run()

