# -*- coding: UTF-8 -*-
import logging

from autoscrape.backends.base.tags import TaggerBase
from autoscrape.backends.requests.dom import Dom


logger = logging.getLogger('AUTOSCRAPE')


class Tagger(TaggerBase, Dom):
    def tag_from_element(self, el):
        path = []
        while el is not None:
            nth = 1
            parent = el.getparent()
            children = []
            if parent is not None:
                children = parent.getchildren()
            for child in children:
                if child == el:
                    break
                if child.tag == el.tag:
                    nth += 1
            selector = "%s:nth-of-type(%s)" % (
                el.tag, nth
            )
            path.insert(0, selector)
            el = parent
        tag = " > ".join(path)
        return tag

    def get_inputs(self, form=None, itype=None, root_node=None):
        return super().get_inputs(form=form, itype=itype, root_node=self.dom)

    def get_buttons(self, in_form=False, path=None):
        x_path = path or "|".join([
            "//form//a", "//input[@type='submit']", "//table//a",
        ])
        return super().get_buttons(in_form=in_form, path=x_path)

    def get_clickable(self, path=None):
        clickable = super().get_clickable(path="//a|//iframe")
        return clickable

    def clickable_sanity_check(self, element):
        raw_href = self.element_attr(element, "href")

        tag_name = self.element_tag_name(element)
        if tag_name == "iframe":
            raw_href = self.element_attr(element, "src")

        if not raw_href:
            return False

        href = self._normalize_url(raw_href).split("#")[0]
        if href.split("#")[0] == self.current_url:
            return False

        # skip any weird protos ... we whitelist notrmal HTTP,
        # anchor tags and blank tags (to support JavaScript & btns)
        if href and href.startswith("javascript"):
            return False

        return super().clickable_sanity_check(element, href=href)
