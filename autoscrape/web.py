# -*- coding: UTF-8 -*-
import time
import logging

import selenium
from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException, UnexpectedAlertPresentException,
    StaleElementReferenceException, TimeoutException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .tags import Tagger


logger = logging.getLogger('AUTOSCRAPE')


class Scraper(object):

    def __init__(self, driver="Firefox"):
        # Needs geckodriver:
        # https://github.com/mozilla/geckodriver/releases
        # Version 0.20.1 is recommended as of 14/07/2018
        if driver == "Firefox":
            firefox_profile = webdriver.FirefoxProfile()
            # disable images
            firefox_profile.set_preference(
                'permissions.default.image', 2
            )
            # disable flash
            firefox_profile.set_preference(
                'dom.ipc.plugins.enabled.libflashplayer.so', 'false'
            )
            self.driver = webdriver.Firefox(
                firefox_profile=firefox_profile
            )
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
        # sometimes the firefox driver loses its pipe to the browser. in
        # these cases, we can retry this number of times
        self.broken_pipe_retries = 3

    def __del__(self):
        self.driver_exec(self.driver.close)

    def driver_exec(self, fn, *args, **kwargs):
        """
        Wrap all driver function calls with broken pipe handling. This
        is a workaround for geckodriver's problem of killing connections
        or lack of persistent connection. Geckodriver 0.20.1 doesn't seem
        to have the issue ... as it appears to be related to a very
        short keep-alive in 0.21.0.
        """
        pipe_retries = 0
        while True:
            try:
                return fn(*args, **kwargs)
            except BrokenPipeError as e:
                if pipe_retries > self.broken_pipe_retries:
                    msg = "Exceeded max broken pipe retries: %s"
                    logger.info(msg % self.broken_pipe_retries)
                    msg = "Broken pipe err. fn: %s, args: %s, kwargs: %s"
                    logger.error(msg % (fn, args, kwargs))
                    raise e
            except TypeError as e:
                if "not callable" in str(e):
                    return self.driver_exec(lambda: fn)
                    # don't increment pipe_retries here. we just need to
                    # convert our property into a callable for the next
                    # iteration
                    continue
                raise e

            pipe_retries += 1

    def wait_check(self, driver):
        """
        This is the check that gets ran to determine whether
        the page is loaded or not.
        """
        script = "return document.readyState;"
        result = self.driver_exec(driver.execute_script, script)
        return result == "complete"

    def loadwait(self, fn, *args, **kwargs):
        """
        Run a driver interaction function, wait for the page to
        become ready, and handle any broken pipe errors
        """
        check_alerts = False
        if "check_alerts" in kwargs:
            check_alerts = kwargs["check_alerts"]
            del kwargs["check_alerts"]

        self.driver_exec(fn, *args, **kwargs)

        if check_alerts:
            try:
                WebDriverWait(self.driver, 1).until(
                    EC.alert_is_present(),
                    'Waiting for alert timed out'
                )
                alert = self.driver.switch_to_alert()
                alert.accept()
                logger.debug("Alert accepted!")
            except TimeoutException:
                pass

        # wait for the page to become ready, up to 30s, checks every 0.5s
        wait = WebDriverWait(self.driver, 30)
        wait.until(self.wait_check)

    def scrolltoview(self, elem):
        """
        Scroll to an element before we interact with it.
        """
        script = "arguments[0].scrollIntoView();"
        self.driver_exec(self.driver.execute_script, script, elem)

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

        script = "arguments[0].target='_self';"
        self.driver_exec(self.driver.execute_script, script, elem)

    def lookup_by_tag(self, tag):
        try:
            return self.driver_exec(
                self.driver.find_element_by_css_selector, tag
            )
        except Exception as e:
            msg = "Error finding element for tag %s. Error: %s"
            logger.error(msg % (tag, e))

    def elem_stats(self, elem):
        position  = self.driver_exec(elem.location)
        css_vis   = self.driver_exec(elem.value_of_css_property, "visibility")
        css_dis   = self.driver_exec(elem.value_of_css_property, "display")
        displayed = self.driver_exec(elem.is_displayed)
        enabled   = self.driver_exec(elem.is_enabled)
        size      = self.driver_exec(elem.size)
        logger.debug("  element position %s" % position)
        logger.debug("  displayed: %s" % displayed)
        logger.debug("  enabled: %s" % enabled)
        logger.debug("  size: %s" % size)
        logger.debug("  css visibility: %s" % css_vis)
        logger.debug("  css display: %s" % css_dis)

    def click(self, tag, iterating_form=False):
        """
        Click an element by a given tag. Returns True if the link
        hasn't been visited and was actually clicked.
        """
        logger.debug("Click tag %s" % tag)
        elem = self.lookup_by_tag(tag)
        if not elem:
            logger.warn("Element by tag not found. Tag: %s" % tag)
            return False

        name = self.driver_exec(elem.tag_name)
        onclick = self.driver_exec(elem.get_attribute, "onclick")
        href = self.driver_exec(elem.get_attribute, "href")
        hash = "%s|%s|%s" % (href, onclick, name)
        if hash in self.visited and not iterating_form:
            logger.warn("Hash visited: %s" % hash)
            return False

        self.elem_stats(elem)
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
        elem = self.lookup_by_tag(tag)
        self.driver_exec(self.scrolltoview, elem)
        self.elem_stats(elem)
        self.driver_exec(elem.clear)
        self.driver_exec(elem.send_keys, input)

    def submit(self, tag):
        """
        Submit a form from a given tag. Assumes all inputs are filled.
        """
        logger.debug("Submitting tag %s" % tag)
        elem = self.lookup_by_tag(tag)
        self.driver_exec(self.scrolltoview, elem)
        self.elem_stats(elem)
        self.loadwait(elem.submit, check_alerts=True)
        # TODO: better way to wait for this, post-alert clicked
        time.sleep(5)

    @property
    def page_html(self):
        return self.driver_exec(self.driver.page_source)

    @property
    def page_url(self):
        return self.driver_exec(self.driver.current_url)

    def element_text(self, element=None):
        """
        Get the text for all elements either under a given element
        or for a whole page (if element == None)
        """
        if element is None:
            element = self.driver
        elems = element.find_elements_by_xpath(".//*")
        text = " ".join([ e.text for e in elems ])
        return text

    def get_clickable(self, type=None):
        """
        Get tags, by type (optional), for the currently loaded page.
        """
        current_url = self.driver_exec(self.page_url)
        tagger = Tagger(driver=self.driver, current_url=current_url)
        return tagger.get_clickable()

    def get_forms(self):
        current_url = self.driver_exec(self.page_url)
        tagger = Tagger(driver=self.driver, current_url=current_url)
        forms_dict = tagger.get_forms()
        return forms_dict

    def get_buttons(self):
        current_url = self.driver_exec(self.page_url)
        tagger = Tagger(driver=self.driver, current_url=current_url)
        return tagger.get_buttons()

