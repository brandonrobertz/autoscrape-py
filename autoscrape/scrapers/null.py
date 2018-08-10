# -*- coding: UTF-8 -*-
import logging

from . import BaseScraper
from ..control import Controller
from ..web import Scraper


logger = logging.getLogger('AUTOSCRAPE')


class NullScraper(BaseScraper):
    """
    A test scraper that just provides direct access to scraper and
    controller.
    """

    def __init__(self, maxdepth=1, loglevel=None, formdepth=0,
                 html_embeddings=None, word_embeddings=None,
                 scraper=True, controller=False, vectorizer=False):
        super(NullScraper, self).setup_logging(loglevel=loglevel)
        if scraper:
            self.scraper = Scraper()
        if controller:
            self.control = Controller(
                html_embeddings_file=html_embeddings,
                word_embeddings_file=word_embeddings,
            )
        if vectorizer:
            self.vectorizer = self.control.vectorizer

