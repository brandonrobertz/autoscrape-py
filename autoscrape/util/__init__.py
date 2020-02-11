# -*- coding: UTF-8 -*-
import base64
import json
import logging
import os
import re
from urllib import parse

import requests


logger = logging.getLogger('AUTOSCRAPE')


def get_filename_from_url(url):
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
    parsed = parse.urlparse(url)
    host = parsed.netloc
    # split filename/path and extension
    file_parts = os.path.splitext(parsed.path)
    file_part = file_parts[0].replace("/", "_")
    extension = file_parts[1] or ".html"
    filename = "%s_%s" % (host, file_part)
    if parsed.query:
        query_part = "_".join(parsed.query.split("&"))
        filename = "%s__%s" % (filename, query_part)
    return "%s%s" % (filename, extension)


def get_extension_from_url(url):
        # try and extract the extension from the URL
    path = parse.urlparse(url).path
    ext = os.path.splitext(path)[1]
    ext = ext if ext else "html"
    if ext[0] == ".":
        ext = ext[1:]
    return ext


def write_file(filepath, data, fileclass=None, writetype="w", output=None,
               url=None):
    """
    Write out a scraped data file to disk or a remote callback,
    specified in output parameter.
    """
    logger.debug("[.] Writing file: %s to: %s" % (filepath, output))
    if not output:
        return

    # Rest API callback mode
    if re.match("^https?://", output):
        # (b64encode) bytes -> (decode) str
        if type(data) == bytes:
            encoded = base64.b64encode(data).decode()
        else:
            encoded = base64.b64encode(bytes(data, "utf-8")).decode()
        payload = {
            "name": filepath,
            "data": encoded,
            "url": url,
        }
        if fileclass:
            payload["fileclass"] = fileclass
            post_data = json.dumps(payload).encode("utf-8")
            headers = {
                "content-type": "application/json"
            }
            r = requests.post(
                output, data=post_data, headers=headers
            )
            r.status_code

    # filesystem mode
    else:
        dirpath = os.path.dirname(filepath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        with open(filepath, writetype) as f:
            f.write(data)
