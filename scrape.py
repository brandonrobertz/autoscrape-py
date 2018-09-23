#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import argparse

import autoscrape

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

class SmartFormatter(argparse.HelpFormatter):

    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


def parse_args():
    desc = """
AUTOSCRAPE - Interactively crawl, find searchable forms, input data
to them and scrape data on the results, from an initial BASEURL.
 
USAGE
    scrape.py [OPTION...]  BASEURL
 
OPTIONS
 
Crawl-Specific Options
    These options control the crawling capabilities of the scraper.
    You can either have the crawler simply crawl a site, saving data
    as it goes along (see below,  Data-Saving Options) or combine
    crawl with form-discovery and scraping (see Interactive Form Search
    Options below).
    
    --maxdepth 10
        Maximum depth to crawl a site (in search of form if the
        option "--form-match [string]" is specified, see below).
    
    --leave-host False
        Whether the crawl can leave the base URL host.
    
    --link-priority "search"
        A string to sort the links by. In this case, any link
        containing "search" will be clicked before any other links.
    
Interactive Form Search Options
    These options control the interactive form capabilities of the
    scraper. In order to use this, you need both --form-match and
    --input filled properly for your desired search form. This can be
    combined with the crawling capabilities, described above.
     
    --form-match [SEARCH_STRING]
        The crawler will identify a form to search/scrape if it
        contains the specified string. If matched, it will be
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
 
Webdriver-Specific and General Options
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
 
Data Saving Options
    --output-data-dir [OUTPUT_DATA_DIR]
        If specified, this indicates where to save pages during a
        crawl. This directory will be created if it does not
        currently exist.  This directory will have several
        sub-directories that contain the different types of pages
        found (i.e., search_pages, data_pages, screenshots).

EXAMPLES

    ./scrape.py
        --loglevel DEBUG
        --maxdepth 10
        --form-match "first name"
        --input "i:0:firstname,i:1:lastname"
        --next-match "next page"
        --output-data-dir "firstname_lastname_scrape"
        [BASEURL]

In the above example, the scraper will crawl until it finds a form that
contains the text "first name". At that point, it will type "firstname"
in the first text input box and "lastname" into the second input box,
then submits the form. Then it will wait for the submission to be
completed/loaded and will continue clicking on buttons/links containing
"next page" until there are no more. All data found during the scrape
will be saved to the ./firstname_lastname_scrape directory.
"""

    parser = argparse.ArgumentParser(
        description=desc, formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "BASEURL", type=str,
        help="The base URL to begin crawling/scraping from."
    )

    # Crawl-Specific Options
    parser.add_argument(
        "--maxdepth", type=int, default=10,
        help=(
            "Maximum depth to crawl a site (in search of form if the "
            "option \"--form-match [string]\" is specified, see below)."
        )
    )
    parser.add_argument(
        '--leave-host', type=str2bool, default=False,
        help=(
            "Whether the crawl can leave the base URL host."
        )
    )
    parser.add_argument(
        "--link-priority", type=str, default="search",
        help=(
            "A string to sort the links by. By default, any link "
            "containing \"search\" will be clicked before any other links."
        )
    )

    # Interactive Form Search Options
    parser.add_argument(
        "--form-match", type=str, default=None, required=False,
        help=(
            "The crawler will identify a form to search/scrape if it "
            "contains the specified string. If matched, it will be "
            "interactively scraped using the below instructions."
        )
    )
    parser.add_argument(
        "--input", type=str, default=None, required=False,
        help=(
            "Interactive search descriptor. This describes how to "
            "interact with a matched form. The inputs are described in "
            "the following format: a single-input type can be one of "
            "three types: checkbox (\"c\"), input box (\"i\"), and option "
            "select (\"s\"). The type is separated by a colon, and the "
            "input index position is next. (Each input type has its own "
            "list, so a form with one input, one checkbox, and one "
            "option select, will all be at index 0.) The final command, "
            "sepearated by another colon, describes what to do with the "
            "input. Multiple inputs are separated by a comma, so you can "
            "interact with multiple inputs before submitting the form."
        )
    )
    parser.add_argument(
        "--next-match", type=str, default="next page",
        help=(
            "A string to match a \"next\" button with, after searching a form. "
            "The scraper will continue to click \"next\" buttons after a search "
            "until no matches are found, unless limited by the --formdepth "
            "option (see below)."
        )
    )
    parser.add_argument(
        "--formdepth", type=int, default=0,
        help=(
            "How deep the scraper will iterate, by clicking \"next\" "
            "buttons."
        )
    )
    parser.add_argument(
        "--form-submit-natural-click", type=str2bool, default=False,
        help=(
            "Some webpages make clicking a link element difficult due to "
            "JavaScript onClick events. In cases where a click does "
            "nothing, you can use this option to get the scraper to "
            "emulate a mouse click over the link's poition on the "
            "page, activating any higher level JS interactions."
        )
    )
    parser.add_argument(
        "--form-submit-wait", type=int, default=5,
        help=(
            "How many seconds to force wait after a submit to a form. "
            "This should be used in cases where the builtin "
            "wait-for-page-load isn't working properly (JS-heavy pages, "
            "etc). "
        )
    )

    # Webdriver-Specific and General Options
    parser.add_argument(
        '--load-images', type=str2bool, default=False,
        help=(
            "By default, images on a page will not be fetched. "
            "This speeds up scrapes on sites and lowers bandwidth "
            "needs."
        )
    )
    parser.add_argument(
        '--headless', type=str2bool, default=True,
        help=(
            "This hides the browser while it is bring automatically ran. If "
            "you need to debug a scrape, set this to False."
        )
    )
    parser.add_argument(
        '--driver', type=str,
        default="Firefox", choices=["Firefox", "Chrome"],
        help=(
            "Which browser to use."
        )
    )
    parser.add_argument(
        '--loglevel', type=str, default="INFO",
        choices=["DEBUG", "INFO", "WARN", "ERROR"],
        help=(
            "Loglevel, note that DEBUG is extremely verbose"
        )
    )

    # Data Saving Options
    parser.add_argument(
        '--output-data-dir', type=str,
        help=(
            "If specified, this indicates where to save pages during a "
            "crawl. This directory will be created if it does not "
            "currently exist.  This directory will have several "
            "sub-directories that contain the different types of pages "
            "found (i.e., search_pages, data_pages, screenshots)."
        )
    )

    # # ML AutoScraper
    # autoscrape_ml_p = subparsers.add_parser(
    #     "autoscrape-ml",
    #     description="A fully-automated web scraper that runs based on the outputs of several machine learning classifiers which have been trained on other crawls."
    # )
    # autoscrape_ml_p.add_argument(
    #     "baseurl", type=str,
    #     help=baseurl_desc
    # )
    # autoscrape_ml_p.add_argument(
    #     '--word_embeddings', type=str,
    #     help=(
    #         'Path to a word embeddings file for page text vectorization. '
    #         'This is only used for the autoscrape-ml model.'
    #     )
    # )
    # autoscrape_ml_p.add_argument(
    #     '--html_embeddings', type=str,
    #     help=(
    #         'Path to a HTML char embeddings file for page HTML/code '
    #         'vectorization. This is only used for the autoscrape-ml model.'
    #     )
    # )

    # # Reinforcement AutoScraper
    # autoscrape_rl_p = subparsers.add_parser(
    #     "autoscrape-rl",
    #     description="A fully-automated web scraper that runs using a self-learning technique called reinforcement learning, where a scraper learns how to interact with a page by trial-and-error."
    # )
    # autoscrape_rl_p.add_argument(
    #     "baseurl", type=str,
    #     help=baseurl_desc
    # )
    # autoscrape_rl_p.add_argument(
    #     '--formdepth', type=int, default=0,
    #     help=formdepth_help,
    # )
    # autoscrape_rl_p.add_argument(
    #     '--word_embeddings', type=str,
    #     help=(
    #         'Path to a word embeddings file for page text vectorization. '
    #         'This is only used for the autoscrape-ml model.'
    #     )
    # )
    # autoscrape_rl_p.add_argument(
    #     '--html_embeddings', type=str,
    #     help=(
    #         'Path to a HTML char embeddings file for page HTML/code '
    #         'vectorization. This is only used for the autoscrape-ml model.'
    #     )
    # )

    # # DFS Test Scraper
    # test_p = subparsers.add_parser(
    #     "test",
    #     description="A depth-first search crawler which doesn't interact with forms. This is just a test crawler to ensure basic systems are working."
    # )
    # test_p.add_argument(
    #     "baseurl", type=str,
    #     help=baseurl_desc
    # )

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    kwargs = {
        "maxdepth": args.maxdepth,
        "loglevel": args.loglevel,
        "formdepth": args.formdepth,
        "driver": args.driver,
        "load_images": args.load_images,
        "headless": args.headless,
        "next_match": args.next_match,
        "form_match": args.form_match,
        "output_data_dir": args.output_data_dir,
        "leave_host": args.leave_host,
        "link_priority": args.link_priority,
        "form_submit_wait": args.form_submit_wait,
        "form_submit_natural_click": args.form_submit_natural_click,
        "input": args.input
    }
    autoscrape.ManualControlScraper(args.BASEURL, **kwargs).run()

    # elif args.scraper == "autoscrape-ml":
    #     kwargs["html_embeddings"] = args.html_embeddings or None
    #     kwargs["word_embeddings"] = args.word_embeddings or None
    #     autoscrape.MLAutoScraper(args.baseurl, **kwargs).run()

    # else:
    #     print("No scraper found for %s" % args.scraper)

