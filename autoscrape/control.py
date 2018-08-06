# -*- coding: UTF-8 -*-
import time
import logging

from .web import Scraper
from .vectorization import Vectorizer


logger = logging.getLogger('AUTOSCRAPE')


class Controller(object):
    """
    High-level control for scraping a web page. This allows us to control
    all of the possible scraper commands in an automated way, using a set
    of indices instead of tags. This way we can present vectors of options
    to a ML model. This abstraction also returns feature matrices for pages
    and elements on the webpage.
    """

    def __init__(self, html_embeddings_file=None, word_embeddings_file=None):
        """
        Set up our WebDriver and misc utilities.
        """
        self.vectorizer = Vectorizer(
            html_embeddings_file=html_embeddings_file,
            word_embeddings_file=word_embeddings_file,
        )
        self.scraper = Scraper()
        self.clickabke = []
        self.forms = []
        self.inputs = []

    def load_indices(self):
        self.clickable = self.scraper.get_clickable()
        forms_dict = self.scraper.get_forms()
        self.forms = list(forms_dict.keys())
        self.inputs = [ tags for tags in forms_dict.values() ]
        self.buttons = self.scraper.get_buttons()

    def initialize(self, url):
        """
        Instantiate a web scraper, given a starting point URL. Also
        gets the links for the current page and sets its tag array.
        """
        self.scraper.fetch(url)
        self.load_indices()

    def select_link(self, index):
        tag = self.clickable[index]
        clicked = self.scraper.click(tag)
        if clicked:
            self.load_indices()
        return clicked

    def select_button(self, index, iterating_form=False):
        tag = self.buttons[index]
        logger.debug("Clicking button ix: %s, tag: %s" % (
            index, tag))
        clicked = self.scraper.click(tag, iterating_form=iterating_form)
        time.sleep(1)
        if clicked:
            self.load_indices()
        return clicked

    def input(self, form_ix, index, chars):
        tag = self.inputs[form_ix][index]
        self.scraper.input(tag, chars)

    def submit(self, index):
        tag = self.forms[index]
        self.scraper.submit(tag)
        self.load_indices()

    def back(self):
        self.scraper.back()
        self.load_indices()

    def page_vector(self, type="text"):
        """
        Get feature vector from currently loaded page. This should
        be used to determine what type of page we're on and what action
        we ought to take (continue crawl, enter input, scrape structured
        data, etc).
        """
        html = self.scraper.page_html

    def form_vectors(self, type="text"):
        """
        Get a feature vector representing the forms on a page. This ought
        to be used in cases where the model indicates the page may be a
        search page, but where there are multiple forms. Or where you
        just want to determine if a form is interactive data search.
        Another alternative strategy would be to try the search and then
        look at the next page.
        """
        form_data = []
        if type == "text":
            for tag in self.forms:
                form = self.scraper.lookup_by_tag(tag)
                elems = form.find_elements_by_xpath(".//*")
                text = " ".join([ e.text for e in elems ])
                form_data.append(text)

        return form_data

    def button_vectors(self, type="text"):
        buttons_data = []
        print("Buttons", self.buttons)
        if type == "text":
            for tag in self.buttons:
                btn = self.scraper.lookup_by_tag(tag)
                value = btn.get_attribute("value")
                text = "%s %s" % (btn.text, value)
                buttons_data.append(text)
        return buttons_data

    def link_vectors(self):
        """
        Get a matrix of link vectors. These describe the text of the link
        in a way that a ML algorithm could decide how to prioritize the
        search pattern.
        """
        pass

