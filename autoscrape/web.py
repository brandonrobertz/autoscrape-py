from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Scraper(object):

    def __init__(self):
        # this requires chromedriver to be on the PATH
        # if using chromium and ubuntu, apt install chromium-chromedriver
        self.driver = webdriver.Chrome()

    def fetch(self, url):
        """
        Fetch a page from a given URL (entry point, typically). Most of the time
        we just want to click a link or submit a form using webdriver.
        """
        self.driver.get(url)

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
        Click an element by a given tag.
        """
        elem = self.driver.find_element_by_xpath(tag)
        self.disable_target(elem)
        elem.click()

    def index(self, tag, input):
        """
        Enter some input into an element by a given tag.
        """
        pass

    def submit(self, tag):
        """
        Submit a form from a given tag. Assumes all inputs are filled.
        """
        pass

    def page_html(self):
        """
        Get raw page HTML from the currently loaded page.
        """
        return self.driver.page_source

    def tags(self, type):
        """
        Get tags, by type (optional), for the currently loaded page.
        """
        pass

