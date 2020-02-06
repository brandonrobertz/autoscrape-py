# -*- coding: UTF-8 -*-
import logging
import os
import re
import urllib

from autoscrape.util import write_file, get_filename_from_url


logger = logging.getLogger('AUTOSCRAPE')


class DomBase:
    """
    Stateful base of a web scraper. This class deals with finding and interacting
    with elements and tags. It also holds the base state variables like
    current url.
    """

    def __init__(self, leave_host=False, current_url=None, current_html=None):
        self.leave_host = leave_host
        self.current_url = current_url
        self.current_html = current_html

    def elements_by_path(self, path, from_element=None):
        """
        Return element nodes matching a path where path could be xpath,
        css, etc, depending on the backend)
        """
        raise NotImplementedError("DomBase.elements_by_path not implemented")

    def element_attr(self, element, name, default=None):
        """
        For a given element and attribute name, return the value if it
        exists.
        """
        raise NotImplementedError("DomBase.element_attr not implemented")

    def element_by_tag(self, tag):
        """
        For a given tag, return the specified element.
        """
        raise NotImplementedError("DomBase.element_by_tag not implemented")

    def get_stylesheet(self):
        """
        Return the text of all loaded CSS stylesheets.
        """
        raise NotImplementedError("DomBase.get_stylesheet not implemented")

    def element_tag_name(self):
        """
        Return the tag name of the given element.
        """
        raise NotImplementedError("DomBase.element_tag_name not implemented")

    def element_text(self, element, block=False):
        """
        Return the text of an element, or the combined text of all its
        descendants (if block=True).
        """
        raise NotImplementedError("DomBase.element_text not implemented")

    def element_value(self, element):
        """
        Return the text value of an element (e.g., input element). Since
        this is usually called like element.value() or element.value, we
        wrap this functionality here.
        """
        if not hasattr(element, "value"):
            raise NotImplementedError("DomBase.element_value not implemented")
        return element.value

    def element_name(self, element):
        """
        Return the name of an element (e.g., input element).        """
        if not hasattr(element, "name"):
            raise NotImplementedError("DomBase.element_name not implemented")
        return element.name

    def download_file(self, url, return_data=False):
        """
        Fetch the given url, returning a byte stream of the page data. This
        really is only useful in situations where the scraper is on a binary
        filetype, such as PDF, etc.

        Note that we're doing this as opposed to some XHR thing inside the
        selenium driver due to CORS issues.
        """
        logger.debug("Fetching non-HTML page directly: %s" % url)
        user_agent = (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64; rv:62.0) "
            "Gecko/20100101 Firefox/62.0"
        )
        request = urllib.request.Request(url, headers={
            "User-Agent": user_agent,
            "Referrer": self.page_url,
        })

        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as e:
            logger.debug("[!] HTTP error while downloading: %s" % (e))
            return

        data = response.read()
        action = {
            "action": "download_file",
            "url": url,
        }
        self.graph.add_action_to_current(action)
        if return_data:
            return data

        # always keep filename for downloads, for now
        if re.match("^https?://", self.output):
            dl_dir = "downloads"
        else:
            dl_dir = os.path.join(self.output, "downloads")

        parsed_filename = get_filename_from_url(url)
        logger.debug("Parsed output filename: %s" % parsed_filename)
        filepath = os.path.join(dl_dir, parsed_filename)
        write_file(
            filepath, data, fileclass="download", writetype="wb",
            output=self.output, url=self.page_url,
        )

    def _no_tags(self, list, l_type="path"):
        clean = []
        for p in list:
            name, args, kwargs = p
            if name == "click":
                args[0] = "tag"
            clean.append((name, args, kwargs))
        return clean
