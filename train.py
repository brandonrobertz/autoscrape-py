#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import argparse
import pickle

from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report
import numpy as np

from vectorize_data import Data


def parse_args():
    desc = "Convenience script for training autoscrape models."
    parser = argparse.ArgumentParser(
        description=desc
    )
    parser.add_argument(
        "--data", type=str, required=True,
        help="Input data pickle."
    )
    parser.add_argument(
        "--output", type=str, required=True,
        help="Fileame to output trained model to."
    )
    parser.add_argument(
        "--model", type=str, default="kNN",
        choices=["kNN", "SVC"],
        help="Which classifier to use (default: kNN)."
    )
    return parser.parse_args()


def load_data(filepath):
    print("Loading data...")
    with open(filepath, "rb") as f:
        return pickle.load(f)


if __name__ == "__main__":
    args = parse_args()

    MODEL = "k-NN"
    X = []
    y = []

    data = load_data(args.data)

    print("X shape", data.X.shape)
    for i in range(data.X.shape[0]):
        x = data.X[i]
        if np.any(np.isnan(x)):
            continue
        X.append(x)
        y.append(data.y[i][0])

    X = np.array(X)
    y = np.array(y)

    if args.model == "kNN":
        model = KNeighborsClassifier(1)
    elif args.model == "SVM":
        print("Fitting SVC model..")
        model = SVC()
    else:
        raise NotImplmentedError("Bad model selected: %s" % args.model)

    model.fit(X, y)

    print("Predicting on training data...")
    y_pred = model.predict(X)

    print("Complete!")
    print(classification_report(y, y_pred))

    print("Saving model...")
    with open(args.output, "wb") as f:
        pickle.dump(model, f)

    print("Done!")

