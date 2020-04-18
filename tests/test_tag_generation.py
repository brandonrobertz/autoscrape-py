import unittest
import urllib

import autoscrape


class TestTagGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.filename = "test_page_large.cleaned.html"
        self.url = "http://localhost:8000/%s" % (self.filename)

    def test_test_server_running(self):
        """
        Make sure our test HTML server is online. We need this to be
        loaded to continue the remaining tests.
        """
        html = None
        try:
            html = urllib.request.urlopen(self.url).read()
        except urllib.error.URLError:
            pass
        msg = "Test server not running! HINT: python -m http.server --directory ./tests/data/"
        self.assertIsNotNone(
            html, msg=msg
        )

    def _get_page_source(self):
        with open("tests/data/%s" % (self.filename), "r") as f:
            return f.read()

    def test_requests_backend_can_load_page(self):
        """
        Load the test page and make sure it matches our test page.
        """
        self.requests_browser = autoscrape.backends.requests.browser.RequestsBrowser()
        self.requests_browser.fetch(self.url)
        loaded_html = self.requests_browser.page_html
        self.assertIsNotNone(loaded_html)
        raw_html = self._get_page_source()
        self.assertEqual(raw_html, loaded_html)

    def test_selenium_backend_can_load_page(self):
        """
        Test that we can load the test page and that it doesn't get
        mutated by the browser (it's clean so this shouldn't happen).
        We do this so that later we can measure differences in the CSS
        path algorithms, not differences between represented pages.
        """
        self.selenium_browser = autoscrape.backends.selenium.browser.SeleniumBrowser()
        self.selenium_browser.fetch(self.url)
        loaded_html = self.selenium_browser.page_html
        self.assertIsNotNone(loaded_html)
        raw_html = self._get_page_source()
        self.assertEqual(raw_html, loaded_html)

    def test_backend_tags_match(self):
        self.requests_browser = autoscrape.backends.requests.browser.RequestsBrowser()
        self.requests_browser.fetch(self.url)
        self.selenium_browser = autoscrape.backends.selenium.browser.SeleniumBrowser()
        self.selenium_browser.fetch(self.url)
        sel_clickable = self.selenium_browser.get_clickable()
        req_clickable = self.requests_browser.get_clickable()
        self.assertTrue(len(sel_clickable) > 0)
        self.assertTrue(len(req_clickable) > 0)
        # self.assertEqual(len(sel_clickable), len(req_clickable))
        # self.assertEqual(sel_clickable, req_clickable)


if __name__ == "__main__":
    unittest.main()
