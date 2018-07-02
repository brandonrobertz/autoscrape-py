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
        self.clickabke = []
        self.inputs = []
        self.forms = []

    def initialize(self, url):
        """
        Instantiate a web scraper, given a starting point URL. Also
        gets the links for the current page and sets its tag array.
        """
        self.scraper.fetch(url)
        self.clickable = self.scraper.get_clickable()
        # TODO: form-indexed inputs
        # self.inputs = self.scraper.get_inputs()
        # self.forms = self.scraper.get_forms()

    def select_link(self, index):
        tag = self.clickable[index]
        self.scraper.click(tag)

    def input(self, index, chars):
        tag = self.inputs[index]
        self.scraper.input(tag, chars)

    def submit(self, index):
        tag = self.forms[index]
        self.scraper.submit(tag)

    def page_vector(self):
        """
        Get feature vector from currently loaded page. This should
        be used to determine what type of page we're on and what action
        we ought to take (continue crawl, enter input, scrape structured
        data, etc).
        """
        pass

    def link_vectors(self):
        """
        Get a matrix of link vectors. These describe the text of the link
        in a way that a ML algorithm could decide how to prioritize the
        search pattern.
        """
        pass

