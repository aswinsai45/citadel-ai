"""Baseline query classifier: TF-IDF + Logistic Regression.

Classic ML reference point for the DistilBERT fine-tune. Trains in seconds on CPU.
"""

import argparse
import json
import os

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.pipeline import Pipeline

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "datasets")
MODELS = os.path.join(HERE, "models")


def load(base, split):
    rows = [json.loads(l) for l in open(os.path.join(DATA, f"{base}.{split}.jsonl"))]
    return [r["text"] for r in rows], [r["label"] for r in rows]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="classification", help="dataset base name")
    args = ap.parse_args()

    Xtr, ytr = load(args.data, "train")
    Xva, yva = load(args.data, "val")
    labels = json.load(open(os.path.join(DATA, "labels.json")))

    clf = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
        ("lr", LogisticRegression(max_iter=1000, C=4.0)),
    ])
    clf.fit(Xtr, ytr)

    pred = clf.predict(Xva)
    acc = accuracy_score(yva, pred)

    print(f"\nval accuracy: {acc:.4f}  (n={len(yva)})\n")
    print(classification_report(yva, pred, labels=labels, zero_division=0))
    print("confusion matrix (rows=true, cols=pred):")
    print("labels:", labels)
    print(confusion_matrix(yva, pred, labels=labels))

    os.makedirs(MODELS, exist_ok=True)
    out = os.path.join(MODELS, "baseline.joblib")
    joblib.dump(clf, out)
    print(f"\nsaved -> {out}")


if __name__ == "__main__":
    main()
