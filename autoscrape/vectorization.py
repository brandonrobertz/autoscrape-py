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
    def __init__(self, html_embeddings_file=None, word_embeddings_file=None):
        """
        Initialize our vectorizer with paths to the relevant word
        embedding files for our vectorization routines.
        """
        print("html_embeddings_file=%s, word_embeddings_file=%s" % (
            html_embeddings_file, word_embeddings_file
        ))
        self.html = None
        if html_embeddings_file:
            self.html = self.load_embedding(html_embeddings_file)

        self.word = None
        if word_embeddings_file:
            self.word = self.load_embedding(word_embeddings_file)

    def embeddings_length(self, path):
        N = 0
        with open(path, "r") as f:
            for line in f:
                if N == 0 and re.match("^[0-9]+\s[0-9]+$", line):
                    logger.debug("Skipping embedding meta first line")
                    continue
                N += 1
            key, data = line.split(' ', 1)
            logger.debug("key=%s data=%s" % ( key, data))
            vec = [ float(d) for d in data.split() ]
            dim = len(vec)
        return N, dim

    def load_embedding(self, path):
        logger.info("Loading embedding file %s..." % path)
        N, dim = self.embeddings_length(path)
        logger.info("vocab size: %s, dim: %s" % (
            N, dim
        ))
        logger.debug("Allocating embedding matrix...")
        # token to ID (embedding row)
        t2id = dict()
        # ID to token
        id2t = dict()
        # embedding matrix
        embeddings = np.zeros(shape=(N, dim))
        logger.debug("Reading embeddings into memory...")
        outputs = [ (N // 10) * i for i in range(10) ]
        with open(path, "r") as f:
            I = 0
            for line in f:
                if I == 0 and re.match("^[0-9]+\s[0-9]+$", line):
                    logger.debug("Skipping embedding meta first line")
                    continue
                if I in outputs:
                    logger.info("%0.4f%% complete" % ((I / float(N)) * 100))
                key, data = line.split(' ', 1)
                vec = [ float(d) for d in data.split() ]
                embeddings[I, :] = vec
                t2id[key] = I
                id2t[I] = key
                I += 1

        logger.debug("Embeddings matrix: %s x %s" % embeddings.shape)
        return Embedding(
            embeddings = embeddings,
            t2id = t2id,
            id2t = id2t,
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
            t = t.strip()
            if not t:
                continue
            logger.debug("Token=%s" % t)
            N += 1
            if re.match("\s", t):
                t = "</s>"
            try:
                id = self.word.t2id[t]
            except Exception as e:
                logger.warn("Skipping word=%s,  Error=%s" % (
                    t, e))
            x += self.word.embeddings[id]
        return x / N

    def element_to_position_vector(self, element):
        return np.array([0.0])

    def vectorize(self, html, text, element):
        x_html = self.html_to_vector(html)
        x_text = self.text_to_vector(text)
        x_pos  = self.element_to_position_vector(element)
        # import IPython; IPython.embed()
        x = np.concatenate([x_html, x_text, x_pos])
        return x

