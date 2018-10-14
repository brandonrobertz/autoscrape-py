# -*- coding: UTF-8 -*-
import time
import logging
import re
import urllib.request

import selenium
from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException, UnexpectedAlertPresentException,
    StaleElementReferenceException, TimeoutException,
    NoSuchElementException, ElementNotInteractableException,
    InvalidElementStateException,
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from .tags import Tagger
from .search.graph import Graph


logger = logging.getLogger('AUTOSCRAPE')


class Scraper(object):

    def __init__(self, driver="Firefox", leave_host=False, load_images=False,
                 form_submit_natural_click=False, form_submit_wait=5,
                 show_browser=False, remote_hub="http://localhost:4444/wd/hub"):
        # Needs geckodriver:
        # https://github.com/mozilla/geckodriver/releases
        # Version 0.20.1 is recommended as of 14/07/2018
        if driver == "Firefox":
            firefox_options = webdriver.firefox.options.Options()
            if not show_browser:
                logger.debug("Headless mode enabled")
                firefox_options.add_argument("--headless")
            firefox_profile = webdriver.FirefoxProfile()
            if not load_images:
                # disable images
                firefox_profile.set_preference(
                    'permissions.default.image', 2
                )
            #  disable flash
            firefox_profile.set_preference(
                'dom.ipc.plugins.enabled.libflashplayer.so', 'false'
            )
            firefox_profile.set_preference(
                'security.fileuri.strict_origin_policy', 'false'
            )
            self.driver = webdriver.Firefox(
                firefox_options=firefox_options,
                firefox_profile=firefox_profile,
            )

        # this requires chromedriver to be on the PATH
        # if using chromium and ubuntu, apt install chromium-chromedriver
        elif driver == "Chrome":
            chrome_options = webdriver.ChromeOptions()
            if not show_browser:
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--window-size=1920x1080")
            prefs = {
                "profile.managed_default_content_settings.images":2
            }
            chrome_options.add_experimental_option("prefs",prefs)
            self.driver = webdriver.Chrome(chrome_options=chrome_options)

        elif driver == "remote":
            self.driver = webdriver.Remote(
                command_executor=remote_hub,
                desired_capabilities={
                    "browserName": "chrome",
                    "goog:chromeOptions": {
                        "args": [
                            "--disable-logging",
                            "--headless",
                            "--window-size=1920x1080",
                        ],
                        "prefs": {
                            "profile.managed_default_content_settings.images": 2
                        },
                        "extensions": [],
                    }
                })

        # set of clicked elements
        self.visited = set()
        # queue of the path that led us to the current page
        # this is in the form of (command, *args, **kwargs)
        self.path = []
        # tree building
        self.graph = Graph()
        # sometimes the firefox driver loses its pipe to the browser. in
        # these cases, we can retry this number of times
        self.broken_pipe_retries = 3
        # setting to False, ensures crawl will stay on same host
        self.leave_host = leave_host
        # characters that need to be escaped if found inside an ID tag
        self.css_escapables = ".:"
        self.form_submit_natural_click=form_submit_natural_click
        self.form_submit_wait=form_submit_wait

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
                    logger.debug(msg % self.broken_pipe_retries)
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
        logger.debug("Waiting for page to load...")
        script = "return document.readyState;"
        result = self.driver_exec(driver.execute_script, script)
        return result == "complete"

    def loadwait(self, fn, *args, **kwargs):
        """
        Run a driver interaction function, wait for the page to
        become ready, and handle any broken pipe errors
        """
        wait_for_stale_time = 10 # seconds
        start = time.time()
        check_alerts = False
        if "check_alerts" in kwargs:
            check_alerts = kwargs["check_alerts"]
            del kwargs["check_alerts"]

        # get any element as a reference for staleness check
        elem = self.driver.find_element_by_xpath("//*")

        self.driver_exec(fn, *args, **kwargs)
        time.sleep(1)

        if check_alerts:
            logger.debug("Checking for popup alerts...")
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

        stale_check_max_times = 10.0
        stale_check_times = 0
        while stale_check_times < stale_check_max_times:
            try:
                elem.text
            except StaleElementReferenceException:
                logger.debug("Stale element found! Loading complete.")
                break
            stale_check_times += 1
            time.sleep(wait_for_stale_time / stale_check_max_times)

        # wait for the page to become ready, up to 30s, checks every 0.5s
        wait = WebDriverWait(self.driver, 30)
        wait.until(self.wait_check)
        t = time.time() - start
        logger.debug("Page wait for load check succeeded in %s" % t)

    def scrolltoview(self, elem):
        """
        Scroll to an element before we interact with it.
        """
        script = "arguments[0].scrollIntoView();"
        try:
            self.driver_exec(self.driver.execute_script, script, elem)
        except ElementNotInteractableException as e:
            pass

    def fetch(self, url):
        """
        Fetch a page from a given URL (entry point, typically). Most of
        the time we just want to click a link or submit a form using
        webdriver.
        """
        logger.info("Fetching %s" % url)
        self.loadwait(self.driver.get, url)
        self.path.append(("fetch", (url,), {}))
        node = "Fetch, url: %s" % url
        self.graph.add_root_node(node, url=url, action="fetch")

    def back(self):
        logger.debug("Going back...")
        self.loadwait(self.driver.back)
        self.path.pop()
        self.graph.move_to_parent()

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
        inside_id = False
        # escaping logic
        newtag = ""
        for c in tag:
            if c == "#":
                inside_id = True
                newtag += c
                continue

            # end of ID
            elif inside_id and re.search("\s", c):
                inside_id = False

            elif inside_id and c in self.css_escapables:
                for escapable in self.css_escapables:
                    c = "\%s" % escapable

            newtag += c

        if newtag != tag:
            logger.debug("Original tag: %s, newtag: %s" % (tag, newtag))
            tag = newtag

        try:
            return self.driver_exec(
                self.driver.find_element_by_css_selector, tag
            )
        except Exception as e:
            msg = "Error finding element for tag %s. Error: %s"
            logger.error(msg % (tag, e))

    def elem_stats(self, elem):
        # position  = self.driver_exec(elem.location)
        # css_vis   = self.driver_exec(elem.value_of_css_property, "visibility")
        # css_dis   = self.driver_exec(elem.value_of_css_property, "display")
        # displayed = self.driver_exec(elem.is_displayed)
        # enabled   = self.driver_exec(elem.is_enabled)
        # size      = self.driver_exec(elem.size)
        # text      = self.driver_exec(elem.text)
        # logger.debug("  element position %s" % position)
        # logger.debug("  displayed: %s" % displayed)
        # logger.debug("  enabled: %s" % enabled)
        # logger.debug("  size: %s" % size)
        # logger.debug("  css visibility: %s" % css_vis)
        # logger.debug("  css display: %s" % css_dis)
        # logger.debug("  text: %s" % text.replace("\n", "\\n"))
        pass

    def click(self, tag, iterating_form=False):
        """
        Click an element by a given tag. Returns True if the link
        hasn't been visited and was actually clicked.
        """
        logger.debug("Attempting to click tag %s" % tag)

        elem = self.lookup_by_tag(tag)
        if not elem:
            logger.warn("Element by tag not found. Tag: %s" % tag)
            return False

        name = self.driver_exec(elem.tag_name)
        onclick = self.driver_exec(elem.get_attribute, "onclick")
        href = self.driver_exec(elem.get_attribute, "href")
        hash = "%s|%s|%s" % (href, onclick, name)
        text = self.driver_exec(elem.text)
        if hash in self.visited and not iterating_form:
            logger.debug("Hash visited: %s" % hash)
            return False

        self.visited.add(hash)
        self.disable_target(elem)
        self.scrolltoview(elem)
        self.elem_stats(elem)

        try:
            self.loadwait(elem.click)
        except Exception as e:
            logger.error("Error clicking %s: %s" % (href, e))
            return False

        self.path.append((
            "click", (tag,), {"iterating_form": iterating_form}
        ))
        node = "Click, text: %s, hash: %s, tag: %s" % (text, hash, tag)
        node_meta = {
            "click": tag,
            "click_text": text,
            "click_iterating_form": iterating_form,
        }
        self.graph.add_node(
            node,
            **node_meta
        )
        self.graph.move_to_node(node)
        return True

    def expand_key_substitutions(self, input):
        """
        This split an input string into a series of either
        plain text chunks of webdriver Key objects.
        """
        replacements = {
            "[:left:]": Keys.ARROW_LEFT,
            "[:right:]": Keys.ARROW_RIGHT,
            "[:down:]": Keys.ARROW_DOWN,
            "[:up:]": Keys.ARROW_UP,
            "[:enter:]": Keys.ENTER,
        }
        split_replacements = re.split(
            "(\[:left:\]|\[:right:\]|\[:down:\]|\[:up:\]|\[:enter:\])",
            input
        )
        logger.debug("Split replacements input string: %s" % split_replacements)
        for chunk in split_replacements:
            if not chunk:
                continue
            if chunk in replacements:
                yield replacements[chunk]
                continue
            yield chunk

    def input(self, tag, input):
        """
        Enter some input into an element by a given tag.
        """
        logger.info("Injecting text \"%s\" to input" % (input))
        elem = self.lookup_by_tag(tag)
        self.driver_exec(self.scrolltoview, elem)
        self.elem_stats(elem)
        try:
            self.driver_exec(elem.clear)
        except ElementNotInteractableException as e:
            pass
        # this handles date fields which aren't clearable
        except InvalidElementStateException as e:
            pass
        for inp in self.expand_key_substitutions(input):
            elem.send_keys(inp)
        self.path.append(("input", (tag,input,), {}))
        action = {
            "action": "input",
            "text": input,
            "tag": tag,
        }
        self.graph.add_action_to_current(action)

    def input_select_option(self, tag, option_str):
        """
        Select an input select option based on its visible string value.
        """
        logger.info("Selecting option %s" % (option_str))
        elem = self.lookup_by_tag(tag)
        self.driver_exec(self.scrolltoview, elem)
        # TODO: wrap in driver_exec after testing
        select = Select(elem)
        # select by visible text
        select.select_by_visible_text(option_str)
        self.path.append(("input_select_option", (tag,option_str,), {}))
        action = {
            "action": "input_select_option",
            "option": option_str,
            "tag": tag,
        }
        self.graph.add_action_to_current(action)

    def input_checkbox(self, tag, to_check):
        """
        Check, uncheck, or don't touch an input checkbox, based
        on its current checked value.
        """
        logger.info("Checking to checkbox selected=%s" % (to_check))
        elem = self.lookup_by_tag(tag)
        self.driver_exec(self.scrolltoview, elem)
        # TODO: wrap in driver_exec after testing
        if elem.is_selected() != to_check:
            elem.click()
            self.driver_exec(elem.clear)
        self.path.append(("input_checkbox", (tag,to_check,), {}))
        action = {
            "action": "input_checkbox",
            "checked?": to_check,
            "tag": tag,
        }
        self.graph.add_action_to_current(action)

    def click_at_position_over_element(self, elem):
        """
        Perform a "natural" click of an element, so that if there are
        any parent listeners, they will also be triggered.
        """
        logger.info("Performing a 'natural' click")
        from selenium.webdriver.common.action_chains import ActionChains
        ac = ActionChains(self.driver)
        x_off = 0
        y_off = 0
        ac.move_to_element(elem).move_by_offset(x_off, y_off).click().perform()

    def submit(self, tag):
        """
        Submit a form from a given tag. Assumes all inputs are filled.
        """
        logger.info("Submitting form by tag: %s" % tag)
        form = self.lookup_by_tag(tag)
        self.elem_stats(form)
        self.driver_exec(self.scrolltoview, form)

        # try to find a Submit input button
        sub = None
        try:
            sub = self.driver_exec(
                form.find_element_by_xpath,
                "//input[@type='submit']"
            )
            logger.debug("Form submit input button: %s" % sub)
        except NoSuchElementException as e:
            pass

        # try to find a Submit link
        # NOTE: instead of using xpath we're going to do a manual search.
        # this is due to the lack of a regex xpath matcher in some browsers
        # The below should be the functional equivaliant of something like:
        #   xpath = //a[matches(., 'submit')
        if not sub:
            try:
                possible_subs = self.driver_exec(
                    form.find_elements_by_xpath,
                    "//a"
                )
                els = [ el for el in possible_subs if "submit" in el.text.lower() ]
                if els:
                    sub = els[0]
                    logger.debug("Form submit link: %s" % sub)
            except NoSuchElementException as e:
                pass

        # attempt to click on the button, if this fails, we will
        # try to perform a form submit
        sub_failure = False
        if sub:
            try:
                if self.form_submit_natural_click:
                    self.click_at_position_over_element(sub)
                else:
                    self.loadwait(sub.click)
            except Exception as e:
                sub_failure = True
                logger.warn("Failure to click on submit button/link: %s" % e)

        # otherwise, try to submit the form itself
        if not sub or sub_failure:
            logger.debug("Using form.submit selenium shim")
            self.loadwait(form.submit, check_alerts=True)

        self.path.append(("submit", (tag,), {}))
        node = "Submit, tag: %s" % (tag)
        node_meta = {
            "submit": tag,
            "submit_natural_click": self.form_submit_natural_click,
        }
        self.graph.add_node(node, **node_meta)

        # TODO: better way to wait for this, post-alert clicked
        if self.form_submit_wait:
            logger.debug(
                "Forcing post-submit wait period of %ss" %
                self.form_submit_wait
            )
            time.sleep(self.form_submit_wait)

        # move to the node if we're successful (got here, so we assume)
        self.graph.move_to_node(node)

    @property
    def page_html(self):
        """
        Get the current DOM HTML of the page.
        """
        return self.driver_exec(self.driver.page_source)

    def download_page(self, url):
        """
        Fetch the given url, returning a byte stream of the page data. This
        really is only useful in situations where the scraper is on a binary
        filetype, such as PDF, etc.

        Note that we're doing this as opposed to some XHR thing inside the
        selenium driver due to CORS issues.
        """
        logger.info("Fetching non-HTML page directly: %s" % url)
        response = urllib.request.urlopen(url)
        data = response.read()
        action = {
            "action": "download_page",
            "url": url,
        }
        self.graph.add_action_to_current(action)
        return data

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
        # TODO: this is a major bottleneck. find a way
        # to ensure all text of children is extracted
        # (non-duplicately via descendants) in a more
        # performant way
        elems = element.find_elements_by_xpath(".//*")
        text = []
        for el in elems:
            try:
                txt = el.text
                if txt:
                    text.append(txt.strip())
            except Exception as e:
                logger.error("Error getting text element: %s, Err: %s" % (
                    el, e))

            placeholder = el.get_attribute("placeholder")
            if placeholder:
                text.append(placeholder.strip())

        logger.debug("Element texts: %s" % text)
        return " ".join(text)

    def get_clickable(self, type=None):
        """
        Get tags, by type (optional), for the currently loaded page.
        """
        current_url = self.driver_exec(self.page_url)
        tagger = Tagger(
            driver=self.driver, current_url=current_url,
            leave_host=self.leave_host,
        )
        return tagger.get_clickable()

    def get_forms(self):
        current_url = self.driver_exec(self.page_url)
        tagger = Tagger(
            driver=self.driver, current_url=current_url,
            leave_host=self.leave_host,
        )
        forms_dict = tagger.get_forms()
        logger.debug("page forms: %s" % forms_dict)
        return forms_dict

    def get_buttons(self):
        current_url = self.driver_exec(self.page_url)
        tagger = Tagger(
            driver=self.driver, current_url=current_url,
            leave_host=self.leave_host,
        )
        return tagger.get_buttons()

    def close(self):
        self.driver_exec(self.driver.close)

