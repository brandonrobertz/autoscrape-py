# -*- coding: UTF-8 -*-
import io
import logging
import os
import pickle
import sys

from autoscrape.backends.requests.browser import RequestsBrowser
from autoscrape.backends.requests.tags import Tagger
from autoscrape.search.graph import Graph
from autoscrape.util.warc import build_warc_index, _warc_records


logger = logging.getLogger('AUTOSCRAPE')


try:
    import plyvel
    import warcio
except ModuleNotFoundError:
    pass


class WARCBrowser(RequestsBrowser):
    def __init__(self, warc_index_file=None, warc_directory=None,
                 filter_domain=None, leave_host=False, **kwargs):
        try:
            warcio
        except NameError:
            logger.debug(
                "WARC dependencies not installed."
                " (Hint: pip install autoscrape[warc-backend])"
                " Exiting."
            )
            sys.exit(1)

        no_dir_msg = "Error: No warc_directory specified for WARCBrowser"
        assert warc_directory is not None, no_dir_msg

        no_index_msg = "Error: No warc_index_file specified for WARCBrowser"
        assert warc_index_file is not None, no_index_msg

        # leveldb directory
        self.warc_index_file = warc_index_file
        # directory containing Common Crawl WARCs
        self.warc_directory = warc_directory
        # only build index for a specific domain
        self.filter_domain = filter_domain

        # WARC index: URL => (filename, record_number)
        self.warc_index = plyvel.DB(self.warc_index_file, create_if_missing=True)
        build_warc_index(
            db=self.warc_index, warc_directory=self.warc_directory,
            filter_domain=self.filter_domain
        )
        # WARC cache: filename => [record1, ..., recordN]
        self.warc_cache = {}
        self.warc_directory = warc_directory

        # how many WARC files to keep in memory at a given time
        # since the crawls are sequential, most files for a site
        # will exist in a segment of a few WARC files.
        self.warc_cache_size = 2
        # we're going to store the order the files have have been
        # accessed most recently here:
        #     [most_recently_used_filename, ..., least_recently_used_filename]
        # This will be used to enforce our cache size.
        self.warc_cache_stack = []

        # set of clicked elements
        self.visited = set()

        # queue of the path that led us to the current page
        # this is in the form of (command, *args, **kwargs)
        self.path = []

        # tree building
        self.graph = Graph()

        # setting to False, ensures crawl will stay on same host
        self.leave_host = leave_host

        self.current_url = None
        self.current_html = None

    def _load_warc_file(self, filename):
        """
        Take a specified WARC file, load it and keep it in memory in a quickly
        readable format (python dict). This operates directly on the class
        variable self.warc_cache and also handles maximum cache size pruning.
        """
        logger.debug("[-] Loading WARC file: %s" % (filename))
        if len(self.warc_cache_stack) > self.warc_cache_size:
            least_used = self.warc_cache_stack.pop()
            logger.debug(" - Removing WARC from memory: %s" % (filename))
            del self.warc_cache[least_used]

        self.warc_cache[filename] = []
        for record in _warc_records(filename):
            payload = record["payload"]
            if not payload:
                payload = "<html></html>"
            self.warc_cache[filename].append({
                "header": record["headers"],
                "payload": payload,
            })

    def fetch(self, url, initial=False):
        """
        Fetch a page from a given URL from the WARC archive (via
        an index).
        """
        logger.info("%s Fetching url=%s initial=%s" % (
            ("[+]" if initial else " -"), url, initial,
        ))
        url_b = bytes(url, "utf-8")
        data = self.warc_index.get(url_b)
        if not data:
            logger.debug("[!] Couldn't find URL in WARC index: %s" % (url))
            return False
        else:
            filename, record_number = pickle.loads(data)
            logger.debug(" -  Loading filename: %s record number: %s" % (
                filename, record_number
            ))
            if filename not in self.warc_cache:
                self._load_warc_file(filename)
            warcfile = self.warc_cache[filename]
            record = warcfile[record_number]
            self.current_html = record["payload"]

            try:
                self.warc_cache_stack.remove(filename)
            except ValueError:
                pass

            self.warc_cache_stack.insert(0, filename)

        self.current_url = url
        self.dom = self._get_dom()

        if initial:
            self.path.append(("fetch", [url], {"initial": initial}))
            node = "Fetch\n url: %s" % url
            self.graph.add_root_node(node, url=url, action="fetch")

        return True
