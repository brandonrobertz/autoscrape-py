# -*- coding: UTF-8 -*-
import lxml.html
from multiprocessing import Pool

import requests
from urllib.parse import urlparse, ParseResult

from autoscrape.backends.base.dom import DomBase


def download_stylesheet(css_url):
    response = requests.get(css_url)
    data = response.text
    if type(data) == bytes:
        return text.decode("utf-8")
    return data


class Dom(DomBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dom = self._get_dom()

    def _get_dom(self):
        return lxml.html.fromstring(self.current_html)

    def element_attr(self, element, name, default=None):
        if element.attrib and "href" in element.attrib:
            return element.attrib["href"]
        return default

    def element_by_tag(self, tag):
        return self.dom.cssselect(tag)[0]

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

        pool = Pool(8)
        results = pool.map(download_stylesheet, stylesheet_urls)
        pool.close()

        css = "\n".join(results)
        for style in self.dom.xpath("style"):
            css += style.text_content()
        return css

    def _normalize_url(self, url):
        argnames = ['scheme', 'netloc', 'path', 'params', 'query', 'fragment']
        parsed_current_url = urlparse(self.current_url)
        parsed_url = urlparse(url)

        args = []
        for argname in argnames:
            value = getattr(parsed_url, argname, None)
            if not value:
                value = getattr(parsed_current_url, argname, '')
            args.append(value)

        pr = ParseResult(*args)
        normalized = pr.geturl()
        return normalized

    def element_text(self, element, block=False):
        if block and element is not None:
            return element.text_content()
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

