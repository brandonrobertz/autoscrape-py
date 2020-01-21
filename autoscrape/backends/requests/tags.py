import logging
from urllib.parse import urlparse

from lxml import html

from autoscrape.backends.base.tags import TaggerBase


logger = logging.getLogger('AUTOSCRAPE')


class Tagger(TaggerBase):
    def __init__(self, html=None, **kwargs):
        super().__init__(**kwargs)
        self.html = html
        self.dom = self._parse_html(self.html)

    def path_from_element(self, el):
        path = []
        while el:
            siblings = []
            nth = 1
            parent = el.getparent()
            for child in parent.getchildren():
                if child == el:
                    break
                if child.tag == el.tag:
                    nth += 1
            selector = "%s:nth-of-type(%s)" % (
                el.tag, nth
            )
            path.insert(0, selector)
            el = parent
        return " > ".join(path)

    def elements_by_path(self, xpath):
        return self.dom.xpath(xpath)

    def element_attr(self, element, name):
        if not element.attrib:
            return None
        return element.attrib.get("href")

    def get_inputs(self, form=None, itype=None):
        return []

    def get_forms(self):
        return []

    def get_buttons(self, in_form=False):
        return []

    def _parse_html(self, html):
        # # html5lib version of the parser ... maybe easier to install?
        # import html5lib
        # parser = html5lib.HTMLParser(tree=html5lib.getTreeBuilder("dom"))
        # return html5lib.parse(html)
        return html.fromstring(html)
