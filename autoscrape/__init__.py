# -*- coding: UTF-8 -*-
import logging

from .control import Controller
from .web import Scraper


logger = logging.getLogger('AUTOSCRAPE')


"""
COMMAND        Logical Control Flow Step
--------       -------------------------------------------------------------------
INIT (url)               initialize & get entry point
                                     │
                                     ↓
                                 load page    🠤───────────────────┐
                                     │                            │
GET_CLICKABLE                        │            click a link based on likelihood
SELECT_LINK (index)                  │               of finding a search form
                                     ↓                            │
GET_FORMS    ┌────🠦 look for search form (possibly classifier) ───┘
             │                       │
             │                       │ FOUND
             │                       ↓
GET_INPUTS   │         identify forms on page that require input
             │     (begin with config then move to heuristic then ML)
             │                       │
             │                       ↓
             │      initialize iterators for required inputs
             │      (begin with config/brute force, then RL)
             │                       │
             │                       ↓
             └─────── are we at the end of our iterators?
                YES                  │
                                     ↓
INPUT (index, chars)     enter data into form inputs 🠤───────┐
                                     │                       │
                                     ↓                       │
SUBMIT (index)          submit form and load next page       │
                                     │                       │
                                     ↓                       │
                     ┌──────🠦 scrape the page                │
                     │               │                       │
                     │               ↓                       │
GET_LINKS            │     look for a next button ───────────┘
                     │         (classifier)        NOT FOUND
                     │               │
                     │               │ YES
                     │               ↓
SELECT_LINK (index)  └─── click the next button & load page
"""

class BaseScraper(object):
    def setup_logging(self, loglevel=None):
        if not loglevel or loglevel == "DEBUG":
            loglevel = logging.DEBUG
        elif loglevel == "INFO":
            loglevel = logging.INFO
        elif loglevel == "WARN":
            loglevel = logging.WARN
        elif loglevel == "ERROR":
            loglevel = logging.ERROR

        logger.setLevel(loglevel)
        console_handler = logging.StreamHandler()
        logger.addHandler(console_handler)


class TestScraper(BaseScraper):

    def __init__(self, baseurl, maxdepth=10, loglevel=None):
        """
        Initialize our scraper and get the first page.
        """
        super(TestScraper, self).setup_logging(loglevel=loglevel)
        self.scraper = Scraper()
        self.scraper.fetch(baseurl)
        self.visited_urls = set()
        self.maxdepth = maxdepth

    def run(self, depth=0, tags=None):
        """
        This is the main recursive depth-first search of a site. It
        doesn't do anything but crawl a site DFS and ensure the tagging
        and web engine is working as it should.
        """
        if depth > self.maxdepth:
            logger.debug("Maximum depth %s reached, returning..." % depth)
            self.scraper.back()
            return

        logger.debug("** DEPTH %s" % depth)

        if not tags:
            tags = self.scraper.get_clickable()

        logger.debug("All tags at this depth \n    %s" % ("\n    ").join(tags))

        for tag in tags:
            logger.debug("Attempting click on tag \n    %s" % tag)

            if self.scraper.click(tag):
                logger.debug("Clicked! Recursing ...")
                self.run(depth=depth + 1, tags=self.scraper.get_clickable())

        logger.debug("Going back...")
        self.scraper.back()


class BruteForceScraper(object):
    pass


class AutoScraper(object):
    pass

