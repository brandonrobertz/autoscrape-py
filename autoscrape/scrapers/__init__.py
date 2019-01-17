# -*- coding: UTF-8 -*-
import hashlib
import logging
import os
import re
import time

from urllib.parse import urlparse

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
        return self.control.scraper.driver.execute_script(script)

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

        screenshot_dir = os.path.join(self.output_data_dir, "screenshots")

        filepath = os.path.join(screenshot_dir, "%s_%s.png" % (
            int(time.time()), classname
        ))

        logger.debug("Saving screenshot to file: %s." % filepath)
        # only FF has this capability, it removes the scrollbar
        if self.control.scraper.driver == "Firefox":
            self.control.scraper.driver.find_element_by_tag_name(
                'html'
            ).screenshot(filepath)
        else:
            write_file(
                filepath, png, fileclass="screenshot",
                writetype="wb", output_data_dir=self.output_data_dir
            )

        # restore original window size to avoid side effects
        self.control.scraper.driver.set_window_size(
            original_size['width'], original_size['height']
        )

    def save_training_page(self, classname=None):
        """
        Writes the current page to the output data directory (if provided)
        to the given class folder.
        """
        if not self.output_data_dir:
            return

        logger.debug("Saving training page for class: %s" % classname)
        if classname not in self.training_classes:
            raise ValueError("Base class speficied: %s" % classname)

        # always keep filename for downloads, for now
        if re.match("^https?://", self.output_data_dir):
            classdir = classname
        else:
            classdir = os.path.join(self.output_data_dir, classname)

        data = self.control.scraper.page_html
        url = self.control.scraper.page_url

        ext = get_extension_from_url(url)
        if ext not in TEXT_EXTENSIONS:
            data = self.control.scraper.download_file(url, return_data=True)
            classname = "downloads"

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

        write_file(
            filepath, data, fileclass=classname,
            writetype=writetype, output_data_dir=self.output_data_dir
        )

        # only save stylesheets for web content types
        if not self.disable_style_saving and ext in TEXT_EXTENSIONS:
            logger.debug("Saving stylesheet")
            style_filepath = "%s.css" % filepath
            # this will save stylesheet as filepath.html.css
            write_file(
                style_filepath, self.get_stylesheet(), fileclass=classname,
                output_data_dir=self.output_data_dir
            )

    def save_scraper_graph(self):
        """
        Saves our graph that was built throughout the scrape. This can
        be used to visualize the scrape, debug it, and replicate it.

        Graph is saved to the graph subdirectory of the output_data_dir
        path, with the filename a microscond timestamp with the .gpickle
        extension.

        If output_data_dir is not set, then calling this function has no
        effect.
        """
        if not self.output_data_dir or not self.save_graph:
            logger.debug("No output-data-dir or save-graph options. Not saving")
            return

        filename = "%s.gpickle" % int(time.time() * 1000)
        basedir = os.path.join(self.output_data_dir, "graph")
        if not os.path.exists(basedir):
            logger.debug("Creating graph subdir: %s" % basedir)
            os.makedirs(basedir)

        graph_save_path = os.path.join(basedir, filename)
        logger.debug("Saving graph to: %s" % graph_save_path)
        self.control.scraper.graph.save_graph(graph_save_path)

