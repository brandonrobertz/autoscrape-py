# -*- coding: UTF-8 -*-
import logging

from autoscrape.backends.base.tags import TaggerBase
from autoscrape.backends.selenium.dom import Dom


logger = logging.getLogger('AUTOSCRAPE')


class Tagger(TaggerBase, Dom):
    """
    Generates tags from a given page that can be used, in a stateless manner,
    to refer to unique elements on a web page.
    """

    def __init__(self, driver=None, current_url=None, leave_host=False):
        super().__init__(current_url=current_url, leave_host=leave_host)
        self.driver = driver

    def tag_from_element(self, element):
        """
        Takes a WebDriver element and returns an CSSPath for finding it
        in the future. As far as I know, this is only really feasible
        using JavaScript (without resorting to a complicated tree walking
        algorithm ... which we may need to do if this ends up failing).

        Modified from: https://stackoverflow.com/a/12222317
        """
        script = """
            var getPathTo = function(el) {
                if (!(el instanceof Element))
                    return;
                var path = [];
                while (el.nodeType === Node.ELEMENT_NODE) {
                    var selector = el.nodeName.toLowerCase();
                    // // NOTE: we removed this because web pages often use
                    // // strange characters in ID names which cause the CSS
                    // // selector to fail upon lookup. If we only use traversal
                    // // methods, we don't have that webpage-specific problem
                    // if (el.id) {
                    //     selector += '#' + el.id;
                    //     path.unshift(selector);
                    //     break;
                    // }

                    var sib = el, nth = 1;
                    while (sib = sib.previousElementSibling) {
                        if (sib.nodeName.toLowerCase() == selector)
                           nth++;
                    }

                    // // NOTE: always give a nth-of-type tag, even if
                    // // if there's only a single sibling, just to be
                    // // extra-specific
                    // if (nth != 1)

                    selector += ":nth-of-type("+nth+")";
                    path.unshift(selector);
                    el = el.parentNode;
                }
                return path.join(" > ");
            }

            // NOTE: this used to have a toLowerCase on it, but it caused
            // problems with some pages. Leaving it as it was found in the
            // original DOM is best here.
            return getPathTo(arguments[0]); //.toLowerCase();
        """
        return self.driver.execute_script(script, element)

    def clickable_sanity_check(self, element):
        if not element.is_displayed() and not element.is_enabled():
            logger.debug(" - Skipping non-displayed: %s" % (element))
            return False
        return super().clickable_sanity_check(element)

    def get_inputs(self, form=None, itype=None, root_node=None):
        return super().get_inputs(form=form, itype=itype, root_node=self.driver)

    def get_clickable(self, path=None):
        """
        Get all clickable element tags on the current page.

        TODO: In the future we may need to recurse the page to find
        other clickable types like JS-enabled divs, etc.
        """
        xpath = path or "|".join([
            "//a", "//button", "//input[@type='submit']",
            "//input[@type='button']"
        ])
        return super().get_clickable(path=xpath)
