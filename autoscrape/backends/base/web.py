# -*- coding: UTF-8 -*-


class WebBase:
    """
    Stateful base of a web scraper. This class deals with finding and interacting
    with elements and tags. It also holds the base state variables like
    current url.
    """

    def __init__(self, leave_host=False, current_url=None, current_html=None):
        self.leave_host = leave_host
        self.current_url = current_url
        self.current_html = current_html

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

    def element_by_tag(self, tag):
        """
        For a given tag, return the specified element.
        """
        raise NotImplementedError("Tagger.element_by_tag not implemented")

    def get_stylesheet(self):
        """
        Return the text of all loaded CSS stylesheets.
        """
        raise NotImplementedError("Tagger.get_stylesheet not implemented")

