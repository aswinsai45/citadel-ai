# Citadel ML

Training work for the agent. All local; training runs on Apple MPS (or CPU).

## Setup

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Track B — query classifier (done)

Goal: classify an operator's question into one of 10 maintenance/ops categories, so
the agent can route it. Built two models and compared them honestly.

### Pipeline

```bash
python gen_data.py        # structured facts -> ~4k templated examples (QA + classification)
python harden_data.py     # harder task: train on direct phrasings + a few colloquial;
                          # test on UNSEEN colloquial phrasings + typos (no keyword leakage)
python train_baseline.py --data classification_hard    # TF-IDF + Logistic Regression
python train_classifier.py                             # fine-tune DistilBERT (keeps best epoch)
python evaluate.py                                     # side-by-side comparison
```

### Result (hard val: 210 unseen-phrasing questions)

| model | accuracy | f1_macro |
|---|---|---|
| TF-IDF + LogReg (baseline) | 0.414 | 0.401 |
| DistilBERT (fine-tuned) | 0.548 | 0.429 |

**+13 accuracy points** for the transformer: it generalizes to colloquial phrasings a
bag-of-words model has never seen.

### What this taught (the honest lessons)

1. **Perfect score = red flag.** On the first (easy) dataset the baseline hit 100% —
   the templates leaked the label through keywords. Real signal needs a harder test.
2. **Data leakage.** Near-duplicate question variants must stay on the same side of the
   train/val split (group-aware split in `gen_data.py`), or the model just memorizes.
3. **Domain shift can be too harsh.** Training only on direct phrasings and testing only
   on colloquial ones gave the transformer 47% (worse than baseline) — it never saw the
   target style. Mixing a little colloquial into training fixed it.
4. **Overfitting.** Train loss → ~0 while val stalls; DistilBERT peaked at epoch 1 then
   decayed. We keep the best checkpoint (`load_best_model_at_end`).
5. **Small val = noisy.** 210 examples, so treat the delta as directional, not exact.

## Track A — fine-tune the LLM (next)

QLoRA on the `qa.*.jsonl` instruction data, on a free GPU (Colab/Kaggle), then run the
adapter locally in Ollama.
