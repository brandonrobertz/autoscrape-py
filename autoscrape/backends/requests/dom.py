# -*- coding: UTF-8 -*-
import lxml.html
# use threads so we can run autoscrape inside celery
from multiprocessing.pool import ThreadPool

import requests
from urllib.parse import urlparse, ParseResult

from autoscrape.backends.base.dom import DomBase


def download_stylesheet(css_url):
    response = requests.get(css_url)
    data = response.text
    if type(data) == bytes:
        return data.decode("utf-8")
    return data


class Dom(DomBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dom = self._get_dom()

    def _get_dom(self):
        try:
            dom = lxml.html.fromstring(self.current_html)
        # this handles trying to load XML, RSS feed, etc
        except ValueError as e:
            if "Please use bytes input" in str(e):
                html_b = bytes(self.current_html, encoding="utf-8")
                dom = lxml.html.fromstring(html_b)
            else:
                raise e
        # if our page's HTML is just an element, like an
        # iframe, without a body or html then lxml will
        # return an element surrounded by a body and html.
        # so here we make element the root and use that as
        # our base DOM.
        while True:
            parent = dom.getparent()
            if parent is None:
                break
            dom = parent
        return dom

    def element_attr(self, element, name, default=None):
        if not element.attrib:
            return default
        return element.attrib.get(name, default)

    def element_by_tag(self, tag):
        elements = self.dom.cssselect(tag)
        if not elements:
            return None
        return elements[0]

    def elements_by_path(self, xpath, from_element=None):
        if from_element is None:
            return self.dom.xpath(xpath)
        return from_element.xpath(xpath)

    def get_stylesheet(self, fetch_css=False):
        stylesheet_urls = []
        for link in self.dom.xpath("//link"):
            if not link.attrib:
                continue
            l_type = link.attrib.get("type")
            l_rel = link.attrib.get("rel")
            l_href = link.attrib.get("href")
            if l_type != "text/css" and l_rel != "stylesheet":
                continue
            css_url = self._normalize_url(l_href)
            stylesheet_urls.append(css_url)

        pool = ThreadPool(8)
        results = pool.map(download_stylesheet, stylesheet_urls)
        pool.close()

        css = "\n".join(results)
        for style in self.dom.xpath("style"):
            css += style.text_content()
        return css

    def _normalize_url(self, url):
        argnames = ['scheme', 'netloc', 'path', 'params', 'query', 'fragment']
        inheritable = ['scheme', 'netloc', 'path']
        parsed_current_url = urlparse(self.current_url)
        parsed_url = urlparse(url)

        args = []
        for argname in argnames:
            value = getattr(parsed_url, argname, None)
            if not value and argname in inheritable:
                value = getattr(parsed_current_url, argname, '')
            args.append(value)

        pr = ParseResult(*args)
        normalized = pr.geturl()
        return normalized

    def element_text(self, element, block=False):
        if block and element is not None:
            return element.text_content()
        if element is None:
            return ''
        text = element.text
        if not text:
            return ''
        return text

    def element_name(self, element):
        return element.name

    def element_tag_name(self, element):
        if element is None:
            return ""
        return element.tag
