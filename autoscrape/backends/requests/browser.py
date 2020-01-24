import logging

import requests
from autoscrape.backends.requests.tags import Tagger
from autoscrape.search.graph import Graph


logger = logging.getLogger('AUTOSCRAPE')


class Browser(Tagger):
    def __init__(self, leave_host=False, **kwargs):
        # requests Session
        self.s = requests.Session()

        # set of clicked elements
        self.visited = set()

        # queue of the path that led us to the current page
        # this is in the form of (command, *args, **kwargs)
        self.path = []

        # tree building
        self.graph = Graph()

        # setting to False, ensures crawl will stay on same host
        self.leave_host = leave_host

        self.current_url = None
        self.current_html = None

    def click(self, tag, **kwargs):
        element = self.element_by_tag(tag)
        text = element.text
        url = None
        if element.tag == "a":
            raw_href = self.element_attr(element, "href")
            if not raw_href:
                return False

            url = self.normalize(raw_href)
            hash = "%s|%s" % (url, element.tag)
            if hash in self.visited:
                logger.debug("Hash already visited: %s" % hash)
                return False
            self.visited.add(hash)

            print("!! Clicking link", url)
            self.fetch(url)
        else:
            raise NotImplementedError(
                "click not supported for tag: %s" % (element.tag)
            )

        self.path.append((
            "click", [tag], {"url": url}
        ))
        node = "Click, text: %s, url: %s, tag: %s" % (text, url, tag)
        node_meta = {
            "click": tag,
            "click_text": text,
            "click_iterating_form": None,
        }
        self.graph.add_node(
            node,
            **node_meta
        )
        self.graph.move_to_node(node)
        return True

    def fetch(self, url, initial=False):
        """
        Fetch a page from a given URL (entry point, typically). Most of
        the time we just want to click a link or submit a form using
        webdriver.
        """
        print("%s! Fetching url=%s initial=%s" % (
            ("!" if initial else " "), url, initial,
        ))
        response = self.s.get(url)
        self.current_url = response.url
        self.current_html = response.text
        self.dom = self._get_dom()

        if initial:
            self.path.append(("fetch", [url], {"initial": initial}))
            node = "Fetch, url: %s" % url
            self.graph.add_root_node(node, url=url, action="fetch")

    def _no_tags(self, list, l_type="path"):
     clean = []
     for p in list:
         name, args, kwargs = p
         if name == "click":
             args[0] = "tag"
         clean.append((name, args, kwargs))
     return clean

    def back(self):
        print("!! Going back... current n=%s path=%s" % (
            len(self.path),
            self._no_tags(self.path),
        ))

        # We're now where we started from
        curr = self.path.pop()
        if not self.path:
            self.path = []
            return

        prev = self.path[-1]
        if prev[0] == "fetch":
            self.graph.move_to_parent()
            self.fetch(prev[1][0])

        elif prev[0] == "click":
            self.graph.move_to_parent()
            self.fetch(prev[2]["url"])

    @property
    def page_html(self):
        return self.current_html

    @property
    def page_url(self):
        return self.current_url

    def get_clickable(self, **kwargs):
        print(" ! Getting clickable...")
        self.dom = self._get_dom()
        tagger = Tagger(
            current_html=self.current_html,
            current_url=self.current_url,
            leave_host=self.leave_host,
        )
        clickable = tagger.get_clickable()
        print("clickable n=%s" % (len(clickable)))
        print(" n=%s, path=%s" % (len(self.path), self._no_tags(self.path)))
        print(" --")
        return clickable

    # def download_file(self, url):
    #     response = self.s.get(url)
    #     action = {
    #         "action": "download_page",
    #         "url": url,
    #     }
    #     self.graph.add_action_to_current(action)
    #     return response.text

