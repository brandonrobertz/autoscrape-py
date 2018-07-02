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

    def __init__(self, driver="Firefox"):
        # Needs geckodriver: https://github.com/mozilla/geckodriver/releases
        if driver == "Firefox":
            self.driver = webdriver.Firefox()
        # this requires chromedriver to be on the PATH
        # if using chromium and ubuntu, apt install chromium-chromedriver
        elif driver == "Chrome":
            chromeOptions = webdriver.ChromeOptions()
            prefs = {
                "profile.managed_default_content_settings.images":2
            }
            chromeOptions.add_experimental_option("prefs",prefs)
            self.driver = webdriver.Chrome(chrome_options=chromeOptions)
        self.visited = set()

    def wait_check(self, driver):
        script = "return document.readyState"
        result = driver.execute_script(script)
        return result == "complete"

    def loadwait(self, fn, *args, **kwargs):
        fn(*args, **kwargs)
        wait = WebDriverWait(self.driver, 30)
        wait.until(self.wait_check)

    def scrolltoview(self, elem):
        script = "arguments[0].scrollIntoView()"
        result = self.driver.execute_script(script, elem)

    def fetch(self, url):
        """
        Fetch a page from a given URL (entry point, typically). Most of the time
        we just want to click a link or submit a form using webdriver.
        """
        logger.debug("Fetching %s" % url)
        self.loadwait(self.driver.get, url)

    def back(self):
        logger.debug("Going back...")
        self.loadwait(self.driver.back)

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
        name = elem.tag_name
        position = elem.location
        css_vis = elem.value_of_css_property("visibility")
        css_dis = elem.value_of_css_property("display")
        href = elem.get_attribute("href")
        onclick = elem.get_attribute("onclick")
        logger.debug("  name %s" % name)
        logger.debug("  element position %s" % position)
        logger.debug("  displayed: %s" % elem.is_displayed())
        logger.debug("  enabled: %s" % elem.is_enabled())
        logger.debug("  size: %s" % elem.is_enabled())
        logger.debug("  css visibility: %s" % css_vis)
        logger.debug("  css display: %s" % css_dis)
        logger.debug("  href %s" % href)
        logger.debug("  onclick %s" % onclick)

        hash = "%s|%s|%s" % (href, onclick, name)
        if hash in self.visited:
            return False

        self.visited.add(hash)
        logger.debug("Clicked hash %s" % hash)
        self.disable_target(elem)
        self.scrolltoview(elem)
        try:
            self.loadwait(elem.click)
        except Exception as e:
            logger.error("Error clicking %s: %s" % (href, e))
            return False

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
        self.loadwait(elem.submit)

    @property
    def page_html(self):
        return self.driver.page_source

    @property
    def page_url(self):
        return self.driver.current_url

    def get_clickable(self, type=None):
        """
        Get tags, by type (optional), for the currently loaded page.
        """
        tagger = Tagger(driver=self.driver, current_url=self.page_url)
        return tagger.get_clickable()

