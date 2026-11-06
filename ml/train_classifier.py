"""Fine-tune DistilBERT as the query classifier.

Same hard data as the baseline. A pretrained transformer understands phrasing it
never saw in training, so it should beat the bag-of-words baseline on the indirect
val set. Runs on Apple MPS when available.
"""

import argparse
import json
import os

import numpy as np
import torch
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "datasets")
MODELS = os.path.join(HERE, "models")
CKPT = "distilbert-base-uncased"


def load(base, split, label2id):
    rows = [json.loads(l) for l in open(os.path.join(DATA, f"{base}.{split}.jsonl"))]
    return Dataset.from_dict({
        "text": [r["text"] for r in rows],
        "label": [label2id[r["label"]] for r in rows],
    })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="classification_hard")
    ap.add_argument("--epochs", type=float, default=3)
    ap.add_argument("--batch", type=int, default=16)
    args = ap.parse_args()

    labels = json.load(open(os.path.join(DATA, "labels.json")))
    label2id = {l: i for i, l in enumerate(labels)}
    id2label = {i: l for l, i in label2id.items()}

    tok = AutoTokenizer.from_pretrained(CKPT)

    def tokenize(batch):
        return tok(batch["text"], truncation=True, max_length=64)

    train = load(args.data, "train", label2id).map(tokenize, batched=True)
    val = load(args.data, "val", label2id).map(tokenize, batched=True)

    model = AutoModelForSequenceClassification.from_pretrained(
        CKPT, num_labels=len(labels), id2label=id2label, label2id=label2id
    )

    def metrics(eval_pred):
        logits, y = eval_pred
        pred = np.argmax(logits, axis=-1)
        return {
            "accuracy": accuracy_score(y, pred),
            "f1_macro": f1_score(y, pred, average="macro"),
        }

    out = os.path.join(MODELS, "distilbert")
    targs = TrainingArguments(
        output_dir=os.path.join(out, "_trainer"),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch,
        per_device_eval_batch_size=32,
        learning_rate=3e-5,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        save_total_limit=1,
        logging_strategy="epoch",
        disable_tqdm=True,
        report_to=[],
        use_mps_device=torch.backends.mps.is_available(),
    )

    trainer = Trainer(
        model=model,
        args=targs,
        train_dataset=train,
        eval_dataset=val,
        tokenizer=tok,
        compute_metrics=metrics,
    )

    trainer.train()
    final = trainer.evaluate()
    print("\nfinal val:", {k: round(v, 4) for k, v in final.items() if k.startswith("eval_")})

    model.save_pretrained(out)
    tok.save_pretrained(out)
    print(f"saved -> {out}")


if __name__ == "__main__":
    main()
