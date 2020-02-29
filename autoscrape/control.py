# -*- coding: UTF-8 -*-
import time
import logging

from autoscrape.backends.requests.browser import RequestsBrowser
from autoscrape.vectorization.text import TextVectorizer

# backends/vectorizers with optional dependencies
try:
    from autoscrape.vectorization.ebmeddings import EmbeddingsVectorizer
except ModuleNotFoundError:
    pass

try:
    from autoscrape.backends.selenium.browser import SeleniumBrowser
except ModuleNotFoundError:
    pass

try:
    from autoscrape.backends.warc.browser import WARCBrowser
except ModuleNotFoundError:
    pass


logger = logging.getLogger('AUTOSCRAPE')


class Controller:
    """
    High-level control for scraping a web page. This allows us to control
    all of the possible scraper commands in an automated way, using a set
    of indices instead of tags. This way we can present vectors of options
    to a ML model. This abstraction also returns feature matrices for pages
    and elements on the webpage.
    """

    def __init__(self, leave_host=False, driver="Firefox", browser_binary=None,
                 remote_hub="http://localhost:4444/wd/hub", output=None,
                 form_submit_natural_click=False, form_submit_wait=5,
                 warc_index_file=None, warc_directory=None,
                 load_images=False, show_browser=False,
                 html_embeddings_file=None, word_embeddings_file=None,
                 backend="selenium", vectorizer="text"):
        """
        Set up our WebDriver and misc utilities.
        """
        Browser = None
        if backend == "selenium":
            Browser = SeleniumBrowser
        elif backend == "requests":
            Browser = RequestsBrowser
        elif backend == "warc":
            Browser = WARCBrowser
        else:
            raise NotImplementedError(
                "No backend found: %s" % (backend)
            )

        self.scraper = Browser(
            leave_host=leave_host, driver=driver,
            browser_binary=browser_binary, remote_hub=remote_hub,
            form_submit_natural_click=form_submit_natural_click,
            form_submit_wait=form_submit_wait,
            warc_index_file=warc_index_file, warc_directory=warc_directory,
            load_images=load_images, show_browser=show_browser,
            output=output,
        )

        Vectorizer = None
        if vectorizer == "text":
            self.vectorizer = TextVectorizer(
                scraper=self.scraper, controller=self
            )
        elif vectorizer == "embeddings":
            self.vectorizer = EmbeddingsVectorizer(
                scraper=self.scraper, controller=self,
                html_embeddings_file=html_embeddings_file,
                word_embeddings_file=word_embeddings_file,
            )
        else:
            raise NotImplementedError(
                "No vectorizer found: %s" % (vectorizer)
            )

        self.clickable = []
        # simply a list of form tags, each forms input contents is
        # contained in the self.inputs multi-dimensional array, below
        self.forms = []
        # this expands into the following format:
        # [ form_tag:
        #   [
        #     [text input tags...],
        #     [select input tags...],
        #     [checkbox input tags...]
        #   ],
        #   other forms ...,
        # ]
        self.inputs = []

    def load_indices(self):
        logger.debug("[.] Loading page vectors...")
        self.clickable = self.scraper.get_clickable()
        forms_dict = self.scraper.get_forms()
        self.forms = list(forms_dict.keys())
        self.inputs = [tags for tags in forms_dict.values()]
        self.buttons = self.scraper.get_buttons()

        # logger.debug("Clickable links: %s" % (len(self.clickable)))
        # for i in range(len(self.clickable)):
        #     t = self.clickable[i]
        #     elem = self.scraper.element_by_tag(t)
        #     text = ""
        #     if elem:
        #         text = elem.text.replace("\n", " ")
        #     logger.debug("  %s - ...%s, %s" % (i, t[-25:], text))

        # logger.debug("Forms: %s:" % (len(self.forms)))
        # for i in range(len(self.forms)):
        #     t = self.forms[i]
        #     text = ""
        #     elem = self.scraper.element_by_tag(t)
        #     if elem:
        #         text = elem.text.replace("\n", " ")
        #     logger.debug("  %s - ...%s, %s" % (i, t[-25:], text))

        # logger.debug("Inputs: %s" % (len(self.inputs)))
        # for i in range(len(self.inputs)):
        #     input_group = self.inputs[i]
        #     for itype_ix in range(len(input_group)):
        #         for t in input_group[itype_ix]:
        #             elem = self.scraper.element_by_tag(t)
        #             text = ""
        #             placeholder = ""
        #             if elem:
        #                 text = elem.text.replace("\n", " ")
        #                 placeholder = elem.get_attribute("placeholder")
        #             logger.debug("  %s - ...%s, %s, %s" % (
        #                 i, t[-25:], text, placeholder))

        # logger.debug("Buttons: %s" % (len(self.buttons)))
        # for i in range(len(self.buttons)):
        #     t = self.buttons[i]
        #     elem = self.scraper.element_by_tag(t)
        #     text = ""
        #     value = ""
        #     if elem:
        #         text = elem.text.replace("\n", " ")
        #         value = elem.get_attribute("value")
        #     logger.debug("  %s - ...%s, %s, %s" % (i, t[-25:], text, value))

    def initialize(self, url):
        """
        Instantiate a web scraper, given a starting point URL. Also
        gets the links for the current page and sets its tag array.
        """
        self.scraper.fetch(url, initial=True)
        self.load_indices()

    def select_link(self, index):
        if index >= len(self.clickable):
            logger.error(
                "[!] Critical error: link index exceeds clickable length."
            )
            return False
        tag = self.clickable[index]
        clicked = self.scraper.click(tag)
        if clicked:
            self.load_indices()
        return clicked

    def select_button(self, index, iterating_form=False):
        tag = self.buttons[index]
        clicked = self.scraper.click(tag, iterating_form=iterating_form)
        if clicked:
            self.load_indices()
        return clicked

    def input(self, form_ix, index, chars):
        """
        Add some string to a text input under a given form.
        """
        tag = self.inputs[form_ix][0][index]
        self.scraper.input(tag, chars)

    def input_select_option(self, form_ix, index, option_str):
        """
        Select an option for a select input under a given form.
        """
        tag = self.inputs[form_ix][1][index]
        self.scraper.input_select_option(tag, option_str)

    def input_checkbox(self, form_ix, index, to_check):
        """
        Check/uncheck a checkbox input under a given form.
        """
        tag = self.inputs[form_ix][2][index]
        self.scraper.input_checkbox(tag, to_check)

    def input_date(self, form_ix, index, chars):
        """
        Select a date from an input type="date". String needs to
        be in the MM-DD-YYYY format.
        """
        tag = self.inputs[form_ix][3][index]
        self.scraper.input(tag, chars)

    def submit(self, index):
        tag = self.forms[index]
        self.scraper.submit(tag)
        self.load_indices()

    def back(self):
        self.scraper.back()
        self.load_indices()
