"""Compare the baseline and the fine-tuned transformer on the hard val set."""

import json
import os

import joblib
import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "datasets")
MODELS = os.path.join(HERE, "models")


def load_val(base="classification_hard"):
    rows = [json.loads(l) for l in open(os.path.join(DATA, f"{base}.val.jsonl"))]
    return [r["text"] for r in rows], [r["label"] for r in rows]


def eval_baseline(X, y):
    clf = joblib.load(os.path.join(MODELS, "baseline.joblib"))
    pred = clf.predict(X)
    return accuracy_score(y, pred), f1_score(y, pred, average="macro")


def eval_distilbert(X, y):
    path = os.path.join(MODELS, "distilbert")
    tok = AutoTokenizer.from_pretrained(path)
    model = AutoModelForSequenceClassification.from_pretrained(path).eval()
    id2label = model.config.id2label
    preds = []
    with torch.no_grad():
        for i in range(0, len(X), 32):
            enc = tok(X[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=64)
            logits = model(**enc).logits
            preds += [id2label[int(j)] for j in logits.argmax(-1)]
    return accuracy_score(y, preds), f1_score(y, preds, average="macro")


def main():
    X, y = load_val()
    ba, bf = eval_baseline(X, y)
    da, df = eval_distilbert(X, y)
    print(f"\nhard val set: {len(y)} unseen-phrasing questions\n")
    print(f"{'model':<28}{'accuracy':>10}{'f1_macro':>10}")
    print("-" * 48)
    print(f"{'TF-IDF + LogReg (baseline)':<28}{ba:>10.3f}{bf:>10.3f}")
    print(f"{'DistilBERT (fine-tuned)':<28}{da:>10.3f}{df:>10.3f}")
    print(f"\ndelta: +{(da - ba) * 100:.1f} accuracy points for the transformer")


if __name__ == "__main__":
    main()
