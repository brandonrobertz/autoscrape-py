from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Scraper(object):

    def __init__(self):
        self.driver = webdriver.Chrome()

    def fetch(url):
        """
        Fetch a page from a given URL (entry point, typically). Most of the time
        we just want to click a link or submit a form using webdriver.
        """
        self.driver.get(url)

    def click(tag):
        """
        Click an element by a given tag.
        """
        pass

    def enter(tag, input):
        """
        Enter some input into an element by a given tag.
        """
        pass

    def submit(tag):
        """
        Submit a form from a given tag. Assumes all inputs are filled.
        """
        pass

    def page_data():
        """
        Get raw page data from the currently loaded page.
        """
        pass

    def tags(type):
        """
        Get tags, by type (optional), for the currently loaded page.
        """
        pass

