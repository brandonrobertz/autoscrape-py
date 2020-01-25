# -*- coding: UTF-8 -*-
import logging
import re

import numpy as np


logger = logging.getLogger('AUTOSCRAPE')


class Embedding(object):
    def __init__(self, embeddings=None, t2id=None, id2t=None):
        self.embeddings = embeddings
        self.t2id = t2id
        self.id2t = id2t
        self.N, self.dim = embeddings.shape


class Vectorizer(object):
    def __init__(self, html_embeddings_file=None, word_embeddings_file=None,
                 loglevel=None):
        """
        Initialize our vectorizer with paths to the relevant word
        embedding files for our vectorization routines.
        """
        self.html = None
        if html_embeddings_file:
            logger.debug("[.] Loading HTML embeddings")
            self.html = self.load_embedding(html_embeddings_file)

        self.word = None
        if word_embeddings_file:
            logger.debug("[.] Loading word embeddings")
            self.word = self.load_embedding(word_embeddings_file)

    def setup_logging(self, loglevel=None):
        level = logging.INFO
        if loglevel == "DEBUG":
            level = logging.DEBUG
        elif loglevel == "INFO":
            level = logging.INFO
        elif loglevel == "WARN":
            level = logging.WARN
        elif loglevel == "ERROR":
            level = logging.ERROR

        logger.setLevel(level)
        console_handler = logging.StreamHandler()
        logger.addHandler(console_handler)

    def embeddings_length(self, path):
        N = 0
        with open(path, "r") as f:
            for line in f:
                if N == 0 and re.match("^[0-9]+\s[0-9]+$", line):
                    continue
                N += 1
            key, data = line.split(' ', 1)
            vec = [float(d) for d in data.split()]
            dim = len(vec)
        return N, dim

    def load_embedding(self, path):
        logger.info("[+] Loading embedding file %s..." % path)
        N, dim = self.embeddings_length(path)
        logger.info(" - vocab size: %s, dim: %s" % (
            N, dim
        ))
        logger.debug(" - Allocating embedding matrix...")
        # token to ID (embedding row)
        t2id = dict()
        # ID to token
        id2t = dict()
        # embedding matrix
        embeddings = np.zeros(shape=(N, dim))
        logger.debug(" - Reading embeddings into memory...")
        outputs = [(N // 10) * i for i in range(10)]
        with open(path, "r") as f:
            embed_id = 0
            for line in f:
                if embed_id == 0 and re.match("^[0-9]+\s[0-9]+$", line):
                    continue
                if embed_id in outputs:
                    pct_done = (embed_id / float(N)) * 100
                    logger.info(" - %0.4f%% complete" % (pct_done))
                key, data = line.split(' ', 1)
                vec = [float(d) for d in data.split()]
                embeddings[embed_id, :] = vec
                t2id[key] = embed_id
                id2t[embed_id] = key
                embed_id += 1

        logger.debug(" - Embeddings matrix: %s x %s" % embeddings.shape)
        return Embedding(
            embeddings=embeddings,
            t2id=t2id,
            id2t=id2t,
        )

    def html_to_vector(self, html):
        x = np.zeros(self.html.dim)
        N = 0.0
        for t in html:
            N += 1
            if re.match("\s", t):
                t = "</s>"
            id = self.html.t2id[t]
            x += self.html.embeddings[id]
        return x / N

    def text_to_vector(self, text):
        x = np.zeros(self.word.dim)
        N = 0.0
        for t in re.split("[^A-Za-z]", text):
            t = t.strip().lower()
            if not t:
                continue
            N += 1
            if re.match("\s", t):
                t = "</s>"
            try:
                id = self.word.t2id[t]
            except Exception as e:
                logger.warn("Skipping word=%s,  Error=%s" % (
                    t, e
                ))
                continue
            x += self.word.embeddings[id]
        return x / N

    def element_to_position_vector(self, element):
        return np.array([0.0])

    def vectorize(self, html, text, element=None):
        x_html = self.html_to_vector(html)
        x_text = self.text_to_vector(text)
        concat_array = [x_html, x_text]
        if element:
            x_pos = self.element_to_position_vector(element)
            concat_array.append(x_pos)
        x = np.concatenate(concat_array)
        return x
