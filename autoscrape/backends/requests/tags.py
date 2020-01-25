import logging
from urllib.parse import urlparse

import lxml.html

from autoscrape.backends.base.tags import TaggerBase
from autoscrape.backends.requests.dom import Dom


logger = logging.getLogger('AUTOSCRAPE')


class Tagger(TaggerBase, Dom):
    def tag_from_element(self, el):
        path = []
        while el is not None:
            siblings = []
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

