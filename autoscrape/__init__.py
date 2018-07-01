# -*- coding: UTF-8 -*-

from .control import Controller
from .web import Scraper


"""
COMMAND        Logical Control Flow Step
--------       -------------------------------------------------------------------
INIT (url)               initialize & get entry point
                                     │
                                     ↓
                                 load page    🠤───────────────────┐
                                     │                            │
SELECT_LINK (index)                  │            click a link based on likelihood
                                     │               of finding a search form
                                     ↓                            │
GET_TAGS     ┌────🠦 look for search form (possibly classifier) ───┘
             │                       │
             │                       │ FOUND
             │                       ↓
GET_TAGS?    │         identify forms on page that require input
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
GET_TAGS             │     look for a next button ───────────┘
                     │         (classifier)        NOT FOUND
                     │               │
                     │               │ YES
                     │               ↓
SELECT_LINK (index)  └─── click the next button & load page
"""

class TestScraper(object):

    def __init__(self, baseurl):
        """
        Initialize our scraper and get the first page.
        """
        self.scraper = Scraper()
        self.scraper.fetch(baseurl)
        self.visited_urls = set()

    def run(self, depth=0, tags=None):
        print("** DEPTH", depth)
        if not tags:
            tags = self.scraper.get_tags()

        print("RUN tags", ("\n    ").join(tags))

        for tag in tags:
            print("RUN tag", tag)

            if self.scraper.click(tag):
                print("Clicked! Recursing ...")
                self.run(depth=depth + 1, tags=self.scraper.get_tags())

        print("Going back...")
        self.scraper.back()


class BruteForceScraper(object):
    pass


class AutoScraper(object):
    pass

