# -*- coding: UTF-8 -*-
import logging
import string
from itertools import product

from . import BaseScraper
from ..control import Controller


logger = logging.getLogger('AUTOSCRAPE')


class MLAutoScraper(BaseScraper):
    """
    A fully-automated web scraper that runs based on the outputs of
    several trained machine learning classifiers.
    """

    def __init__(self, baseurl, maxdepth=10, loglevel=None, formdepth=0,
                 html_embeddings=None, word_embeddings=None, **kwargs):
        # setup logging, etc
        super(MLAutoScraper, self).setup_logging(loglevel=loglevel)
        # set up web scraper controller
        self.control = Controller(
            html_embeddings_file=html_embeddings,
            word_embeddings_file=word_embeddings,
        )
        self.control.initialize(baseurl)
        # depth of DFS in search of form
        self.maxdepth = maxdepth
        # current depth of iterating through 'next' form buttons
        self.formdepth = formdepth
        # the current path to wherever we are at
        self.path = []

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
                # TODO: replace with ML model? Determine whether a link
                # or button is a "next" button?
                if "next page" in button.lower():
                    logger.debug("Clicking button %s..." % ix)
                    depth += 1
                    self.control.select_button(ix, iterating_form=True)
                    found_next = True
                    # don't click any other next buttons
                    break

            if not found_next:
                logger.debug("[*] Next button not found!")
                break

        for _ in range(depth):
            logger.debug("[-] Going back from 'next'...")
            self.control.back()

    def run(self, depth=0):
        if depth > self.maxdepth:
            logger.debug(" - Maximum depth %s reached, returning..." % depth)
            self.control.back()
            return

        logger.debug("** DEPTH %s" % depth)

        # TODO: ML model will go here. What type of page is this?
        # Search form, error page, data page, etc? The result of
        # this will result in a cange in logic
        x = self.control.page_vector()
        logger.debug(" - Page vector x=%s" % x)

        form_vectors = self.control.form_vectors(type="text")
        for ix in range(len(form_vectors)):
            form_data = form_vectors[ix]
            # inputs are keyed by form index
            inputs = self.control.inputs[ix]

            logger.debug(" - Form: %s Text: %s" % (ix, form_data))
            logger.debug(" - Inputs: %s" % inputs)

            # TODO: Another ML model will go here: a classifier that
            # will look through forms and identify a good search form
            # that we should iterate on. This model will only be
            # used if the parent model (page classifier) determines
            # that this may be a search form page. This one will search
            # the DOM and find the best matching block with inputs.
            logger.debug(" - Page vector x=%s" % x)
            if "Verify Degrees" not in form_data or len(inputs) != 1:
                continue

            for input in self.input_generator(length=1):
                self.control.input(ix, 0, input)
                self.control.submit(ix)
                logger.debug("[*] Beginning iteration of data pages")
                self.keep_clicking_next_btns(maxdepth=3)
                self.control.back()

            logger.debug("[+] Completed iteration!")

        links = self.control.clickable
        logger.debug(" - All tags at this depth %s" % links)

        # TODO: ML model will go here: Which link should we click on?
        # This may be a job best suited for RL, but we could use a
        # simple classifier to order the links by most likely to lead
        # to a search form page.
        for ix in range(len(links)):
            logger.debug(" - Attempting click on link %s" % ix)
            if self.control.select_link(ix):
                logger.debug("[.] Clicked! Recursing ...")
                self.run(depth=depth + 1)

        self.control.back()
