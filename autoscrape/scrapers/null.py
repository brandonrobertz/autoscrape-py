# -*- coding: UTF-8 -*-
import logging

from . import BaseScraper
from ..control import Controller
from autoscrape.backends.requests.browser import RequestsBrowser
from autoscrape.backends.selenium.browser import SeleniumBrowser


logger = logging.getLogger('AUTOSCRAPE')


class NullScraper(BaseScraper):
    """
    A test scraper that just provides direct access to scraper and
    controller. For vectorizing documents.
    """

    def __init__(self, *args, html_embeddings=None, word_embeddings=None,
                 loglevel="INFO", scraper=True, controller=False, backend=None,
                 driver="Chrome", vectorizer=False, **kwargs):
        super(NullScraper, self).setup_logging(loglevel=loglevel)

        Browser = None
        if backend == "selenium":
            Browser = SeleniumBrowser
        elif backend == "requests":
            Browser = RequestsBrowser
        else:
            raise NotImplementedError(
                "No backend found: %s" % (backend)
            )

        if scraper:
            self.scraper = Browser(driver=driver)
        if controller:
            self.control = Controller(
                html_embeddings_file=html_embeddings,
                word_embeddings_file=word_embeddings,
            )
        if vectorizer:
            self.vectorizer = self.control.vectorizer
