# -*- coding: UTF-8 -*-
import logging

from urllib.parse import urlparse

from autoscrape.backends.base.dom import DomBase


logger = logging.getLogger('AUTOSCRAPE')


class TaggerBase(DomBase):
    """
    Generates tags from a given page that can be used, in a stateless manner,
    to refer to unique elements on a web page.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_host = urlparse(self.current_url).netloc

    def tag_from_element(self, element):
        """
        For a given element, return a path (a.k.a. a "tag") leading
        to it. Path can be CSS, XPath, or whatever the backend supports.
        """
        raise NotImplementedError("Tagger.tag_from_element not implemented")

    def clickable_sanity_check(self, element, href=None):
        """
        Check a series of element nodes, checking their attributes and other
        attributes, determining if a element is actually 'clickable'. This
        check determines which nodes will end up as clickable options for
        the scraper on this page.
        """
        if not href:
            raw_href = self.element_attr(element, "href")
            if not raw_href:
                return False

            if hasattr(self, "_normalize_url"):
                href = self._normalize_url(raw_href).split("#")[0]
            else:
                href = raw_href

        if href.split("#")[0] == self.current_url:
            return False

        # skip any weird protos ... we whitelist notrmal HTTP,
        # anchor tags and blank tags (to support JavaScript & btns)
        if href and \
           not href.startswith("//") and \
           not href.startswith("https:") and \
           not href.startswith("http:") and \
           not href.startswith("javascript"):
            return False

        # Don't leave base host ... configurable?
        elem_host = urlparse(href).netloc
        if elem_host and not self.leave_host and elem_host != self.base_host:
            return False

        return True

    def get_clickable(self, path="//a"):
        """
        Get all clickable element tags on the current page.
        """
        tags = []
        a_elems = self.elements_by_path(path)
        for element in a_elems:
            if not self.clickable_sanity_check(element):
                continue

            tag = self.tag_from_element(element)
            # No way to get back to here, so we can't use it
            if not tag:
                logger.warn("No tag for element %s" % (element))
                return False

            tags.append(tag)
        return tags

    def get_inputs(self, form=None, itype=None, root_node=None):
        """
        Get inputs, either for full page or by a form WebElement.
        Returns a list of tags. itype can be one of "text", "select",
        "checkbox", or None (all types), indicating the type of input.
        """
        x_path = "//input"
        if itype == "select":
            x_path = "//select"
        elif itype:
            x_path = "//input[@type='%s']" % (itype)

        elem = root_node
        tags = []
        if form is not None:
            elem = form
            x_path = ".%s" % x_path

        elems = self.elements_by_path(x_path, from_element=elem)
        for input in elems:
            input_tag = self.tag_from_element(input)
            if not input_tag:
                logger.warn("No tag for input %s" % input)
                continue

            tags.append(input_tag)

        return tags

    def get_forms(self):
        """
        Get all tags to forms on a page and their respective text
        inputs. Tags are returned in a dict, with the form tag as
        the key and a list of input CSSPaths under the form.
        """
        x_path = "//form"
        forms = self.elements_by_path(x_path)

        tags = {}
        for elem in forms:
            # TODO: migrate these to DOM? requests can't really do this...
            if hasattr(elem, "is_displayed") and not elem.is_displayed():
                continue
            if hasattr(elem, "is_enabled") and not elem.is_enabled():
                continue

            tag = self.tag_from_element(elem)
            if not tag:
                logger.warn("No tag for element %s" % elem)
                continue

            tags[tag] = [
                self.get_inputs(form=elem, itype="text"),
                self.get_inputs(form=elem, itype="select"),
                self.get_inputs(form=elem, itype="checkbox"),
                self.get_inputs(form=elem, itype="date"),
            ]

        return tags

    def get_buttons(self, in_form=False, path=None):
        """
        Return all tags leading to a form link, button, or submit input button,
        optionally given a base form to look from. This is used to identify
        clickable things related to forms.
        """
        x_path = path or "|".join([
            "//form//a", "//button", "//input[@type='button']",
            "//input[@type='submit']", "//table//a",
        ])
        btns = self.elements_by_path(x_path)

        tags = []
        for elem in btns:
            if hasattr(elem, "is_displayed") and not elem.is_displayed():
                continue
            if hasattr(elem, "is_enabled") and not elem.is_enabled():
                continue
            tag = self.tag_from_element(elem)
            if not tag:
                logger.warn("No tag for element %s" % elem)
                continue
            tags.append(tag)
        return tags
