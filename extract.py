#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Autoscrape Extractor - A wrapper around Hext for
walking a directory and extracting all structured
data using a provided Hext template.

Hext templates can be created using the JavaScript
UI found in ./hext_builder_ui.

Usage:
    extract.py <input-directory> <hext-template> [options]

Options:
    --output-file FILENAME
        By default, all output will be printed to stdout.
        This option directs all output to a specified file.
"""
from docopt import docopt
import html5lib
import hext


def parse_html_file(filepath):
    with open(filepath, "r") as f:
        html = f.read()
    return html5lib.parse(
        html, treebuilder='lxml', namespaceHTMLElements=False
    )


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

    elif option == "extract":
        # TODO: walk directory, feed files to below:
        rule = hext.Rule(strhext)
        document = hext.Html(strhtml)
        result = rule.extract(document)

