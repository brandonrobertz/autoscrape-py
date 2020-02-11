# -*- coding: UTF-8 -*-
import io
import logging
import os
import pickle

from autoscrape.backends.requests.browser import RequestsBrowser
from autoscrape.backends.requests.tags import Tagger
from autoscrape.search.graph import Graph


logger = logging.getLogger('AUTOSCRAPE')


try:
    import plyvel
    import warc
except ModuleNotFoundError:
    pass


class WARCBrowser(RequestsBrowser):
    def __init__(self, warc_index_file=None, warc_directory=None,
                 leave_host=False, **kwargs):
        no_dir_msg = "Error: No warc_directory specified for WARCBrowser"
        assert warc_directory is not None, no_dir_msg

        no_index_msg = "Error: No warc_index_file specified for WARCBrowser"
        assert warc_index_file is not None, no_index_msg

        # leveldb directory
        self.warc_index_file = warc_index_file
        # directory containing Common Crawl WARCs
        self.warc_directory = warc_directory

        # WARC index: URL => (filename, record_number)
        self.warc_index = self._build_warc_index()
        # WARC cache: filename => [record1, ..., recordN]
        self.warc_cache = {}
        self.warc_directory = warc_directory

        # how many WARC files to keep in memory at a given time
        # since the crawls are sequential, most files for a site
        # will exist in a segment of a few WARC files.
        self.warc_cache_size = 20
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

    def _warc_payload(self, record):
        """
        Extract the body from a WARC response "payload".
        """
        # find the initial blank line, indicating body starts
        line = True
        while line:
            line = record.payload.readline().strip()
        payload = ""
        for line in record.payload:
            cleaned = line.decode("utf-8").strip()
            payload += cleaned
        return payload

    def _warc_record_sane(self, record):
        if record.type != "response":
            return False
        if "WARC-Target-URI" not in record:
            return False
        return True

    def _build_warc_index(self):
        """
        Read through all WARC files in self.warc_directory and build
        an index: URL => filename, record_number
        """
        db = plyvel.DB(self.warc_index_file, create_if_missing=True)
        blank = True
        for rec in db.iterator():
            blank = False
            break
        if not blank:
            logger.debug("[.] Loaded WARC index: %s" % (self.warc_index_file))
            return db
        logger.info("[.] Building WARC index. This might take a while...")
        _, _, filenames = list(os.walk(self.warc_directory))[0]
        for basename in filenames:
            filename = os.path.join(self.warc_directory, basename)
            if not filename.endswith(".warc.gz"):
                continue
            logger.debug(" - Parsing %s" % (filename))
            record_number = -1
            for record in warc.open(filename):
                if not self._warc_record_sane(record):
                    continue
                record_number += 1
                uri = record["WARC-Target-URI"]
                uri_bytes = bytes(uri, "utf-8")
                value = pickle.dumps((filename, record_number))
                db.put(uri_bytes, value)
        return db

    def _load_warc_file(self, filename):
        """
        Take a specified WARC file, load it and keep it in memory in a quickly
        readable format (python dict). This operates directly on the class
        variable self.warc_cache and also handles maximum cache size pruning.
        """
        logger.debug("[-] Loading WARC file: %s" % (filename))
        if len(self.warc_cache_stack) > self.warc_cache_size:
            least_used = self.warc_cache_stack.pop()
            del self.warc_cache[least_used]

        self.warc_cache[filename] = []
        for record in warc.open(filename):
            if not self._warc_record_sane(record):
                continue
            payload = self._warc_payload(record)
            if not payload:
                payload = "<html></html>"
            self.warc_cache[filename].append({
                "header": {k: v for k,v in record.header.items()},
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
            self.current_html = "<html></html>"
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

