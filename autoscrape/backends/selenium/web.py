# -*- coding: UTF-8 -*-
import logging

from autoscrape.backends.base.web import WebBase


logger = logging.getLogger('AUTOSCRAPE')


class Web(WebBase):
    def element_attr(self, element, name):
        return element.get_attribute(name)

    def element_by_tag(self, tag):
        return self.dom.cssselect(tag)[0]

    def elements_by_path(self, xpath):
        return self.driver.find_elements_by_xpath(xpath)

    def get_stylesheet(self):
        script = """
        return [].slice.call(document.styleSheets)
          .reduce((prev, styleSheet) => {
            try {
              if (styleSheet.cssRules) {
                return prev +
                  [].slice.call(styleSheet.cssRules)
                    .reduce(function (prev, cssRule) {
                      return prev + cssRule.cssText;
                    }, '');
              } else {
                  return prev;
              }
            } catch (e) {
              return prev + `@import url("${styleSheet.href}");`
            }
          }, '');"""
        return self.driver.execute_script(script)

    def element_text(self, element=None):
        """
        Get the text for all elements either under a given element
        or for a whole page (if element == None)
        """
        if element is None:
            element = self.driver
        # TODO: this is a major bottleneck. find a way
        # to ensure all text of children is extracted
        # (non-duplicately via descendants) in a more
        # performant way
        elems = element.find_elements_by_xpath(".//*")
        text = []
        for el in elems:
            try:
                txt = el.text
                if txt:
                    text.append(txt.strip())
            except Exception as e:
                logger.error("Error getting text element: %s, Err: %s" % (
                    el, e))

            try:
                placeholder = el.get_attribute("placeholder")
                if placeholder:
                    text.append(placeholder.strip())
            except Exception as e:
                logger.error("Error getting placeholder: %s, Error: %s" % (
                el, e))

        logger.debug("Element texts: %s" % text)
        return " ".join(text)

