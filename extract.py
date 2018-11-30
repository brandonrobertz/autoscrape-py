#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Autoscrape Extractor - A simplified method for
converting a source HTML record into a Hext
extractor template and recursively extracting
all structured data from HTML documents found
in a given directory.

Usage:
    extract.py build-template <example-html-record> [options]
    extract.py extract <input-directory> <hext-template> [options]

Options:
    --output-file FILENAME
        By default, all output will be printed to stdout.
        This option directs all output to a specified file.
"""
from docopt import docopt


if __name__ == "__main__":
    docopt_args = docopt(__doc__)

    option = None
    if "build-template" in docopt_args.keys():
        option = "build-template"
        docopt_args.pop("build-template")
    elif "extract" in docopt_args.keys():
        option = "extract"
        docopt_args.pop("extract")

    # strip the -- and convert - to _, remove <>
    args = {}
    for option in docopt_args:
        args[option[2:].replace(
            '<', ''
        ).replace(
            '>', ''
        ).replace(
            '-', '_'
        )] = docopt_args[option]

    if option == "build-template":
        # TODO: open input HTML record, get string
        # TODO: build a hext template from a HTML record
    elif option == "extract":
        # TODO: walk directory, feed files to below:
        rule = hext.Rule(strhext)
        document = hext.Html(strhtml)
        result = rule.extract(document)

