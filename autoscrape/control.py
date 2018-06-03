
class Controller(object):
    """
    High-level control for scraping a web page. This allows us to control
    all of the possible scraper commands in an automated way.
    """
    def __init__(self, url):
        pass

    def initialize(self, url):
        """
        Instantiate a web scraper, given a starting point URL.
        """
        pass

    def select_link(self, index):
        pass

    def input(self, index, chars):
        pass

    def submit(self, index):
        pass

