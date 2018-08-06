import logging

import numpy as np


logger = logging.getLogger('AUTOSCRAPE')


class Vectorizer(object):
    def __init__(self, html_embeddings_file=None, word_embeddings_file=None):
        """
        Initialize our vectorizer with paths to the relevant word
        embedding files for our vectorization routines.
        """
        print("html_embeddings_file=%s, word_embeddings_file=%s" % (
            html_embeddings_file, word_embeddings_file
        ))
        self.html_embeddings = None
        if html_embeddings_file:
            self.html_embeddings = self.load_embedding(html_embeddings_file)

        self.word_embeddings = None
        if word_embeddings_file:
            self.word_embeddings = self.load_embedding(word_embeddings_file)

    def embeddings_length(self, path):
        N = 0
        with open(path, "r") as f:
            for line in f:
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
        embedding = np.zeros(shape=(N, dim))
        logger.debug("Reading embeddings into memory...")
        outputs = [ (N // 10) * i for i in range(10) ]
        with open(path, "r") as f:
            I = 0
            for line in f:
                if I in outputs:
                    logger.info("%0.4f%% complete" % ((I / float(N)) * 100))
                key, data = line.split(' ', 1)
                vec = [ float(d) for d in data.split() ]
                embedding[I, :] = vec
                I += 1
        logger.debug("Embeddings matrix: %s x %s" % embedding.shape)
        return embedding

