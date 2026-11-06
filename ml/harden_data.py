"""Harden the classification task.

Train questions use DIRECT phrasings (carry the category keyword).
Val questions use INDIRECT/colloquial phrasings (keyword-light) + noise.

So a bag-of-words model can't win by matching "oil"->lubrication; the val set
rewards a model that understands meaning, not surface words.

Outputs:
  datasets/classification_hard.train.jsonl   (direct)
  datasets/classification_hard.val.jsonl     (indirect + noise)
"""

import argparse
import json
import os
import random

from gen_data import EQUIPMENT, QUESTION_TEMPLATES, PREFIXES, cap

OUT = os.path.join(os.path.dirname(__file__), "datasets")

# Colloquial, keyword-light phrasings. {alias} = equipment. No {attr}: these are
# vague on purpose, so the category is carried by meaning, not a giveaway word.
INDIRECT = {
    "lubrication": [
        "what do i pour into {alias}?",
        "{alias} is running dry, what goes in it?",
        "which grade keeps {alias} running smooth?",
        "how long before {alias} needs a top-up?",
    ],
    "operating_limits": [
        "how hard can i push {alias}?",
        "what's the redline on {alias}?",
        "when does {alias} hit its ceiling?",
        "how far can i run {alias} before it's too much?",
    ],
    "startup_shutdown": [
        "how do i bring {alias} online?",
        "what's the drill to fire up {alias}?",
        "steps to bring {alias} down safely?",
        "how do i get {alias} going and stop it right?",
    ],
    "maintenance_schedule": [
        "how often does {alias} need a look?",
        "when's {alias} due again?",
        "what's the service cadence for {alias}?",
        "how frequently do we touch {alias}?",
    ],
    "safety": [
        "what keeps {alias} from blowing?",
        "what's the danger line on {alias}?",
        "how do i keep {alias} from becoming a hazard?",
        "what protects us if {alias} goes out of range?",
    ],
    "electrical": [
        "what does {alias} draw from the grid?",
        "how's {alias} wired up?",
        "power needs of {alias}?",
        "what trips if {alias} pulls too much?",
    ],
    "instrumentation": [
        "how do we watch {alias}?",
        "what reads {alias}?",
        "how is {alias} monitored and signalled?",
        "what tells us what {alias} is doing?",
    ],
    "environmental": [
        "how do we keep {alias} clean for the planet?",
        "what stops {alias} from polluting?",
        "discharge rules for {alias}?",
        "how do we stay within limits around {alias}?",
    ],
    "troubleshooting": [
        "why is {alias} acting up?",
        "{alias} is misbehaving, what gives?",
        "what makes {alias} go wrong?",
        "something's off with {alias}, what could it be?",
    ],
    "specifications": [
        "what's {alias} made of and how big?",
        "give me the build sheet for {alias}",
        "the nuts and bolts of {alias}?",
        "what are the raw numbers on {alias}?",
    ],
}

FILLERS = ["", "", "hey ", "ok so ", "quick one, ", "uh ", "sry, "]


def typo(s: str) -> str:
    # Drop one character occasionally to mimic real typing.
    if len(s) < 8 or random.random() > 0.3:
        return s
    i = random.randint(1, len(s) - 2)
    return s[:i] + s[i + 1:]


def noisy(text: str) -> str:
    text = random.choice(FILLERS) + text
    return typo(text)


# Hold out the last 2 indirect phrasings per category for val (unseen phrasings).
N_TRAIN_INDIRECT = 2


def build_train():
    rows = []
    for eq in EQUIPMENT:
        for category, facts in eq["facts"].items():
            # direct phrasings (carry the keyword)
            for attr, _ in facts:
                for alias in eq["aliases"]:
                    for tmpl in QUESTION_TEMPLATES[category]:
                        q = tmpl.format(alias=alias, attr=attr)
                        for pre in PREFIXES[:4]:
                            rows.append({"text": cap((pre + q).strip()), "label": category})
            # a couple of indirect phrasings so the model learns the colloquial style
            for alias in eq["aliases"]:
                for tmpl in INDIRECT[category][:N_TRAIN_INDIRECT]:
                    rows.append({"text": noisy(tmpl.format(alias=alias)), "label": category})
    return rows


def build_val():
    rows = []
    for eq in EQUIPMENT:
        for category in eq["facts"].keys():
            for alias in eq["aliases"]:
                for tmpl in INDIRECT[category][N_TRAIN_INDIRECT:]:
                    rows.append({"text": noisy(tmpl.format(alias=alias)), "label": category})
    return rows


def dedup(rows):
    seen, out = set(), []
    for r in rows:
        k = (r["text"], r["label"])
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out


def write(rows, name):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    random.seed(args.seed)

    train = dedup(build_train())
    val = dedup(build_val())
    random.shuffle(train)
    random.shuffle(val)

    write(train, "classification_hard.train.jsonl")
    write(val, "classification_hard.val.jsonl")
    print(f"hard train (direct):   {len(train)}")
    print(f"hard val (indirect):   {len(val)}")
    print("sample val:")
    for r in val[:6]:
        print(f"  [{r['label']:>18}]  {r['text']}")


if __name__ == "__main__":
    main()
