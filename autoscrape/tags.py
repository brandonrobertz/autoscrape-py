# -*- coding: UTF-8 -*-
import logging
from urllib.parse import urlparse


logger = logging.getLogger('AUTOSCRAPE')


class Tagger(object):
    """
    Generates tags from a given page that can be used, in a stateless manner,
    to refer to unique elements on a web page.
    """

    def __init__(self, driver=None, current_url=None):
        self.driver = driver
        self.current_url = current_url

    def csspath_from_element(self, element):
        """
        Takes a WebDriver element and returns an CSSPath for finding it
        in the future. As far as I know, this is only really feasible
        using JavaScript (without resorting to a complicated tree walking
        algorithm ... which we may need to do if this ends up failing).

        Taken from: https://stackoverflow.com/a/12222317
        """
        script = """
            var getPathTo = function(el) {
                if (!(el instanceof Element))
                    return;
                var path = [];
                while (el.nodeType === Node.ELEMENT_NODE) {
                    var selector = el.nodeName.toLowerCase();
                    if (el.id) {
                        selector += '#' + el.id;
                        path.unshift(selector);
                        break;
                    } else {
                        var sib = el, nth = 1;
                        while (sib = sib.previousElementSibling) {
                            if (sib.nodeName.toLowerCase() == selector)
                               nth++;
                        }
                        //if (nth != 1)
                            selector += ":nth-of-type("+nth+")";
                    }
                    path.unshift(selector);
                    el = el.parentNode;
                }
                return path.join(" > ");
            }
            return getPathTo(arguments[0]).toLowerCase();
        """
        return self.driver.execute_script(script, element)

    def clickable_tags(self):
        """
        Get all clickable element tags on the current page.

        TODO: In the future we may need to recurse the page to find
        other clickable types like JS-enabled divs, etc.
        """
        tags = []

        x_path_types = "//a|//button"
        a_elems = self.driver.find_elements_by_xpath(x_path_types)
        base_host = urlparse(self.driver.current_url).netloc

        for elem in a_elems:
            # avoid hidden or disabled links, these can be traps or lead
            # to strange errors
            if not elem.is_displayed() or not elem.is_enabled():
                continue

            href = elem.get_attribute("href")
            if href == self.current_url:
                # ("Skipping current url  href %s" % href)
                continue

            # skip any weird protos ... we whitelist notrmal HTTP,
            # anchor tags and blank tags (to support JavaScript & btns)
            if not href.startswith("https:") and \
               not href.startswith("http:") and \
               not href.startswith("#") and \
               not href:
                # print("Skipping element w/ href %s" % href)
                continue

            tag = self.csspath_from_element(elem)
            # No way to get back to here, so we can't use it
            if not tag:
                logger.warn("No tag for element %s" % elem)
                continue

            # Don't leave base host ... configurable?
            elem_host = urlparse(href).netloc
            if elem_host != base_host:
                # print("Skipping external host link %s" % href)
                continue

            tags.append(tag)

        return tags

    def get_tags(self, type=None):
        elem_tags = []
        clickable_tags = self.clickable_tags()
        elem_tags.extend(clickable_tags)
        return elem_tags

