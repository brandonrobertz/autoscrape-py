# -*- coding: UTF-8 -*-
import logging

from . import BaseScraper

from autoscrape.backends.requests.browser import RequestsBrowser


logger = logging.getLogger('AUTOSCRAPE')


class TestScraper(BaseScraper):
    def __init__(self, baseurl, maxdepth=10, loglevel=None):
        """
        Initialize our scraper and get the first page.
        """
        super(TestScraper, self).setup_logging(loglevel=loglevel)
        self.scraper = RequestsBrowser()
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
