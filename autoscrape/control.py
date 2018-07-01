# -*- coding: UTF-8 -*-

from .web import Scraper

class Controller(object):
    """
    High-level control for scraping a web page. This allows us to control
    all of the possible scraper commands in an automated way, using a set
    of indices instead of tags. This way we can present vectors of options
    to a ML model.
    """
    def __init__(self):
        """
        Set up our WebDriver and misc utilities.
        """
        self.scraper = Scraper()
        self.tags = []

    def initialize(self, url):
        """
        Instantiate a web scraper, given a starting point URL.
        """
        self.scraper.fetch(url)
        self.tags = self.scraper.get_tags()

    def select_link(self, index):
        tag = self.tag[index]
        self.scraper.click(tag)

    def input(self, index, chars):
        tag = self.tag[index]
        self.scraper.input(tag, chars)

    def submit(self, index):
        tag = self.tag[index]
        self.scraper.submit(tag)

