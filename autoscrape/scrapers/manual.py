# -*- coding: UTF-8 -*-
import hashlib
import logging
import os
import string
from itertools import product

from . import BaseScraper
from ..control import Controller


logger = logging.getLogger('AUTOSCRAPE')


class ManualControlScraper(BaseScraper):
    """
    A Depth-First Search scraper that looks for forms, inputs, and next
    buttons by some manual criteria and iterates accordingly.
    """

    # TODO: save the path to the matched search form to a file. then
    # upon subsequent loads, we can try that path first and then go
    # from there. this way the manual control scraper can learn from
    # self-exploration based on manual params
    #
    # Another related idea: it would be nice if we had an API that
    # saved data about successful runs and loading/replaying them
    # so users can get familiar with the concepts of self-exploration
    # and self-learning but without having to get the ML concepts.

    def __init__(self, baseurl, maxdepth=10, loglevel=None, formdepth=0,
                 next_match="next page", form_match="first name",
                 output_data_dir=None, input_minlength=1):
        # setup logging, etc
        super(ManualControlScraper, self).setup_logging(loglevel=loglevel)
        # set up web scraper controller
        self.control = Controller()
        self.control.initialize(baseurl)
        # depth of DFS in search of form
        self.maxdepth = maxdepth
        # current depth of iterating through 'next' form buttons
        self.formdepth = formdepth
        # match for link to identify a "next" button
        self.next_match = next_match
        # string to match a form (by element text) we want to scrape
        self.form_match = form_match
        # Where to write training data from crawl
        self.output_data_dir = output_data_dir

    def save_training_page(self, classname=None):
        """
        Writes the current page to the output data directory (if provided)
        to the given class folder.
        """
        logger.debug("Saving training page for class: %s" % classname)
        classes = [
            "data_pages", "error_pages", "links_to_documents",
            "links_to_search", "search_pages"
        ]
        if classname not in classes:
            raise ValueError("Base class speficied: %s" % classname)

        if not self.output_data_dir:
            return

        classdir = os.path.join(self.output_data_dir, classname)
        if not os.path.exists(classdir):
            os.mkdir(classdir)

        html = self.control.scraper.page_html
        url = self.control.scraper.page_url
        h = hashlib.sha256(html.encode("utf-8")).digest().hex()
        logger.debug("URL: %s, Hash: %s" % (url, h))
        filepath = os.path.join(classdir, "%s.html" % h)

        with open(filepath, "w") as f:
            f.write(html)

    def input_generator(self, length=1):
        chars = string.ascii_lowercase
        for input in product(chars, repeat=length):
            yield "".join(input)

    def keep_clicking_next_btns(self, maxdepth=0):
        depth = 0
        while True:
            if self.formdepth and depth > self.formdepth:
                logger.debug("Max 'next' formdepth reached %s" % depth)
                break

            found_next = False
            button_data = self.control.button_vectors()
            logger.debug("Button vectors %s" % button_data)

            for ix in range(len(button_data)):
                logger.debug("Depth %s" % depth)
                button = button_data[ix]
                logger.debug("Checking button %s" % button)
                if self.next_match in button.lower():
                    self.save_training_page(classname="data_pages")
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

            if self.form_match not in form_data:
                continue

            self.save_training_page(classname="search_pages")
            for input in self.input_generator(length=self.input_minlength):
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

