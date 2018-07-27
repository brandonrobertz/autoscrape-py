# -*- coding: UTF-8 -*-
import logging
import string
from itertools import product

from .control import Controller
from .web import Scraper


logger = logging.getLogger('AUTOSCRAPE')


"""
COMMAND        Logical Control Flow Step
--------       ---------------------------------------------------------------
INIT (url)               initialize & get entry point
                                     │
                                     ↓
                                 load page    🠤───────────────────┐
                                     │                            │
GET_CLICKABLE                        │        click a link based on likelihood
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

        logger.debug(
            "All tags at this depth \n    %s" % ("\n    ").join(tags))

        for tag in tags:
            logger.debug("Attempting click on tag \n    %s" % tag)

            if self.scraper.click(tag):
                logger.debug("Clicked! Recursing ...")
                self.run(
                    depth=depth + 1, tags=self.scraper.get_clickable())

        logger.debug("Going back...")
        self.scraper.back()


class TestManualControlScraper(TestScraper):
    """
    A Depth-First Search scraper that looks for forms, inputs, and next
    buttons by some manual criteria and iterates accordingly.
    """

    def __init__(self, baseurl, maxdepth=10, loglevel=None):
        super(TestScraper, self).setup_logging(loglevel=loglevel)
        self.control = Controller()
        self.control.initialize(baseurl)
        self.maxdepth = maxdepth

    def input_generator(self, length=1):
        chars = string.ascii_lowercase
        for input in product(chars, repeat=length):
            yield "".join(input)

    def keep_clicking_next_btns(self, maxdepth=0):
        button_data = self.control.button_vectors()
        logger.debug("Button vectors %s" % button_data)
        depth = 0
        while True:
            found_next = False
            if maxdepth and depth > maxdepth:
                logger.debug("Max 'next' depth reached %s" % depth)
                break

            for ix in range(len(button_data)):
                logger.debug("Depth %s" % depth)
                button = button_data[ix]
                logger.debug("Checking button %s" % button)
                if "next page" in button.lower():
                    logger.debug("Clicking button %s..." % ix)
                    depth += 1
                    self.control.select_button(ix, iterating_form=True)
                    found_next = True
                    # don't click any other next buttons
                    break

            if not found_next:
                logger.debug("Next button not found!")
                break

        for _ in range(depth):
            logger.debug("Going back from 'next'...")
            self.control.back()

    def run(self, depth=0):
        if depth > self.maxdepth:
            logger.debug("Maximum depth %s reached, returning..." % depth)
            self.control.back()
            return

        logger.debug("** DEPTH %s" % depth)

        form_vectors = self.control.form_vectors(type="text")
        for ix in range(len(form_vectors)):
            form_data = form_vectors[ix]
            # inputs are keyed by form index
            inputs = self.control.inputs[ix]

            logger.debug("Form: %s Text: %s" % (ix, form_data))
            logger.debug("Inputs: %s" % inputs)

            # TODO: this is where a ML algorithm will go.
            # Classifier for determining if there's a good form
            # on a page.
            if "Verify Degrees" not in form_data or len(inputs) != 1:
                continue

            for input in self.input_generator(length=1):
                logger.debug("Inputting %s to input %s" % (input, 0))
                self.control.input(ix, 0, input)
                self.control.submit(ix)
                logger.debug("Beginning iteration of data pages")
                self.keep_clicking_next_btns(maxdepth=3)
                self.control.back()

            logger.debug("Completed iteration!")

        links = self.control.clickable
        logger.debug("All tags at this depth %s" % links)

        for ix in range(len(links)):
            logger.debug("Attempting click on link %s" % ix)
            if self.control.select_link(ix):
                logger.debug("Clicked! Recursing ...")
                self.run(depth=depth + 1)

        logger.debug("Going back...")
        self.control.back()


class BruteForceScraper(object):
    pass


class AutoScraper(object):
    pass

