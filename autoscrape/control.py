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

    def __init__(self, html_embeddings_file=None, word_embeddings_file=None,
                 leave_host=False, driver="Firefox",
                 form_submit_natural_click=False, form_submit_wait=5,
                 load_images=False, headless=True):
        """
        Set up our WebDriver and misc utilities.
        """
        self.vectorizer = Vectorizer(
            html_embeddings_file=html_embeddings_file,
            word_embeddings_file=word_embeddings_file,
        )
        self.scraper = Scraper(
            leave_host=leave_host, driver=driver,
            form_submit_natural_click=form_submit_natural_click,
            form_submit_wait=form_submit_wait,
            load_images=load_images, headless=headless
        )
        self.clickable = []
        self.forms = []
        self.inputs = []

    def load_indices(self):
        logger.debug("Loading page vectors...")
        self.clickable = self.scraper.get_clickable()
        forms_dict = self.scraper.get_forms()
        self.forms = list(forms_dict.keys())
        self.inputs = [ tags for tags in forms_dict.values() ]
        self.buttons = self.scraper.get_buttons()

        logger.debug("Clickable links: %s" % (len(self.clickable)))
        for i in range(len(self.clickable)):
            t = self.clickable[i]
            elem = self.scraper.lookup_by_tag(t)
            text = ""
            if elem:
                text = elem.text.replace("\n", " ")
            logger.debug("  %s - ...%s, %s" % (i, t[-25:], text))

        logger.debug("Forms: %s:" % (len(self.forms)))
        for i in range(len(self.forms)):
            t = self.forms[i]
            text = ""
            elem = self.scraper.lookup_by_tag(t)
            if elem:
                text = elem.text.replace("\n", " ")
            logger.debug("  %s - ...%s, %s" % (i, t[-25:], text))

        logger.debug("Inputs: %s" % (len(self.inputs)))
        for i in range(len(self.inputs)):
            input_group = self.inputs[i]
            for t in input_group:
                elem = self.scraper.lookup_by_tag(t)
                text = ""
                placeholder = ""
                if elem:
                    text = elem.text.replace("\n", " ")
                    placeholder = elem.get_attribute("placeholder")
                logger.debug("  %s - ...%s, %s, %s" % (
                    i, t[-25:], text, placeholder))

        logger.debug("Buttons: %s" % (len(self.buttons)))
        for i in range(len(self.buttons)):
            t = self.buttons[i]
            elem = self.scraper.lookup_by_tag(t)
            text = ""
            value = ""
            if elem:
                text = elem.text.replace("\n", " ")
                value = elem.get_attribute("value")
            logger.debug("  %s - ...%s, %s, %s" % (i, t[-25:], text, value))

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

    def page_vector(self, type="embeddings"):
        """
        Get feature vector from currently loaded page. This should
        be used to determine what type of page we're on and what action
        we ought to take (continue crawl, enter input, scrape structured
        data, etc).
        """
        if type == "embeddings":
            html = self.scraper.page_html
            text = self.scraper.element_text()
            # this means use the root of the page
            element = None
            return self.vectorizer.vectorize(html, text, element)

    def form_vectors(self, type="text"):
        """
        Get a feature vector representing the forms on a page. This ought
        to be used in cases where the model indicates the page may be a
        search page, but where there are multiple forms. Or where you
        just want to determine if a form is interactive data search.
        Another alternative strategy would be to try the search and then
        look at the next page.
        """
        logger.debug("Loading form vectors")
        form_data = []
        if type == "text":
            for tag in self.forms:
                form = self.scraper.lookup_by_tag(tag)
                txt = self.scraper.element_text(form)
                if txt:
                    form_data.append(txt)

        return form_data

    def button_vectors(self, type="text"):
        logger.debug("Building button vectors")
        buttons_data = []
        if type == "text":
            for tag in self.buttons:
                btn = self.scraper.lookup_by_tag(tag)
                value = ""
                if btn:
                    value = btn.get_attribute("value")
                text = []
                if value:
                    text.append(value)
                if btn and btn.text:
                    text.append(btn.text)
                logger.debug("  %s => value: %s, text: %s" % (
                    tag[-25:], value, text))
                buttons_data.append(" ".join(text))
        return buttons_data

    def link_vectors(self, type="text"):
        """
        Get a matrix of link vectors. These describe the text of the link
        in a way that a ML algorithm could decide how to prioritize the
        search pattern.
        """
        logger.debug("Building link vectors")
        buttons_data = []
        if type == "text":
            for i in range(len(self.clickable)):
                t = self.clickable[i]
                elem = self.scraper.lookup_by_tag(t)
                text = ""
                if elem:
                    text = elem.text.replace("\n", " ")
                else:
                    logger.warn("Link element couldn't be found: %s" % t)
                buttons_data.append(text)
        return buttons_data

