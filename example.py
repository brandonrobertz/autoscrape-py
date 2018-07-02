#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import argparse
import autoscrape


def parse_args():
    desc = 'Example of running various autoscrapers.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        'baseurl', type=str,
        help='The base URL to begin scraping.')
    parser.add_argument(
        '--scraper', type=str, default="test",
        help='Which scraper to use. Default is the test DFS scraper.')
    parser.add_argument(
        '--maxdepth', type=int, default=10,
        help='Maximum depth to allow the scraper to traverse.')
    parser.add_argument(
        '--loglevel', type=str, default="INFO",
        help='Log level. Default: INFO. Options: DEBUG, INFO, WARN, ERROR')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    if args.scraper == "test":
        kwargs = {
            "maxdepth": args.maxdepth,
        }
        if args.loglevel:
            kwargs["loglevel"] = args.loglevel
        autoscrape.TestScraper(args.baseurl, **kwargs).run()
    else:
        print("No scraper found for %s" % args.scraper)

