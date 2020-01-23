# -*- coding: UTF-8 -*-
import os
import re
import urllib.request

from autoscrape.util import write_file


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

    def element_tag_name(self):
        """
        Return the tag name of the given element.
        """
        raise NotImplementedError("Tagger.element_tag_name not implemented")

    def download_file(self, url, return_data=False):
        """
        Fetch the given url, returning a byte stream of the page data. This
        really is only useful in situations where the scraper is on a binary
        filetype, such as PDF, etc.

        Note that we're doing this as opposed to some XHR thing inside the
        selenium driver due to CORS issues.
        """
        print("Fetching non-HTML page directly: %s" % url)
        user_agent = (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64; rv:62.0) "
            "Gecko/20100101 Firefox/62.0"
        )
        request = urllib.request.Request(url, headers={
            "User-Agent": user_agent,
            "Referrer": self.page_url,
        })
        response = urllib.request.urlopen(request)
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
            output=self.output
        )

