# -*- coding: UTF-8 -*-
import logging
from urllib.parse import urlparse


logger = logging.getLogger('AUTOSCRAPE')


class Tagger(object):
    """
    Generates tags from a given page that can be used, in a stateless manner,
    to refer to unique elements on a web page.
    """

    def __init__(self, driver=None, current_url=None, leave_host=False):
        self.driver = driver
        self.current_url = current_url
        # controls whether or not to include non-base host urls
        self.leave_host = leave_host

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
                        /*if (nth != 1)*/
                        selector += ":nth-of-type("+nth+")";
                    }
                    path.unshift(selector);
                    el = el.parentNode;
                }
                return path.join(" > ");
            }
            return getPathTo(arguments[0]); /*.toLowerCase();*/
        """
        return self.driver.execute_script(script, element)

    def get_clickable(self):
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
            href = elem.get_attribute("href")
            # logger.debug("Elem text=%s, href=%s" % (elem.text, href))

            # avoid hidden or disabled links, these can be traps or lead
            # to strange errors
            # vis = elem.get_attribute("visibility")
            # or vis == "None":
            if not elem.is_displayed() and not elem.is_enabled():
                logger.debug("Skipping non-displayed: %s" % href)
                continue

            href = elem.get_attribute("href")
            if not href:
                continue

            if href.split("#")[0] == self.current_url:
                print("Skipping current url (%s) href %s" % (
                    self.current_url, href
                ))
                continue

            # skip any weird protos ... we whitelist notrmal HTTP,
            # anchor tags and blank tags (to support JavaScript & btns)
            if href and \
               not href.startswith("https:") and \
               not href.startswith("http:") and \
               not href.startswith("javascript"):
                logger.debug("Skipping element w/ href %s" % href)
                continue

            tag = self.csspath_from_element(elem)
            # No way to get back to here, so we can't use it
            if not tag:
                logger.warn("No tag for element %s" % elem)
                continue

            # Don't leave base host ... configurable?
            elem_host = urlparse(href).netloc
            if not self.leave_host and elem_host != base_host:
                logger.debug("Skipping external host link %s" % href)
                continue

            # logger.debug("Adding href=%s as tag=%s" % (href, tag))
            tags.append(tag)

        return tags

    def get_inputs(self, form=None):
        """
        Get inputs, either for full page or by a form WebElement.
        Returns a list of tags.
        """
        x_path = "//input[@type='text']|input[@type='text']"
        elem = self.driver
        tags = []
        if form:
            elem = form
            x_path = ".%s" % x_path

        elems = elem.find_elements_by_xpath(x_path)
        for input in elems:
            input_tag = self.csspath_from_element(input)
            if not input_tag:
                logger.warn("No tag for input %s" % input)
                continue

            tags.append(input_tag)

        return tags

    def get_forms(self):
        """
        Get all tags to forms on a page and their respective
        text inputs. Tags are returned in a dict, with the
        form CSSPath as the key and a list of input CSSPaths
        under the form.
        """
        x_path = "//form"
        forms = self.driver.find_elements_by_xpath(x_path)

        tags = {}
        for elem in forms:
            if not elem.is_displayed() or not elem.is_enabled():
                continue

            tag = self.csspath_from_element(elem)
            if not tag:
                logger.warn("No tag for element %s" % elem)
                continue

            tags[tag] = self.get_inputs(form=elem)

        return tags

    def get_buttons(self, in_form=False):
        x_path = "//form//a|//button|//input[@type='button']"
        btns = self.driver.find_elements_by_xpath(x_path)
        print("*** btns", btns)

        tags = []
        for elem in btns:
            if not elem.is_displayed() or not elem.is_enabled():
                continue

            tag = self.csspath_from_element(elem)
            if not tag:
                logger.warn("No tag for element %s" % elem)
                continue

            tags.append(tag)

        return tags

