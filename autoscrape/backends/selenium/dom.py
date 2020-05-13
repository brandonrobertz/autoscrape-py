# -*- coding: utf-8 -*-
import logging
import re

try:
    from selenium.common.exceptions import (
        NoSuchElementException, StaleElementReferenceException,
        NoSuchFrameException
    )
except ModuleNotFoundError:
    # we haven't installed selenium backend deps
    pass

from autoscrape.backends.base.dom import DomBase


logger = logging.getLogger('AUTOSCRAPE')


class FrameTransparentList(list):
    def __init__(self, *args, **kwargs):
        self.driver = kwargs.pop("driver")
        super().__init__(*args, **kwargs)

    def __getitem__(self, index):
        raw_item = super().__getitem__(index)
        if not isinstance(raw_item, list):
            self.driver.switch_to.default_content()
            return raw_item
        iframe_ix, element = raw_item
        self.driver.switch_to.frame(iframe_ix)
        return element

    def __iter__(self):
        for raw_item in list.__iter__(self):
            if not isinstance(raw_item, list):
                self.driver.switch_to.default_content()
                yield raw_item
                continue
            iframe_ix, element = raw_item
            self.driver.switch_to.frame(iframe_ix)
            yield element
            self.driver.switch_to.default_content()


class Dom(DomBase):
    def element_attr(self, element, name, default=None):
        return element.get_attribute(name)

    def iframe_capable_lookup(self, tag):
        try:
            self.driver.switch_to.default_content()
            return self.driver.find_element_by_css_selector(tag)
        except NoSuchElementException:
            pass
        self.driver.switch_to.default_content()
        iframes = self.driver.find_elements_by_tag_name("iframe")
        for iframe_ix in range(len(iframes)):
            try:
                self.driver.switch_to.frame(iframe_ix)
            except NoSuchFrameException:
                continue
            try:
                return self.driver.find_element_by_css_selector(tag)
            except NoSuchElementException:
                continue
            self.driver.switch_to.default_content()
        logger.debug("[!] No element found for tag: %s" % (tag))
        return None

    def element_by_tag(self, tag):
        """
        Take a tag and return the corresponding live element in the DOM.
        """
        inside_id = False
        # escaping logic
        newtag = ""
        for c in tag:
            if c == "#":
                inside_id = True
                newtag += c
                continue

            # end of ID
            elif inside_id and re.search("\s", c):
                inside_id = False

            elif inside_id and c in self.css_escapables:
                for escapable in self.css_escapables:
                    c = "\%s" % escapable

            newtag += c

        if newtag != tag:
            logger.debug("Original tag: %s, newtag: %s" % (tag, newtag))
            tag = newtag

        return self.iframe_capable_lookup(tag)

    def elements_by_path(self, xpath, from_element=None):
        """
        Get all elements, across all iframes. We output a
        FrameTransparentList which is a normal list of elements, but it will
        switch to the correct frame upon accessing/iterating to
        each element.
        """
        if from_element is None:
            from_element = self.driver
        return from_element.find_elements_by_xpath(xpath)
        iframes = from_element.find_elements_by_tag_name("iframe")
        if not len(iframes):
            return from_element.find_elements_by_xpath(xpath)
        # gather all elements from iframe
        elements = from_element.find_elements_by_xpath(xpath)
        for iframe_ix in range(len(iframes)):
            self.driver.switch_to.frame(iframe_ix)
            for el in self.driver.find_elements_by_xpath(xpath):
                elements.append([iframe_ix, el])
            self.driver.switch_to.default_content()
        self.driver.switch_to.default_content()
        return FrameTransparentList(elements, driver=self.driver)

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

    def _text_via_many_means(self, el):
        text = []
        try:
            txt = el.text
            if txt:
                text.append(txt.strip())
        except Exception as e:
            logger.error("Error getting text element: %s, Err: %s" % (
                el, e))

        title = el.get_attribute("title")
        if title:
            text.append(title.strip())

        try:
            placeholder = el.get_attribute("placeholder")
            if placeholder:
                text.append(placeholder.strip())
        except Exception as e:
            logger.error("Error getting placeholder: %s, Error: %s" % (
                el, e))

        img_els = el.find_elements_by_tag_name("img")
        for img in img_els:
            try:
                text.append(img.get_attribute("alt"))
            except StaleElementReferenceException as e:
                logger.error("Error getting image text: %s, Error: %s" % (
                    img, e
                ))

        if self.element_tag_name(el) == "input":
            text.append(el.get_attribute("value"))

        return " ".join(text).replace("\n", "").strip()

    def element_text(self, element, block=False):
        """
        Get the text for all elements either under a given element
        or for a whole page (if element == None)
        """
        if not block and element is not None:
            return self._text_via_many_means(element)

        if element is None:
            element = self.driver

        return element.text

    def element_tag_name(self, element):
        if element is None:
            return ""
        return element.tag_name

    def element_value(self, element):
        return element.get_attribute("value")

    def element_displayed(self, element):
        fn_names = ["is_displayed", "is_enabled"]
        for fn_name in fn_names:
            if not hasattr(element, fn_name):
                continue
            try:
                if not getattr(element, fn_name)():
                    return False
            except StaleElementReferenceException as e:
                pass
        return True
