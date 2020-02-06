# -*- coding: UTF-8 -*-
import datetime
import hashlib
import logging
import os
import re
import sys
import time

from ..filetypes import TEXT_EXTENSIONS
from ..util import (
    get_filename_from_url, get_extension_from_url, write_file
)


logger = logging.getLogger('AUTOSCRAPE')


class BaseScraper(object):
    """
    A base class for common scraper functionality like loglevel
    parsing & setup, file saving, etc.
    """

    def setup_logging(self, loglevel=None, stdout=False):
        if loglevel == "DEBUG":
            loglevel = logging.DEBUG
        elif not loglevel or loglevel == "INFO":
            loglevel = logging.INFO
        elif loglevel == "WARN":
            loglevel = logging.WARN
        elif loglevel == "ERROR":
            loglevel = logging.ERROR

        logger.setLevel(loglevel)
        if stdout:
            console_handler = logging.StreamHandler(stream=sys.stdout)
            logger.addHandler(console_handler)

    def save_screenshot(self, classname=None):
        """
        Save a screenshot of the current page window. The files
        created by this are quite large and also only contain the
        first, above-the-fold content.

        Screenshots are saved by the timestamp and the "class"
        of the page currently visited (data_page, etc).
        """
        if not self.output or not self.save_screenshots:
            return

        if classname not in self.training_classes:
            raise ValueError("Base class speficied: %s" % classname)

        if self.full_page_screenshots:
            # adjust the window size to the document size, this captures most
            # web configurations except cases where a footer, for example, has
            # been placed absolutely outside of the body and hangs beneath
            # NOTE: this comes from here: https://stackoverflow.com/a/52572919
            original_size = self.control.scraper.driver.get_window_size()
            required_width = self.control.scraper.driver.execute_script(
                'return document.body.parentNode.scrollWidth'
            )
            required_height = self.control.scraper.driver.execute_script(
                'return document.body.parentNode.scrollHeight'
            )
            logger.debug(
                "Required width=%s, height=%s, Original width=%s, height=%s" % (
                    required_width, required_height, original_size["width"],
                    original_size["height"]
                ))
            self.control.scraper.driver.set_window_size(
                required_width, required_height
            )

        if re.match("^https?://", self.output):
            screenshot_dir = "screenshots"
        else:
            screenshot_dir = os.path.join(self.output, "screenshots")

        filepath = os.path.join(screenshot_dir, "%s_%s.png" % (
            int(time.time()), classname
        ))

        png = None
        if hasattr(self.control.scraper, "driver"):
            logger.debug("[.] Saving screenshot to file: %s." % filepath)
            png = self.control.scraper.driver.get_screenshot_as_png()

        # if self.control.scraper.driver_name == "Firefox":
        #     try:
        #         html_el = self.control.scraper.driver.find_element_by_tag_name(
        #             "html"
        #         )
        #         png = html_el.screenshot_as_png
        #         logger.debug("HTML root for screenshot: %s" % html_el)
        #         logger.debug("DIR: %s" % dir(html_el))
        #     except Exception as e:
        #         logger.warn("Error saving screenshot: %s" % e)

        # elif not png:
        #     try:
        #         png = self.control.scraper.driver.get_screenshot_as_png()
        #     except Exception as e:
        #         logger.warn("Error saving screenshot: %s" % e)

        if png and self.output:
            write_file(
                filepath, png, fileclass="screenshot",
                writetype="wb", output=self.output,
                url=self.control.scraper.page_url,
            )

        if self.full_page_screenshots:
            # restore original window size to avoid side effects
            self.control.scraper.driver.set_window_size(
                original_size['width'], original_size['height']
            )

    def save_training_page(self, classname=None, url=None):
        """
        Writes the current page to the output data directory (if provided)
        to the given class folder.
        """
        if not self.output and not self.return_data:
            return

        logger.debug("[.] Saving training page for class: %s" % classname)
        if classname not in self.training_classes:
            raise ValueError("Base class speficied: %s" % classname)

        # always keep filename for downloads, for now
        if not self.output or re.match("^https?://", self.output):
            classdir = classname
        else:
            classdir = os.path.join(self.output, classname)

        data = None
        if url is None:
            # TODO: migrate over
            data = self.control.scraper.page_html
            url = self.control.scraper.page_url
        else:
            data = self.control.scraper.download_file(url)

        ext = get_extension_from_url(url)
        link_to_text = ext in TEXT_EXTENSIONS
        if not link_to_text:
            data = self.control.scraper.download_file(url, return_data=True)
            classname = "downloads"

        # we had some kind of error downloading
        if data is None:
            return

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
            parsed_filename = get_filename_from_url(url)
            logger.debug("Parsed output filename: %s" % parsed_filename)
            filepath = os.path.join(classdir, parsed_filename)
        # use the hash as the output filename
        else:
            filepath = os.path.join(classdir, "%s.%s" % (h, ext))

        crawl_data = None
        if self.output:
            write_file(
                filepath, data, fileclass=classname,
                writetype=writetype, output=self.output,
                url=self.control.scraper.page_url,
            )
        if self.return_data:
            now = datetime.datetime.utcnow()
            crawl_data = {
                "url": url,
                "html": data,
                "date": now.isoformat(timespec="seconds") + "Z",
            }

        # only save stylesheets for web content types
        if link_to_text and not self.disable_style_saving:
            logger.debug("[.] Saving stylesheet")
            style_filepath = "%s.css" % filepath
            # this will save stylesheet as filepath.html.css
            stylesheet = self.control.scraper.get_stylesheet()
            if self.output:
                write_file(
                    style_filepath, stylesheet,
                    fileclass=classname, output=self.output,
                    url=self.control.scraper.page_url,
                )
            if self.return_data:
                crawl_data["css"] = stylesheet

        if self.return_data:
            self.crawl_data.append(crawl_data)

    def save_scraper_graph(self):
        """
        Saves our graph that was built throughout the scrape. This can
        be used to visualize the scrape, debug it, and replicate it.

        Graph is saved to the graph subdirectory of the output
        path, with the filename a microscond timestamp with the .gpickle
        extension.

        If output is not set, then calling this function has no
        effect.
        """
        if not self.output or not self.save_graph:
            logger.debug("[!] No output or save-graph options. Not saving")
            return

        filename = "%s.gpickle" % int(time.time() * 1000)
        basedir = os.path.join(self.output, "graph")
        if not os.path.exists(basedir):
            os.makedirs(basedir)

        graph_save_path = os.path.join(basedir, filename)
        logger.debug("[.] Saving graph to: %s" % graph_save_path)
        self.control.scraper.graph.save_graph(graph_save_path)
