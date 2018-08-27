# -*- coding: UTF-8 -*-
import time
import hashlib
import logging
import os
import string
import sys
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
                 output_data_dir=None, input_minlength=1, wildcard=None,
                 form_input_range=None, leave_host=False, driver="Firefox",
                 link_priority="search", form_submit_natural_click=False,
                 form_submit_wait=5, load_images=False):
        # setup logging, etc
        super(ManualControlScraper, self).setup_logging(loglevel=loglevel)
        # set up web scraper controller
        self.control = Controller(
            leave_host=leave_host, driver=driver,
            form_submit_natural_click=form_submit_natural_click,
            form_submit_wait=form_submit_wait,
            load_images=load_images,
        )
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
        # minimum length of form inputs (in characters)
        self.input_minlength = input_minlength
        # Additonal filter for range of chars inputted to forms as search
        self.form_input_range = form_input_range
        # Wildcard character to be added to search inputs
        self.wildcard = wildcard
        # string used to match link text in order to sort them higher
        self.link_priority = link_priority
        # attempt a position-based "natural click" over the element
        self.form_submit_natural_click = form_submit_natural_click
        # a period of seconds to force a wait after a submit
        self.form_submit_wait = form_submit_wait

    def save_screenshot(self):
        t = int(time.time())
        screenshot_dir = os.path.join(self.output_data_dir, "screenshots")
        if not os.path.exists(screenshot_dir):
            os.mkdir(screenshot_dir)
        filepath = os.path.join(screenshot_dir, "%s.png" % t)
        logger.debug("Saving screenshot to file: %s." % filepath);
        with open(filepath, "wb") as f:
            png = self.control.scraper.driver.get_screenshot_as_png()
            f.write(png)

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
        if self.form_input_range:
            chars = self.form_input_range
        for input in product(chars, repeat=length):
            inp = "".join(input)
            if self.wildcard:
                inp += self.wildcard
            yield inp

    def keep_clicking_next_btns(self, maxdepth=0):
        logger.debug("*** Entering 'next' iteration routine")
        depth = 0
        while True:
            if self.formdepth and depth > self.formdepth:
                logger.debug("Max 'next' formdepth reached %s" % depth)
                break

            found_next = False
            button_data = self.control.button_vectors()
            n_buttons = len(button_data)
            logger.debug("** 'Next' Iteration Depth %s" % depth)
            logger.debug("Button vectors (%s): %s" % (
                n_buttons, button_data))

            for ix in range(n_buttons):
                button = button_data[ix]
                logger.debug("Checking button: %s" % button)
                if self.next_match.lower() in button.lower():
                    self.save_training_page(classname="data_pages")
                    self.save_screenshot()
                    logger.debug("Next button found! Clicking: %s" % ix)
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
        logger.debug("** Crawl depth %s" % depth)
        if depth > self.maxdepth:
            logger.debug("Maximum depth %s reached, returning..." % depth)
            self.control.back()
            return

        self.save_screenshot()
        scraped = False
        form_vectors = self.control.form_vectors(type="text")

        for ix in range(len(form_vectors)):
            form_data = form_vectors[ix]
            # inputs are keyed by form index
            inputs = self.control.inputs[ix]

            logger.debug("Form: %s Text: %s" % (ix, form_data))
            logger.debug("Inputs: %s" % inputs)

            if self.form_match.lower() not in form_data.lower():
                continue

            logger.debug("*** Found an input form!")
            self.save_training_page(classname="search_pages")
            self.save_screenshot()
            inp_gen = self.input_generator(
                length=self.input_minlength,
            )
            for input in self.input_generator(length=self.input_minlength):
                logger.debug("Inputting %s to input %s" % (input, 0))
                self.control.input(ix, 0, input)
                self.save_screenshot()
                self.control.submit(ix)
                logger.debug("Beginning iteration of data pages")
                self.save_screenshot()
                self.keep_clicking_next_btns(maxdepth=3)
                scraped = True
                self.control.back()

            logger.debug("Completed iteration!")
            # Only scrape a single form, due to explicit, single
            # match configuration option

            if scraped:
                logger.debug("Scrape complete! Exiting.")
                sys.exit(0)

        links = self.control.clickable
        link_vectors = self.control.link_vectors()
        link_zip = list(zip(range(len(link_vectors)),link_vectors))
        # TODO: this will be replaced by a ML algorith to sort links by those
        # most likely to be fruitful
        link_zip.sort(key=lambda r: self.link_priority in r[1].lower(), reverse=True)
        for ix, _ in link_zip:
            if depth == self.maxdepth:
                logger.debug("At maximum depth: %s, skipping links." % depth)
                break

            if self.control.select_link(ix):
                logger.debug("Clicked! Recursing ...")
                self.run(depth=depth + 1)

        logger.debug("Searching forms and links on page complete")
        self.control.back()

