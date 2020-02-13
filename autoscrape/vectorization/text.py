# -*- coding: UTF-8 -*-
import logging


logger = logging.getLogger('AUTOSCRAPE')


class TextVectorizer:
    """
    # for ix, text in link_vectors
    link_vectors = self.control.vectorizer.link_vectors()
    # for ix, text in button_vectors
    button_data = self.control.vectorizer.button_vectors()
    form_vectors = self.control.vectorizer.form_vectors()
    """
    def __init__(self, scraper=None, controller=None):
        self.scraper = scraper
        self.controller = controller

    def page_vector(self, html):
        """
        Get feature vector from currently loaded page. This should
        be used to determine what type of page we're on and what action
        we ought to take (continue crawl, enter input, scrape structured
        data, etc).
        """
        return self.scraper.element_text(None, block=True)

    def form_vectors(self):
        """
        Get a feature vector representing the forms on a page. This ought
        to be used in cases where the model indicates the page may be a
        search page, but where there are multiple forms. Or where you
        just want to determine if a form is interactive data search.
        Another alternative strategy would be to try the search and then
        look at the next page.
        """
        logger.debug("[.] Loading form vectors")
        form_data = []
        for tag in self.controller.forms:
            form = self.scraper.element_by_tag(tag)
            txt = self.scraper.element_text(form, block=True)
            if txt:
                form_data.append(txt)
        return form_data

    def button_vectors(self):
        logger.debug("[.] Building button vectors")
        buttons_data = []
        for tag in self.controller.buttons:
            elem = self.scraper.element_by_tag(tag)
            value = ""
            if elem is not None:
                value = self.scraper.element_value(elem)
            text = []
            if value:
                text.append(value)
            if elem is not None and self.scraper.element_text(elem):
                text.append(self.scraper.element_text(elem))
            logger.debug(" - button value: %s, text: %s" % (value, text))
            buttons_data.append(" ".join(text))
        return buttons_data

    def link_vectors(self):
        """
        Get a matrix of link vectors. These describe the text of the link
        in a way that a ML algorithm could decide how to prioritize the
        search pattern.
        """
        logger.debug("[.] Building link vectors")
        buttons_data = []
        for i in range(len(self.controller.clickable)):
            t = self.controller.clickable[i]
            elem = self.scraper.element_by_tag(t)
            tag_name = self.scraper.element_tag_name(elem)
            text = ""
            if elem is None:
                logger.warn("[!] Link element couldn't be found: %s" % t)
            elif tag_name != "input":
                text = self.scraper.element_text(elem).replace("\n", " ")
            elif tag_name == "input":
                value = self.scraper.element_attr(elem, "value")
                text = value.replace("\n", " ")
            buttons_data.append(text)
        return buttons_data
