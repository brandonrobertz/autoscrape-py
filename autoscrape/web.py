# -*- coding: UTF-8 -*-
import time
import logging

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .tags import Tagger


logger = logging.getLogger('AUTOSCRAPE')


class Scraper(object):

    def __init__(self):
        # this requires chromedriver to be on the PATH
        # if using chromium and ubuntu, apt install chromium-chromedriver
        self.driver = webdriver.Chrome()
        self.visited = set()

    def fetch(self, url):
        """
        Fetch a page from a given URL (entry point, typically). Most of the time
        we just want to click a link or submit a form using webdriver.
        """
        logger.debug("Fetching %s" % url)
        self.driver.get(url)
        time.sleep(2)

    def back(self):
        logger.debug("Going back...")
        self.driver.back()
        time.sleep(2)

    def disable_target(self, elem):
        """
        Look for targets either non-blank or not _self and set to _self.
        This needs to be a JavaScript injected script with element as param.
        """
        target = elem.get_attribute("target")
        if not target or target == "_self":
            return

        self.driver.execute_script("arguments[0].target='_self';", elem)

    def click(self, tag):
        """
        Click an element by a given tag. Returns True if the link
        hasn't been visited and was actually clicked.
        """
        logger.debug("Click tag %s" % tag)
        elem = self.driver.find_element_by_css_selector(tag)
        href = elem.get_attribute("href")
        logger.debug("  href %s" % href)
        onclick = elem.get_attribute("onclick")
        name = elem.tag_name
        hash = "%s|%s|%s" % (href, onclick, name)
        if hash in self.visited:
            return False

        self.visited.add(hash)
        logger.debug("Clicked hash %s" % hash)
        self.disable_target(elem)
        elem.click()
        time.sleep(2)
        return True

    def input(self, tag, input):
        """
        Enter some input into an element by a given tag.
        """
        logger.debug("Inputting %s into tag %s" % (input, tag))
        elem = self.driver.find_element_by_css_selector(tag)
        elem.send_keys(input)

    def submit(self, tag):
        """
        Submit a form from a given tag. Assumes all inputs are filled.
        """
        logger.debug("Submitting tag %s" % tag)
        elem = self.driver.find_element_by_css_selector(tag)
        elem.submit()
        time.sleep(2)

    @property
    def page_html(self):
        return self.driver.page_source

    @property
    def page_url(self):
        return self.driver.current_url

    def get_tags(self, type=None):
        """
        Get tags, by type (optional), for the currently loaded page.
        """
        tagger = Tagger(driver=self.driver, current_url=self.page_url)
        return tagger.get_tags()

