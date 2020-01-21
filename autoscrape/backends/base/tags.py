# -*- coding: UTF-8 -*-
import logging

from urllib.parse import urlparse


logger = logging.getLogger('AUTOSCRAPE')


class TaggerBase:
    """
    Generates tags from a given page that can be used, in a stateless manner,
    to refer to unique elements on a web page.
    """

    def __init__(self, current_url=None, leave_host=False, **kwargs):
        self.current_url = current_url
        self.base_host = urlparse(current_url).netloc
        # controls whether or not to include non-base host urls
        self.leave_host = leave_host

    def path_from_element(self, element):
        """
        For a given element, return a path (a.k.a. a "tag") leading
        to it. Path can be CSS, XPath, or whatever the backend supports.
        """
        raise NotImplementedError("Tagger.path_from_element not implemented")

    def clickable_sanity_check(self, element):
        """
        Check a series of element nodes, checking their attributes and other
        attributes, determining if a element is actually 'clickable'. This
        check determines which nodes will end up as clickable options for
        the scraper on this page.
        """
        href = self.element_attr(element, "href")
        if not href:
            return False

        if href.split("#")[0] == self.current_url:
            logger.debug("Skipping current url (%s) href %s" % (
                self.current_url, href
            ))
            return False

        # skip any weird protos ... we whitelist notrmal HTTP,
        # anchor tags and blank tags (to support JavaScript & btns)
        if href and \
           not href.startswith("https:") and \
           not href.startswith("http:") and \
           not href.startswith("javascript"):
            logger.debug("Skipping element w/ href %s" % href)
            return False

        # Don't leave base host ... configurable?
        elem_host = urlparse(href).netloc
        if not self.leave_host and elem_host != self.base_host:
            logger.debug("Skipping external host link %s" % href)
            return False

        return True

    def get_clickable(self, path="//a"):
        """
        Get all clickable element tags on the current page.
        """
        tags = []
        a_elems = self.elements_by_path(path)
        for element in a_elems:
            href = self.element_attr(element, "href")

            if not self.clickable_sanity_check(element):
                continue

            tag = self.path_from_element(element)
            # No way to get back to here, so we can't use it
            if not tag:
                logger.warn("No tag for element %s" % element)
                return False

            if not element.is_displayed() and not element.is_enabled():
                logger.debug("Skipping non-displayed: %s" % href)
                return False

            tags.append(tag)
        return tags

    def get_inputs(self, form=None, itype=None):
        """
        Get inputs, either for full page or by a form.  Returns a list
        of tags. itype can be one of "text", "select", "checkbox", or
        None (all types), indicating the type of input.
        """
        raise NotImplementedError("Tagger.get_inputs not implemented")

    def get_forms(self):
        """
        Get all tags to forms on a page and their respective text
        inputs. Tags are returned in a dict, with the form CSSPath as
        the key and a list of input CSSPaths under the form.
        """
        raise NotImplementedError("Tagger.get_forms not implemented")

    def get_buttons(self, in_form=False):
        """
        Return all tags leading to a form link, button, or submit input button,
        optionally given a base form to look from. This is used to identify
        clickable things related to forms.
        """
        raise NotImplementedError("Tagger.get_buttons not implemented")

    def elements_by_path(self, path):
        """
        Return element nodes matching a path where path could be xpath,
        css, etc, depending on the backend)
        """
        raise NotImplementedError("Tagger.elements_by_path not implemented")

    def element_attr(self, element, name):
        """
        For a given element and attribute name, return the value if it
        exists.
        """
        raise NotImplementedError("Tagger.element_attr not implemented")

