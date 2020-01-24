# -*- coding: UTF-8 -*-
import lxml.html

from urllib.parse import urlparse, ParseResult

from autoscrape.backends.base.dom import DomBase


class Dom(DomBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dom = self._get_dom()

    def _get_dom(self):
        return lxml.html.fromstring(self.current_html)

    def element_attr(self, element, name):
        if not element.attrib:
            return None
        return element.attrib.get("href")

    def element_by_tag(self, tag):
        return self.dom.cssselect(tag)[0]

    def elements_by_path(self, path):
        return self.dom.xpath(path)

    def get_stylesheet(self):
        css = ""
        for link in self.dom.xpath("//link"):
            if not link.attrib:
                continue
            l_type = link.attrib.get("type")
            l_rel = link.attrib.get("rel")
            l_href = link.attrib.get("href")
            if l_type != "text/css" and l_rel != "stylesheet":
                continue
            css += '@import url("%s");' % (l_href)
        for style in self.dom.xpath("style"):
            css += style.text_content()
        return css

    def normalize(self, url):
        parsed_current_url = urlparse(self.current_url)
        parsed_url = urlparse(url)

        args = []
        for argname in ['scheme', 'netloc', 'path', 'params', 'query', 'fragment']:
            value = getattr(parsed_url, argname, None)
            if not value:
                value = getattr(parsed_current_url, argname, '')
            args.append(value)

        pr = ParseResult(*args)
        normalized = pr.geturl()
        return normalized

    def element_text(self, element, block=False):
        if block and element is not None:
            # TODO: do recursive text getting
            return element.text_content()
        text = element.text
        if not text:
            return ''
        return text

    def element_tag_name(self, element):
        if element is None:
            return ""
        return element.tag

