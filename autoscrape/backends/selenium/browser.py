# -*- coding: utf-8 -*-
import hashlib
import time
import logging
import os
import re
import sys

try:
    from selenium import webdriver
    from selenium.common.exceptions import (
        TimeoutException, StaleElementReferenceException,
        NoSuchElementException, ElementNotInteractableException,
        InvalidElementStateException, WebDriverException,
    )
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
except ModuleNotFoundError:
    # we haven't installed selenium backend deps
    pass

from autoscrape.backends.base.browser import BrowserBase
from autoscrape.backends.selenium.tags import Tagger
from autoscrape.search.graph import Graph


logger = logging.getLogger('AUTOSCRAPE')


class SeleniumBrowser(BrowserBase, Tagger):
    # override a None passed to page_timeout because we need
    # to set an integer value
    DEFAULT_TIMEOUT = 30

    def __init__(self, driver="Firefox", leave_host=False,
                 load_images=False, form_submit_natural_click=False,
                 form_submit_wait=5, output=None, show_browser=False,
                 form_submit_button_selector=None,
                 browser_binary=None, page_timeout=None,
                 remote_hub="http://localhost:4444/wd/hub", **kwargs):
        try:
            webdriver
        except NameError:
            logger.error(
                "Tried to use selenium backend but Selenium isn't"
                " installed. (Hint: pip install autoscrape[selenium-backend])"
                " Exiting."
            )
            sys.exit(1)

        # toggle the various timeouts in selenium
        self.timeout = page_timeout
        if self.timeout is None:
            self.timeout = self.DEFAULT_TIMEOUT

        # Needs geckodriver:
        # https://github.com/mozilla/geckodriver/releases
        # Version 0.20.1 is recommended as of 14/07/2018
        if driver == "Firefox":
            logger.debug(" - Starting Firefox")
            firefox_options = webdriver.firefox.options.Options()
            if not show_browser:
                logger.debug(" - Headless mode enabled")
                # override beause sometimes FF/Selenium/Geckodriver
                # will ignore the headless options
                os.environ["MOZ_HEADLESS"] = "1"
                firefox_options.add_argument("--headless")
                firefox_options.add_argument("-headless")
                firefox_options.headless = True
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
            binary = None
            if browser_binary is not None:
                logger.debug(" - Using binary: %s" % (browser_binary))
                binary = FirefoxBinary(browser_binary)
            self.driver = webdriver.Firefox(
                options=firefox_options,
                firefox_profile=firefox_profile,
                firefox_binary=binary,
            )
            self.driver.set_page_load_timeout(self.timeout)

        # this requires chromedriver to be on the PATH
        # if using chromium and ubuntu, apt install chromium-chromedriver
        elif driver == "Chrome":
            logger.debug(" - Starting Chrome")
            chrome_options = webdriver.ChromeOptions()
            if not show_browser:
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-web-security")
                chrome_options.add_argument("--window-size=1920x1080")
            prefs = {
                "profile.managed_default_content_settings.images": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            if browser_binary is not None:
                logger.debug(" - Using binary: %s" % (browser_binary))
                options.binary_location = browser_binary
            self.driver = webdriver.Chrome(chrome_options=chrome_options)

        elif driver == "remote":
            logger.debug(" - Starting remote browser")
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
        else:
            raise NotImplementedError("No driver found: %s, exiting." % (
                driver
            ))

        # set of clicked elements
        self.visited = set()
        # queue of the path that led us to the current page
        # this is in the form of (command, *args, **kwargs)
        self.path = []
        # store the values of the history stack length (via JS) for use in determining
        # whether or not we actually navigated somewhere. stored in window, hist
        # pairs: [[win_1, 1], ..., [win_N, N]]
        self.history_stack = []
        # used for detecting infinite loop inside a form (if the 'next' button
        # never does disabled once at the end of results)
        self.page_hashes = []
        # tree building
        self.graph = Graph()
        # sometimes the firefox driver loses its pipe to the browser. in
        # these cases, we can retry this number of times
        self.broken_pipe_retries = 3
        # setting to False, ensures crawl will stay on same host
        self.leave_host = leave_host
        # characters that need to be escaped if found inside an ID tag
        self.css_escapables = ".:"
        self.form_submit_natural_click = form_submit_natural_click
        self.form_submit_wait = form_submit_wait
        # selector to locate submit button, overrides all other
        # selection strategies
        self.form_submit_button_selector = form_submit_button_selector

    def _driver_exec(self, fn, *args, **kwargs):
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
                    return self._driver_exec(lambda: fn)
                    # don't increment pipe_retries here. we just need to
                    # convert our property into a callable for the next
                    # iteration
                    continue
                raise e

            pipe_retries += 1

    def __del__(self):
        if hasattr(self, "driver") and self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass

    def _get_history_depth(self):
        """
        Retrieve the browser history depth for use in detecting
        whether or not we actually navigated to a new page.
        """
        script = "return window.history.length;"
        return self._driver_exec(self.driver.execute_script, script)

    def _get_open_windows(self):
        """
        Get the handles of each open browser window and add any new
        ones to the open window stack.
        """
        return self.driver.window_handles

    def _switch_to_window(self, window_id):
        self.driver.switch_to.window(window_id)

    def _switch_to_iframe(self, frame_id):
        self.driver.switch_to.frame(frame_id)

    def _wait_check(self, driver):
        """
        This is the check that gets ran to determine whether
        the page is loaded or not.
        """
        logger.debug(" - Waiting for page to load (document.readyState)...")
        s = time.time()
        script = """
          var callback = arguments[arguments.length - 1];
          setTimeout(callback(document.readyState), %s);
          document.addEventListener('readystatechange', event => {
            console.log(event.target.readyState);
            if (event.target.readyState === 'interactive') {
            }
            else if (event.target.readyState === 'complete') {
              callback(document.readyState);
            }
          });
        """ % (5000)
        result = self._driver_exec(self.driver.execute_async_script, script)
        logger.debug(" - Page loaded in %s seconds" % (time.time() - s))
        return result == "complete"

    def _loadwait(self, fn, *args, **kwargs):
        """
        Run a driver interaction function, wait for the page to
        become ready, and handle any broken pipe errors
        """
        start = time.time()
        check_alerts = False
        if "check_alerts" in kwargs:
            check_alerts = kwargs["check_alerts"]
            del kwargs["check_alerts"]

        # get any element as a reference for staleness check
        elem = self.driver.find_element_by_xpath("//*")

        self._driver_exec(fn, *args, **kwargs)
        time.sleep(1)

        if check_alerts:
            logger.debug("[.] Checking for popup alerts...")
            try:
                WebDriverWait(self.driver, 1).until(
                    EC.alert_is_present(),
                    'Waiting for alert timed out'
                )
                alert = self.driver.switch_to_alert()
                alert.accept()
                logger.debug("[.] Alert accepted!")
            except TimeoutException:
                pass

        # wait for the page to become ready, up to 30s, checks every 0.5s
        logger.debug(" - Performing native WebDriverWait...")
        wait = WebDriverWait(self.driver, self.timeout)
        wait.until(self._wait_check)

        t = time.time() - start
        logger.debug(" - Wait for load succeeded in %s" % t)

    def scrolltoview(self, elem):
        """
        Scroll to an element before we interact with it.
        """
        script = "arguments[0].scrollIntoView();"
        try:
            self._driver_exec(self.driver.execute_script, script, elem)
        except ElementNotInteractableException as e:
            pass

    def fetch(self, url, **kwargs):
        """
        Fetch a page from a given URL (entry point, typically). Most of
        the time we just want to click a link or submit a form using
        webdriver.
        """
        logger.info("[.] Fetching %s" % url)
        self._loadwait(self.driver.get, url)
        self.path.append(("fetch", (url,), {}))

        depth = self._get_history_depth()
        window = self._get_open_windows()[-1]
        self.history_stack.append([window, depth])

        node = "Fetch\n url: %s" % url
        self.graph.add_root_node(node, url=url, action="fetch")

    def back(self):
        logger.info("[+] Going back...")
        logger.debug(" - current path-length=%s path=%s" % (
            len(self.path), self._no_tags(self.path),
        ))

        # only go 'back' if the history depth changed from
        # now to the previous (back) value. if they're the
        # same, we just clicked something inside the page
        if len(self.history_stack) > 1:
            window, depth = self.history_stack.pop()
            prev_win, prev_depth = self.history_stack[-1]
            # same window, we just incremented the history stack once
            if window == prev_win and depth != prev_depth:
                logger.debug(" - History depth changed since last action.")
                # going backward should be the only time we have a
                # frame focused, where we want to be on the main page
                self.driver.switch_to.default_content()
                self._loadwait(self.driver.back)
            # time to close an open window, focus old
            elif window != prev_win:
                logger.debug(" - Going back to previous window")
                # close current window (make sure we've focused proper one)
                self._switch_to_window(window)
                self.driver.close()
                # focus previous one
                self._switch_to_window(prev_win)
        self.path.pop()
        self.graph.move_to_parent()

    def disable_target(self, elem):
        """
        Look for targets either non-blank or not _self and set to _self.
        This needs to be a JavaScript injected script with element as param.
        """
        target = self.element_attr(elem, "target")
        if not target or target == "_self":
            return

        script = "arguments[0].target='_self';"
        self._driver_exec(self.driver.execute_script, script, elem)

    def click(self, tag, iterating_form=False):
        """
        Click an element by a given tag. Returns True if the link
        hasn't been visited and was actually clicked.
        """
        elem = self.element_by_tag(tag)
        if not elem:
            logger.warn("Element by tag not found. Tag: %s" % tag)
            return False

        try:
            wait = WebDriverWait(self.driver, self.timeout)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, tag)))
        except TimeoutException as e:
            pass

        hash_parts = []
        hash_parts.append(self._driver_exec(elem.tag_name))
        href = self._driver_exec(elem.get_attribute, "href")
        hash_parts.append(href)
        hash_parts.append(self._driver_exec(elem.get_attribute, "onclick"))
        text = self._driver_exec(elem.text)
        hash = "|".join([h for h in hash_parts if h])
        logger.debug(" - Link hash : %s" % (hash))

        # only enable this for URL links
        # if href and hash in self.visited and not iterating_form:
        if hash in self.visited and not iterating_form:
            logger.debug("Link already clicked! Hash: %s" % (hash))
            return False

        self.visited.add(hash)
        self.disable_target(elem)
        self.scrolltoview(elem)

        try:
            self._loadwait(elem.click)
        except TimeoutException as e:
            # this is a fix for landing on the "view image" page
            # that browsers now all include. these cause a timeout
            # error w/ selenium. override the exception here, which
            # would tell the scraper we didn't change pages, and the
            # rest should work
            IMAGE_TYPES = ".*\.(jpg|jpeg|png|gif|bmp)"
            if re.match(IMAGE_TYPES, self.page_url):
                logger.debug("[*] We're on a image viewer page!")
            # some other problem. for now lets assume we didn't change
            # pages until we find otherwise.
            else:
                logger.error("[!] Scraper operation timed out!!")
                logger.error("[!] Current URL: %s" % (self.page_url))
                return False
        except Exception as e:
            logger.debug("[!] Error clicking: %s" % (e))
            logger.debug("[!] Current URL: %s" % (self.page_url))
            return False

        # apply form submit waits to 'next' button clicks
        if iterating_form and self.form_submit_wait:
            logger.debug(
                " - Forcing post-submit wait period of %ss" %
                self.form_submit_wait
            )
            time.sleep(self.form_submit_wait)

        depth = self._get_history_depth()
        window = self._get_open_windows()[-1]

        if len(self.history_stack) > 1:
            prev_window = self.history_stack[-1][0]
            if window != prev_window:
                logger.debug(" - Focusing new window: %s" % (window))
                self._switch_to_window(window)

        self.history_stack.append([window, depth])

        self.path.append((
            "click", (tag,), {"iterating_form": iterating_form}
        ))
        node = "Click\n text: %s\n hash: %s" % (text, hash)
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
        logger.debug(" - Split replacements input string: %s" % split_replacements)
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
        logger.info(" - Injecting text \"%s\" to input" % (input))
        elem = self.element_by_tag(tag)
        self._driver_exec(self.scrolltoview, elem)
        try:
            self._driver_exec(elem.clear)
        except ElementNotInteractableException as e:
            pass
        # this handles date fields which aren't clearable
        except InvalidElementStateException as e:
            pass
        for inp in self.expand_key_substitutions(input):
            elem.send_keys(inp)
        self.path.append(("input", (tag, input,), {}))
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
        logger.info(" - Selecting option %s" % (option_str))
        elem = self.element_by_tag(tag)
        self._driver_exec(self.scrolltoview, elem)
        # TODO: wrap in _driver_exec after testing
        select = Select(elem)
        # select by visible text
        select.select_by_visible_text(option_str)
        self.path.append(("input_select_option", (tag, option_str,), {}))
        action = {
            "action": "input_select_option",
            "option": option_str or "[none]",
            "tag": tag,
        }
        self.graph.add_action_to_current(action)

    def input_checkbox(self, tag, to_check, radio=False):
        """
        Check, uncheck, or don't touch an input checkbox, based
        on its current checked value.
        """
        logger.info(" - Checking to checkbox selected=%s" % (to_check))
        elem = self.element_by_tag(tag)
        self._driver_exec(self.scrolltoview, elem)
        if elem.is_selected() != to_check:
            elem.click()
        self.path.append(("input_checkbox", (tag, to_check,), {}))
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
        logger.info(" - Performing a 'natural' click")
        from selenium.webdriver.common.action_chains import ActionChains
        ac = ActionChains(self.driver)
        x_off = 0
        y_off = 0
        ac.move_to_element(elem).move_by_offset(x_off, y_off).click().perform()

    def _text_matches_search_button(self, text):
        for test_text in ["submit", "search"]:
            if test_text == text.lower():
                return True
        return False

    def _find_submit_button(self, form):
        """
        Find a submit button by a variety of strategies:
            1. use self.form_submit_button_selector
            2. find a input with type 'submit'
            3. find a link with "search" in text
        """
        sub = None
        if self.form_submit_button_selector:
            logger.debug(" - Using submit button selector: %s" % (
                self.form_submit_button_selector
            ))
            sub = self._driver_exec(
                form.find_element_by_xpath,
                self.form_submit_button_selector
            )

        # try to find a input with type 'submit'
        if not sub:
            submit_btns = self._driver_exec(
                form.find_elements_by_xpath,
                ".//input[@type='submit']|.//button[@type='submit']"
            )
            for el in submit_btns:
                if not self.element_displayed(el):
                    continue
                txt = self.element_text(el)
                cls = el.get_attribute("class").lower()
                if self._text_matches_search_button(txt):
                    sub = el
                    logger.debug(" - Form submit input button: %s" % (txt))
                    break
                if self._text_matches_search_button(cls):
                    sub = el
                    logger.debug(" - Form submit input button (class): %s" % (cls))
                    break

        # try to find a Submit link
        # NOTE: instead of using xpath we're going to do a manual search.
        # this is due to the lack of a regex xpath matcher in some browsers
        # The below should be the functional equivaliant of something like:
        #   xpath = //a[matches(., 'submit')
        if not sub:
            try:
                possible_subs = self._driver_exec(
                    form.find_elements_by_xpath, ".//a"
                )

                for el in possible_subs:
                    if not self.element_displayed(el):
                        continue
                    el_text = self.element_text(el)
                    if not self._text_matches_search_button(el_text):
                        continue
                    sub = el
                    logger.debug(" - Form submit link: %s" % (sub))
                    break
            except NoSuchElementException as e:
                pass

        return sub

    def submit(self, tag):
        """
        Submit a form from a given tag. Assumes all inputs are filled.
        """
        logger.info("[.] Submitting form.")
        logger.debug(" - form tag: %s" % tag)
        form = self.element_by_tag(tag)
        self._driver_exec(self.scrolltoview, form)

        # try to find a Submit input button
        sub = self._find_submit_button(form)

        # attempt to click on the button, if this fails, we will
        # try to perform a form submit
        sub_failure = False
        if sub:
            try:
                if self.form_submit_natural_click:
                    self.click_at_position_over_element(sub)
                else:
                    self._loadwait(sub.click)
            except Exception as e:
                sub_failure = True
                logger.warn("Failure to click on submit button/link: %s" % e)

        # otherwise, try to submit the form itself
        if not sub or sub_failure:
            logger.debug("Using form.submit selenium shim")
            self._loadwait(form.submit, check_alerts=True)

        depth = self._get_history_depth()
        window = self._get_open_windows()[-1]
        # assuming we can't pop a new window here, for now
        self.history_stack.append([window, depth])

        self.path.append(("submit", (tag,), {}))
        node = "Submit\n tag: %s" % (tag)
        node_meta = {
            "submit": tag,
            "submit_natural_click": self.form_submit_natural_click,
        }
        self.graph.add_node(node, **node_meta)

        # TODO: better way to wait for this, post-alert clicked
        if self.form_submit_wait:
            logger.debug(
                " - Forcing post-submit wait period of %ss" %
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
        return self._driver_exec(self.driver.page_source)

    @property
    def page_url(self):
        return self._driver_exec(self.driver.current_url)

    @property
    def infinite_loop_detected(self):
        """
        Store the recent page hashes and check to see if
        the most recent pages have all been identical. This
        determines an infinite loop. Note that this is only
        intended to be used inside a results pages loop.
        """
        infinite_loop_threshold = 5

        html_b = self.page_html
        if type(html_b) != bytes:
            html_b = self.page_html.encode("utf-8")

        hash = hashlib.md5(html_b).hexdigest()
        logger.debug(" - Page hash: %s" % (hash))

        # don't even look for infinite loop until we have the
        # required number of hashes to search
        if len(self.page_hashes) < infinite_loop_threshold:
            self.page_hashes.append(hash)
            return False

        self.page_hashes = self.page_hashes[1:] + [hash]
        recent = self.page_hashes[:infinite_loop_threshold]
        identical = recent.count(hash)
        logger.debug(" - %s pages of the past %s have been identical" % (
            identical, infinite_loop_threshold
        ))
        if identical == infinite_loop_threshold:
            return True

        return False

    def get_clickable(self, type=None):
        """
        Get tags, by type (optional), for the currently loaded page.
        """
        current_url = self._driver_exec(self.page_url)
        tagger = Tagger(
            driver=self.driver, current_url=current_url,
            leave_host=self.leave_host,
        )
        return tagger.get_clickable()

    def get_forms(self):
        current_url = self._driver_exec(self.page_url)
        tagger = Tagger(
            driver=self.driver, current_url=current_url,
            leave_host=self.leave_host,
        )
        forms_dict = tagger.get_forms()
        return forms_dict

    def get_buttons(self):
        current_url = self._driver_exec(self.page_url)
        tagger = Tagger(
            driver=self.driver, current_url=current_url,
            leave_host=self.leave_host,
        )
        return tagger.get_buttons()

    def get_screenshot(self):
        """
        Return a PNG screenshot or None if failure.
        """
        try:
            return self.driver.get_screenshot_as_png()
        # handle strange exceptions thrown from inside selenium injected
        # JS which appears to be used when taking screenshots
        except WebDriverException as e:
            logger.error("[!] Error getting screenshot: %s" % (e))
            return None
