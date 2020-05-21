# -*- coding: UTF-8 -*-
import logging
import re

from autoscrape.scrapers import BaseScraper
from autoscrape.control import Controller
from autoscrape.input_parser import InputParser


logger = logging.getLogger('AUTOSCRAPE')


class ManualControlScraper(BaseScraper):
    """
    A Depth-First Search scraper that looks for forms, inputs, and next
    buttons by some manual criteria and iterates accordingly.
    """
    training_classes = [
        "data_pages", "error_pages", "links_to_documents",
        "links_to_search", "search_pages", "crawl_pages",
        "interaction_pages",
    ]

    # TODO: save the path to the matched search form to a file. then
    # upon subsequent loads, we can try that path first and then go
    # from there. this way the manual control scraper can learn from
    # self-exploration based on manual params
    #
    # Another related idea: it would be nice if we had an API that
    # saved data about successful runs and loading/replaying them
    # so users can get familiar with the concepts of self-exploration
    # and self-learning but without having to get the ML concepts.

    def __init__(self, baseurl, loglevel=None, stdout=None, maxdepth=10,
                 max_pages=None,
                 formdepth=0, next_match=None, form_match=None,
                 output=None, keep_filename=False, disable_style_saving=False,
                 save_screenshots=False, save_graph=False,
                 full_page_screenshots=False, input=None, leave_host=False,
                 driver="Firefox", browser_binary=None,
                 remote_hub="http://localhost:4444/wd/hub",
                 link_priority=None, ignore_links=None, only_links=None,
                 ignore_extensions=None, result_page_links=None,
                 form_submit_natural_click=False, form_submit_wait=5,
                 force_page_wait=None, form_submit_button_selector=None,
                 load_images=False, show_browser=False, warc_index_file=None,
                 warc_directory=None, return_data=False, page_timeout=None,
                 backend="selenium"):
        # setup logging, etc
        super().setup_logging(
            loglevel=loglevel, stdout=stdout
        )
        if page_timeout is not None:
            page_timeout = int(page_timeout or 0)
        # set up web scraper controller
        self.control = Controller(
            leave_host=leave_host, driver=driver, remote_hub=remote_hub,
            form_submit_natural_click=form_submit_natural_click,
            form_submit_wait=int(form_submit_wait or 0),
            form_submit_button_selector=form_submit_button_selector,
            force_page_wait=int(force_page_wait or 0),
            load_images=load_images, show_browser=show_browser,
            warc_index_file=warc_index_file, warc_directory=warc_directory,
            output=output, backend=backend, browser_binary=browser_binary,
            page_timeout=page_timeout,
        )
        self.control.initialize(baseurl)
        # depth of DFS in search of form
        self.maxdepth = int(maxdepth or 0)
        # current depth of iterating through 'next' form buttons
        self.formdepth = int(formdepth or 0)
        # max total pages to fetch
        self.max_pages = int(max_pages) if max_pages else None
        # keep number of fetched pages here.
        self.total_pages = 0
        # match for link to identify a "next" button
        self.next_match = next_match
        # string to match a form (by element text) we want to scrape
        self.form_match = form_match
        # Where to write training data from crawl
        self.output = output
        # Whether or not to return crawled data upon completion. This can be
        # used along with output, or on its own. This will store all
        # data in memory (in self.crawl_data) during the crawl, so beware!
        self.return_data = return_data
        self.crawl_data = []
        # If this is true, do not use a file hash for the filename
        self.keep_filename = keep_filename
        # Disable saving of stylesheets for web content types
        self.disable_style_saving = disable_style_saving
        # To save screenshots or not (they're large and expensive)
        self.save_screenshots = save_screenshots
        # To save the whole, scrolled down page screenshot, this can
        # fail in certain circumstances
        self.full_page_screenshots = full_page_screenshots
        # Whether to save the crawl & interaction traversal graph
        self.save_graph = save_graph
        # string used to match link text in order to sort them higher
        self.link_priority = link_priority
        # string or regex to be used to omit links from clickable
        self.ignore_links = ignore_links
        # string or regex to use to not go to URLs with extensions
        self.ignore_extensions = ignore_extensions
        # Whitelisted links to click
        self.only_links = only_links
        # Apply any link clicking rules to the results pages
        self.result_page_links = result_page_links
        # attempt a position-based "natural click" over the element
        self.form_submit_natural_click = form_submit_natural_click
        # a period of seconds to force a wait after a submit
        self.form_submit_wait = int(form_submit_wait or 0)
        # a generator, outputting individual form interaction plans
        if input:
            self.input_gen = InputParser(input).generate()
        # if not specified, do nothing with forms
        else:
            self.input_gen = [[]]
        # whether or not we've successfully scraped what we want
        self.scraped = False

    def click_until_no_links(self, links):
        logger.info("[.] Clicking result page links...")
        if self.max_pages is not None and self.total_pages >= self.max_pages:
            logger.info(" - Maximum pages %s reached, returning..." % self.max_pages)
            return

        link_vectors = self.control.vectorizer.link_vectors()
        link_zip = list(zip(range(len(link_vectors)), link_vectors))
        link_zip = filter(
            lambda x: re.findall(self.result_page_links, x[1]),
            link_zip
        )
        logger.debug(" - Candidate links: %s" % (link_zip))
        # Click until we get no more matches
        for ix, text in link_zip:
            logger.info("[.] Clicking result page link: %s" % (text))
            logger.debug(" - Current URL: %s" % (self.control.scraper.page_url))
            if self.control.select_link(ix, iterating_form=True):
                self.total_pages += 1
                self.click_until_no_links(links)
                self.save_training_page(classname="data_pages")
                self.save_screenshot(classname="data_pages")
                self.control.back()

    def keep_clicking_next_btns(self):
        """
        This looks for "next" buttons, or (in the future) page number
        links, and clicks them until one is not found. This saves the
        pages as it goes.
        """
        logger.info("[*] Entering result page iteration routine")
        depth = 0
        while True:
            if self.formdepth and depth >= self.formdepth:
                logger.debug("[*] Max 'next' formdepth reached %s" % depth)
                break

            button_data = self.control.vectorizer.button_vectors()
            n_buttons = len(button_data)
            logger.info("[.] On result page %s" % (depth + 1))
            logger.debug(" - Button vectors (%s): %s" % (
                n_buttons, button_data
            ))

            if self.result_page_links:
                self.click_until_no_links(self.result_page_links)

            # element type, index, text
            next_found = None
            for ix in range(n_buttons):
                button_text = button_data[ix]
                logger.debug(" - Checking button: %s" % button_text)
                if re.findall(self.next_match.lower(), button_text.lower()):
                    next_found = ("button", ix, button_text)
                    break

            if not next_found:
                link_vectors = self.control.vectorizer.link_vectors()
                n_clickable = len(link_vectors)
                logger.debug(" - Button not found, searching %s links" % (
                    n_clickable
                ))
                for ix in range(n_clickable):
                    link_text = link_vectors[ix]
                    logger.debug(" - Checking clickable: %s" % link_text)
                    if re.findall(self.next_match.lower(), link_text.lower()):
                        next_found = ("link", ix, link_text)
                        break

            # we didn't find a next match, break loop
            if next_found is None:
                logger.debug(" - Next button not found!")
                break
            else:
                ntype, ix, text = next_found
                logger.info("[.] Next button found! Clicking: %s" % (text))
                depth += 1
                if ntype == "button":
                    self.control.select_button(ix, iterating_form=True)
                elif ntype == "link":
                    self.control.select_link(ix, iterating_form=True)

                # subsequent page loads get saved here
                self.save_training_page(classname="data_pages")
                self.save_screenshot(classname="data_pages")

            # check for infinite loop, this is based on the hash
            # of the previous few pages
            logger.debug(" - Checking for infinite loop...")
            if self.control.scraper.infinite_loop_detected:
                logger.debug(" - Infinte loop detected. Breaking.")
                break

        for _ in range(depth):
            logger.debug("[.] Going back from result page...")
            self.control.back()

    def scrape(self, depth=0):
        logger.info("[.] Crawl depth %s" % depth)
        logger.info(" - Total pages: %s of max: %s" % (
            self.total_pages, self.max_pages
        ))
        if self.maxdepth != -1 and depth > self.maxdepth:
            logger.info(" - Maximum depth %s reached, returning..." % depth)
            self.control.back()
            return
        if self.max_pages is not None and self.total_pages >= self.max_pages:
            logger.info(" - Maximum pages %s reached, returning..." % self.max_pages)
            return
        if self.scraped:
            logger.debug(" - Scrape complete, not clicking anything else.")
            return

        if self.ignore_extensions and re.findall(self.ignore_extensions,
                                                 self.control.scraper.page_url):
            logger.debug(" - Ignoring URL matching ignored extension: %s" % (
                self.control.scraper.page_url
            ))
            return

        self.save_training_page(classname="crawl_pages")
        self.save_screenshot(classname="crawl_pages")
        form_vectors = self.control.vectorizer.form_vectors()

        # NOTE: we never get into this loop if self.input_gen is empty
        # this arises when input was not handed to the initializer
        for ix in range(len(form_vectors)):
            # don't bother with looking for forms if we didn't specify
            # th form_match option
            if not self.form_match:
                continue

            form_data = form_vectors[ix]

            # inputs are keyed by form index, purely here for debug purposes
            inputs = self.control.inputs[ix]
            logger.debug(" - Form: %s Text: %s" % (ix, form_data))
            logger.debug(" - Inputs: %s" % inputs)

            if self.form_match.lower() not in form_data.lower():
                continue

            logger.info("[*] Found an input form (No. %s on page)" % (ix))
            self.save_training_page(classname="search_pages")
            self.save_screenshot(classname="search_pages")

            for input_phase in self.input_gen:
                logger.debug(" - Input plan: %s" % input_phase)
                for single_input in input_phase:
                    input_index = single_input["index"]
                    if single_input["type"] == "input":
                        input_string = single_input["string"]
                        logger.info("[.] Inputting %s to input %s" % (
                            input_string, ix
                        ))
                        self.control.input(ix, input_index, input_string)
                    elif single_input["type"] == "select":
                        input_string = single_input["string"]
                        logger.info("[.] Selecting option %s in input %s" % (
                            input_string, input_index
                        ))
                        self.control.input_select_option(
                            ix, input_index, input_string
                        )
                    elif single_input["type"] == "checkbox":
                        to_check = single_input["action"]
                        logger.info("[.] %s checkbox input %s" % (
                            "Checking" if to_check else "Unchecking",
                            input_index
                        ))
                        self.control.input_checkbox(
                            ix, input_index, to_check
                        )
                    elif single_input["type"] == "date":
                        input_string = single_input["string"]
                        logger.info("[.] Setting date to %s in date input %s" % (
                            input_string, ix))
                        self.control.input_date(ix, input_index, input_string)
                    elif single_input["type"] == "radio":
                        radio_index = single_input["string"]
                        logger.info("[.] Selecting radio checkbox %s in group %s" % (
                            radio_index, input_index
                        ))
                        self.control.input_radio_option(
                            ix, input_index, radio_index
                        )

                # capture post-input screenshot
                self.save_screenshot(classname="interaction_pages")

                # actually submit the page
                self.control.submit(ix)
                self.total_pages += 1

                # save the initial landing result page
                self.save_screenshot(classname="data_pages")
                self.save_training_page(classname="data_pages")

                # if we're looking for next buttons, click them
                if self.next_match:
                    self.keep_clicking_next_btns()

                self.scraped = True
                self.control.back()

            logger.debug("[*] Completed iteration!")
            # Only scrape a single form, due to explicit, single
            # match configuration option
            if self.scraped:
                logger.info("[*] Scrape complete! Exiting.")
                return

        link_vectors = self.control.vectorizer.link_vectors()
        logger.debug("[.] Links on page: %s" % (link_vectors))
        link_zip = list(zip(range(len(link_vectors)), link_vectors))
        if self.ignore_links:
            logger.debug(" - Ignoring links matching: %s" % self.ignore_links)
            link_zip = filter(
                lambda x: not re.findall(self.ignore_links, x[1]),
                link_zip
            )
        if self.only_links:
            logger.debug(" - Keeping only links matching: %s" % self.ignore_links)
            link_zip = filter(
                lambda x: re.findall(self.only_links, x[1]),
                link_zip
            )
        if self.link_priority:
            logger.debug(" - Sorting by link priority: %s" % self.link_priority)
            link_zip.sort(
                key=lambda x: not re.findall(self.link_priority, x[1])
            )

        for ix, text in link_zip:
            logger.debug(" - Link index: %s text: %s" % (ix, text))
            if self.maxdepth != -1 and depth == self.maxdepth:
                logger.debug(" - At maximum depth: %s, skipping links." % depth)
                break
            if self.max_pages is not None and self.total_pages >= self.max_pages:
                logger.info(" - Maximum pages reached, skipping links.")
                break
            if self.scraped:
                logger.debug(" - Scrape complete, not clicking anything else.")
                return

            logger.debug(" - Current URL: %s" % (self.control.scraper.page_url))
            logger.debug(" - Attempting to click link text: %s" % text)
            if self.control.select_link(ix):
                logger.info("[.] Link clicked: %s" % (text))
                logger.debug(" - Current URL: %s" % (self.control.scraper.page_url))
                self.total_pages += 1
                self.scrape(depth=depth + 1)
            else:
                logger.debug(" - Click failed, skipping: %s" % text)

        logger.debug("[*] Searching forms and links on page complete")
        self.control.back()

    def run(self, *args, **kwargs):
        # we have to catch this so, in the case of failure, we
        # don't have random browser windows hanging around
        try:
            self.scrape(*args, **kwargs)
        except Exception as e:
            msg = "[!] Fatal error scraping: %s. Cleaning up, quitting."
            logger.error(msg % (e))
            if hasattr(self.control.scraper, "driver"):
                self.control.scraper.driver.quit()
            if self.output and self.save_graph:
                self.save_scraper_graph()
            raise e
        # else:
        #     logger.info("[+] AutoScrape run complete.")
        #     if self.output and self.save_graph:
        #         self.save_scraper_graph()
        try:
            self.control.scraper.driver.quit()
        except Exception:
            pass

        if self.return_data:
            return self.crawl_data
