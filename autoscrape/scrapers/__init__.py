# -*- coding: UTF-8 -*-
import logging


logger = logging.getLogger('AUTOSCRAPE')


class BaseScraper(object):
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

