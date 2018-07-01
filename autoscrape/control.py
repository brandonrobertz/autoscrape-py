# -*- coding: UTF-8 -*-

from .web import Scraper

class Controller(object):
    """
    High-level control for scraping a web page. This allows us to control
    all of the possible scraper commands in an automated way.
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

    def get_tags(self):
        """
        Return a list of tags for analysis. In the future we may
        want to return word vectors, etc, for our tagged elements.
        """
        return self.tags

    def select_link(self, index):
        tag = self.tag[index]
        self.scraper.click(tag)

    def input(self, index, chars):
        tag = self.tag[index]
        self.scraper.input(tag, chars)

    def submit(self, index):
        tag = self.tag[index]
        self.scraper.submit(tag)

