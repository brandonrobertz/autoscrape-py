#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import argparse
import logging
import numpy as np
import os
import pickle
import time

from autoscrape.vectorization import Vectorizer
from autoscrape import NullScraper


class Data:
    def __init__(self, X=None, y=None):
        self.X = X
        self.y = y

    def dump(self, filepath):
        with open(filepath, "wb") as f:
            pickle.dump(self, f)

    def load(self, filepath):
        with open(filepath, "rb") as f:
            tmp_d = pickle.load(f)
            self.X = tmp_d.X
            self.y = tmp_d.y


def parse_args():
    desc = "Convenience script for vectorizing webpage training data."

    parser = argparse.ArgumentParser(
        description=desc,
    )

    parser.add_argument(
        "--html_embeddings", type=str, required=True,
        help="Location of HTML character embeddings file."
    )
    parser.add_argument(
        "--word_embeddings", type=str, required=True,
        help="Location of word embeddings file."
    )
    parser.add_argument(
        "--output_file", type=str, default="data.pickle",
        help="Output file for data matrices."
    )
    parser.add_argument(
        '--loglevel', type=str, default="INFO",
        choices=["DEBUG", "INFO", "WARN", "ERROR"],
        help="Loglevel (default: INFO)"
    )
    parser.add_argument(
        "dir", type=str,
        help=("""
Location of directory containing training HTML data. This directory needs to have the following subdirectories, which correspond to classes: data_pages, error_pages, links_to_documents, links_to_search, search_pages
"""
        )
    )

    args = parser.parse_args()
    return args

def load_file(filename):
    with open(filename, "r") as f:
        return f.read()

if __name__ == "__main__":
    args = parse_args()

    cls_data = {}
    total_records = 0
    for root, dirs, files in os.walk(args.dir):
        cls = root.split("/")[-1]
        if not files or not cls:
            continue

        cls_data[cls] = []
        for file in files:
            filepath = os.path.join(root, file)
            cls_data[cls].append(filepath)

        records = len(cls_data[cls])
        print("Class=%s Records=%s" % (cls, records))
        total_records += records

    print("Total records: %s" % total_records)

    vectorizer = Vectorizer(
        html_embeddings_file=args.html_embeddings,
        word_embeddings_file=args.word_embeddings,
    )

    dim = vectorizer.html.dim + vectorizer.word.dim
    print("Vector dimension: %s" % dim)

    X = np.zeros(shape=(total_records, dim))
    y = np.zeros(shape=(total_records, 1))

    base_dir = os.path.abspath(os.curdir)
    ns = NullScraper(
        loglevel=args.loglevel,
    )

    keys = list(cls_data.keys())
    I = 0
    for ix in range(len(keys)):
        cls = keys[ix]
        for file in cls_data[cls]:
            print("I=%s" % I, end="\r")
            abs_path = os.path.join(base_dir, file)
            print("File=%s, Absolute Path=%s" % (file, abs_path))
            url = "file://%s" % abs_path.replace("#", "%23").replace("%25",
                                                                     "%2525")
            html = load_file(abs_path)
            ns.scraper.fetch(url)
            time.sleep(2)
            text = ns.scraper.element_text()
            x = vectorizer.vectorize(html, text)
            X[I, :] = x
            y[I, :] = [keys.index(cls)]
            print("x=%s" % x)
            I += 1

    print("X: %s" % X)
    print("y: %s" % y)

    data = Data(X=X, y=y)
    data.dump(args.output_file)

