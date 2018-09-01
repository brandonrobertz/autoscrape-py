#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import argparse

import autoscrape


class SmartFormatter(argparse.HelpFormatter):

    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


def parse_args():
    desc = """
A programming-free automatic web crawler and structured data scraper for
interaction-heavy websites.

There are several different scrapers available, each with a different
philosophy/mechanism behind their operation:

  manual-control: command line config-based crawler/scraper
  autoscrape-ml:  machine-learning based crawler/scraper
  autoscrape-rl:  self-learning RL-based crawler/scraper
  test:           crawler to only ensure things are set up properly
"""

    parser = argparse.ArgumentParser(
        description=desc, formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        '--loglevel', type=str, default="INFO",
        choices=["DEBUG", "INFO", "WARN", "ERROR"],
        help="Loglevel (default: INFO)"
    )
    parser.add_argument(
        '--maxdepth', type=int, default=10,
        help=("Maximum depth to allow the scraper to traverse in search "
              "of a scrapable search form (default: 10)")
    )
    parser.add_argument(
        '--driver', type=str,
        default="Firefox", choices=["Firefox", "Chrome"],
        help=("Which WebDriver to use (default: Firefox).")
    )
    parser.add_argument(
        '--load_images', type=bool, default=False,
        help="Whether or not to load images when scraping/crawling.",
    )

    subparsers = parser.add_subparsers(
        dest="scraper",
        help="Specified crawler type (required)"
    )

    baseurl_desc = "The base URL to begin crawling/scraping from."
    formdepth_help = "Once a search form has been found, this controls how many pages will be scraped (default: 0, no limit)"

    # Manual-Control Scraper
    manual_p = subparsers.add_parser(
        "manual-control",
        description="A Depth-First Search scraper that looks for forms, inputs, and next buttons by some manual criteria and iterates accordingly.  This scraper is config-based, and identifies search forms and buttons by configurable string matching from command line options. This scraper can be used to build training data for the other ML/RL scrapers or be used on its own as a config-based scraper."
    )
    manual_p.add_argument(
        "baseurl", type=str,
        help=baseurl_desc
    )
    manual_p.add_argument(
        '--formdepth', type=int, default=0,
        help=formdepth_help,
    )
    manual_p.add_argument(
        '--input_minlength', type=int, default=1,
        help=(
            "Minimum number of characters that can be inserted into "
            "discovered form input."
        ),
    )
    manual_p.add_argument(
        '--form_input_range', type=str,
        help=(
            "The full character list to search form inputs with. "
            "Normally, the algorithm will use all characters A..Z, with "
            "repetitions based on the input_minlength parameter. This "
            "changes that A..Z range. Note that this field needs to contain "
            "every character to be included. Ranges (A-Z) will not be "
            "expanded (A-Z would be three characters A, -, Z)."
        )
    )
    manual_p.add_argument(
        '--form_input_index', type=int, default=0,
        help=(
            "Which input to fill, by order of appearance in HTML document. "
            "Defaults to the first input. (Note for computer-oriented people "
            "this is one-indexed, not zero)"
        )
    )
    manual_p.add_argument(
        '--wildcard', type=str,
        help="A wildcard character to append to the form inputs."
    )
    manual_p.add_argument(
        '--output_data_dir', type=str,
        help="Output directory to save training page data to.",
    )
    manual_p.add_argument(
        '--next_match', type=str, default="next page",
        help=(
            "A string which will be used to identify 'next' buttons in "
            "paginated form results."
        )
    )
    manual_p.add_argument(
        '--form_match', type=str, default="first name",
        help=(
            "A string which will be used to identify forms we want to "
            "scrape. The form text will be used as the haystack."
        )
    )
    manual_p.add_argument(
        '--form_submit_wait', type=int, default=5,
        help=(
            "For slow, interactive pages, the various techniques used "
            "to detect page data load & render don't work well. In these "
            "cases you can use this option to force a wait period "
            "after hitting a submit button."
        )
    )
    manual_p.add_argument(
        '--form_submit_natural_click', type=bool, default=False,
        help=(
            "Some pages have complicated listeners set up on submit buttons. "
            "In these cases, sometimes doing an element.click() does not "
            "work as there are wrapper listeners which need to be activated. "
            "This option simulates a click at a position on the page where the "
            "element lays."
        )
    )
    manual_p.add_argument(
        '--leave_host', type=bool, default=False,
        help=(
            "Controls whether the scraper will follow links outside of the "
            "base_url's host. (default: False, options: True|False)"
        )
    )
    manual_p.add_argument(
        '--link_priority', type=str, default="search",
        help=(
            "A string that will be used to sort the text of links "
            "so that the search phase can be sped up. Default is 'search' "
            "so all links matching 'search' will be bumped to the top of "
            "the stack for traversal and search for forms."
        )
    )


    # ML AutoScraper
    autoscrape_ml_p = subparsers.add_parser(
        "autoscrape-ml",
        description="A fully-automated web scraper that runs based on the outputs of several machine learning classifiers which have been trained on other crawls."
    )
    autoscrape_ml_p.add_argument(
        "baseurl", type=str,
        help=baseurl_desc
    )
    autoscrape_ml_p.add_argument(
        '--formdepth', type=int, default=0,
        help=formdepth_help,
    )
    autoscrape_ml_p.add_argument(
        '--word_embeddings', type=str,
        help=(
            'Path to a word embeddings file for page text vectorization. '
            'This is only used for the autoscrape-ml model.'
        )
    )
    autoscrape_ml_p.add_argument(
        '--html_embeddings', type=str,
        help=(
            'Path to a HTML char embeddings file for page HTML/code '
            'vectorization. This is only used for the autoscrape-ml model.'
        )
    )

    # Reinforcement AutoScraper
    autoscrape_rl_p = subparsers.add_parser(
        "autoscrape-rl",
        description="A fully-automated web scraper that runs using a self-learning technique called reinforcement learning, where a scraper learns how to interact with a page by trial-and-error."
    )
    autoscrape_rl_p.add_argument(
        "baseurl", type=str,
        help=baseurl_desc
    )
    autoscrape_rl_p.add_argument(
        '--formdepth', type=int, default=0,
        help=formdepth_help,
    )
    autoscrape_rl_p.add_argument(
        '--word_embeddings', type=str,
        help=(
            'Path to a word embeddings file for page text vectorization. '
            'This is only used for the autoscrape-ml model.'
        )
    )
    autoscrape_rl_p.add_argument(
        '--html_embeddings', type=str,
        help=(
            'Path to a HTML char embeddings file for page HTML/code '
            'vectorization. This is only used for the autoscrape-ml model.'
        )
    )

    # DFS Test Scraper
    test_p = subparsers.add_parser(
        "test",
        description="A depth-first search crawler which doesn't interact with forms. This is just a test crawler to ensure basic systems are working."
    )
    test_p.add_argument(
        "baseurl", type=str,
        help=baseurl_desc
    )

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
    }

    if args.scraper == "test":
        autoscrape.TestScraper(args.baseurl, **kwargs).run()

    elif args.scraper == "manual-control":
        kwargs["next_match"] = args.next_match
        kwargs["form_match"] = args.form_match
        kwargs["output_data_dir"] = args.output_data_dir
        kwargs["input_minlength"] = args.input_minlength
        kwargs["form_input_range"] = args.form_input_range
        kwargs["wildcard"] = args.wildcard
        kwargs["leave_host"] = args.leave_host
        kwargs["link_priority"] = args.link_priority
        kwargs["form_submit_wait"] = args.form_submit_wait
        kwargs["form_submit_natural_click"] = args.form_submit_natural_click
        kwargs["form_input_index"] = args.form_input_index
        autoscrape.ManualControlScraper(args.baseurl, **kwargs).run()

    elif args.scraper == "autoscrape-ml":
        kwargs["html_embeddings"] = args.html_embeddings or None
        kwargs["word_embeddings"] = args.word_embeddings or None
        autoscrape.MLAutoScraper(args.baseurl, **kwargs).run()

    else:
        print("No scraper found for %s" % args.scraper)

