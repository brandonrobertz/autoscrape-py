# -*- coding: UTF-8 -*-
import hashlib
import logging
import os
import re
import time

from urllib.parse import urlparse

from ..filetypes import TEXT_EXTENSIONS


logger = logging.getLogger('AUTOSCRAPE')


class BaseScraper(object):
    """
    A base class for common scraper functionality like loglevel
    parsing & setup, file saving, etc.
    """
    def setup_logging(self, loglevel=None):
        if not loglevel or loglevel == "DEBUG":
            loglevel = logging.DEBUG
        elif loglevel == "INFO":
            loglevel = logging.INFO
        elif loglevel == "WARN":
            loglevel = logging.WARN
        elif loglevel == "ERROR":
            loglevel = logging.ERROR

        logger.setLevel(loglevel)
        console_handler = logging.StreamHandler()
        logger.addHandler(console_handler)

    def save_screenshot(self, classname=None):
        """
        Save a screenshot of the current page window. The files
        created by this are quite large and also only contain the
        first, above-the-fold content.

        Screenshots are saved by the timestamp and the "class"
        of the page currently visited (data_page, etc).
        """
        if not self.output_data_dir or not self.save_screenshots:
            return

        if classname not in self.training_classes:
            raise ValueError("Base class speficied: %s" % classname)

        screenshot_dir = os.path.join(self.output_data_dir, "screenshots")
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)

        filepath = os.path.join(screenshot_dir, "%s_%s.png" % (
            int(time.time()), classname
        ))
        logger.debug("Saving screenshot to file: %s." % filepath);
        with open(filepath, "wb") as f:
            png = self.control.scraper.driver.get_screenshot_as_png()
            f.write(png)

    def get_filename_from_url(self, url):
        """
        Take a fully-qualified URL and turn it into a filename. For
        example, turn a url like this:

            https://www.cia.gov/library/readingroom/docs/%5B15423241%5D.pdf

        Using the parsed URL:

            ParseResult(scheme='https', netloc='www.cia.gov',
                path='/library/readingroom/docs/%5B15423241%5D.pdf

        Returing this representation (a string):

            _library_readingroom_docs_%5B15423241%5D.pdf

        NOTE: If no extension is found on the page, .html is appended.
        """
        parsed = urlparse(url)
        host = parsed.netloc
        file_part = parsed.path.replace("/", "_")
        extension = os.path.splitext(parsed.path)[1] or ".html"
        filename = "%s_%s" % (host, file_part)
        if parsed.query:
            query_part = "_".join(parsed.query.split("&"))
            filename = "%s__%s" % (filename, query_part)
        return "%s%s" % (filename, extension)

    def save_training_page(self, classname=None):
        """
        Writes the current page to the output data directory (if provided)
        to the given class folder.
        """
        if not self.output_data_dir:
            logger.debug("No output data dir! Not saving data.")
            return

        logger.debug("Saving training page for class: %s" % classname)
        if classname not in self.training_classes:
            raise ValueError("Base class speficied: %s" % classname)

        classdir = os.path.join(self.output_data_dir, classname)
        if not os.path.exists(classdir):
            os.makedirs(classdir)

        data = self.control.scraper.page_html
        url = self.control.scraper.page_url

        # try and extract the extension from the URL
        path = urlparse(url).path
        ext = os.path.splitext(path)[1]
        ext = ext if ext else ".html"
        if ext[0] == ".":
            ext = ext[1:]

        # try a dynamic ajax download via injected script
        if ext not in TEXT_EXTENSIONS:
            data = self.control.scraper.download_page(url)

        # hash the contents of the file, so we don't *not* save dynamic
        # JS pages with the same URl and that we *don't* excessively save
        # the same page over and over
        if type(data) == bytes:
            sha256 = hashlib.sha256()
            sha256.update(data)
            h = sha256.digest().hex()
            writetype = "wb"
        else:
            h = hashlib.sha256(data.encode("utf-8")).digest().hex()
            writetype = "w"

        logger.debug("URL: %s, Hash: %s, Extension: %s" % (url, h, ext))

        # don't use the hash, use the filename from URL
        if self.keep_filename:
            parsed_filename = self.get_filename_from_url(url)
            logger.debug("Parsed output filename: %s" % parsed_filename)
            filepath = os.path.join(classdir, parsed_filename)
        # use the hash as the output filename
        else:
            filepath = os.path.join(classdir, "%s%s" % (h, ext))

        with open(filepath, writetype) as f:
            f.write(data)

