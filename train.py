#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import pickle

from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report
import numpy as np

from vectorize_data import Data


MODEL = "k-NN"
X = []
y = []


print("Loading data...")
data = None
with open("./training_data/page_data.pickle", "rb") as f:
    data = pickle.load(f)

print("X shape", data.X.shape)
for i in range(data.X.shape[0]):
    x = data.X[i]
    if np.any(np.isnan(x)):
        continue
    X.append(x)
    y.append(data.y[i][0])

X = np.array(X)
y = np.array(y)

if MODEL == "SVM":
    print("Fitting SVC model..")
    model = SVC()
elif MODEL == "k-NN":
    model = KNeighborsClassifier(1)

model.fit(X, y)

print("Predicting on training data...")
y_pred = model.predict(X)

print("Complete!")
print(classification_report(y, y_pred))

