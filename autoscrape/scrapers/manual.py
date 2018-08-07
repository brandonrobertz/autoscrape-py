# -*- coding: UTF-8 -*-
import logging
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

    def __init__(self, baseurl, maxdepth=10, loglevel=None, formdepth=0):
        # setup logging, etc
        super(ManualControlScraper, self).setup_logging(loglevel=loglevel)
        # set up web scraper controller
        self.control = Controller()
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
                # TODO: replace with a configuration option?
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

            # TODO: replace with a configuration option
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


