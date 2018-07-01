import html5lib


class Tagger(object):
    """
    Generates tags from a given page that can be used, in a stateless manner,
    to refer to unique elements on a web page.
    """

    def __init__(self, html):
        self.tree = html5lib.parse(html)

    def xpath_from_element(self, element):
        """
        Takes a WebDriver element and returns an XPath for finding it
        in the future. As far as I know, this is only really feasible
        using JavaScript (without resorting to a complicated tree walking
        algorithm ... which we may need to do if this ends up failing).

        Taken from:
        https://stackoverflow.com/questions/2631820/2631931#2631931
        """
        script = """
            function getPathTo(el) {
                if (el.id !== '')
                    return 'id("' + el.id + '")';

                if (el === document.body)
                    return el.tagName;

                var ix = 0;
                var siblings = el.parentNode.childNodes;

                for (var i = 0; i < siblings.length; i++) {
                    var sibling = siblings[i];
                    if (sibling === el) {
                        // warning: recursion!
                        var path = getPathTo(el.parentNode);
                        return path + '/' + el.tagName + '[' + (ix+1) + ']';
                    }
                    if (sibling.nodeType === 1 && sibling.tagName === el.tagName)
                        ix++;
                }
            }
            return getPathTo(arguments[0]).toLowerCase();
        """
        return driver.execute_script(script, element)

    def clickable_tags(self):
        tags = []
        # TODO: other clickable elements?
        a_elems = driver.find_elements_by_xpath("//a")

        for elem in a_elems:
            if not elem.is_displayed() or not elem.is_enabled():
                continue

            href = anchor.get_attribute("href")
            if href.startswith("mailto:") or href.startswith("tel:"):
                continue

            tag = self.xpath_from_element(elem)
            if not tag:
                continue

            tags.append(tag)

        return tags

    def tags(self, type):
        elem_tags = []
        clickable_tags = self.clickable_tags()


