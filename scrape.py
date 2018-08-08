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
    }

    if args.scraper == "test":
        autoscrape.TestScraper(args.baseurl, **kwargs).run()

    elif args.scraper == "manual-control":
        autoscrape.ManualControlScraper(args.baseurl, **kwargs).run()

    elif args.scraper == "autoscrape-ml":
        kwargs["html_embeddings"] = args.html_embeddings or None
        kwargs["word_embeddings"] = args.word_embeddings or None
        autoscrape.MLAutoScraper(args.baseurl, **kwargs).run()

    else:
        print("No scraper found for %s" % args.scraper)

