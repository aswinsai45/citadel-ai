"""Synthetic industrial Q&A + classification data generator.

One structured fact base -> two datasets:
  datasets/classification.{train,val}.jsonl   {"text", "label"}
  datasets/qa.{train,val}.jsonl               {"instruction", "input", "output"}

Template + vocabulary expansion. No LLM, deterministic with --seed.
"""

import argparse
import json
import os
import random

OUT = os.path.join(os.path.dirname(__file__), "datasets")

# Equipment units. Each fact is tagged with the category it belongs to.
EQUIPMENT = [
    {
        "name": "centrifugal pump CP-200",
        "aliases": ["the pump", "the CP-200", "the centrifugal pump", "pump CP-200"],
        "facts": {
            "lubrication": [
                ("bearing oil grade", "ISO VG 68 mineral oil"),
                ("oil change interval", "every 4000 operating hours or 6 months"),
                ("oil level requirement", "between the MIN and MAX marks on the sight glass"),
            ],
            "operating_limits": [
                ("maximum discharge pressure", "16 bar"),
                ("maximum fluid temperature", "120 C"),
                ("rated flow", "200 m3/h at 2950 rpm"),
            ],
            "startup_shutdown": [
                ("pre-start check", "confirm suction valve is open and casing is primed"),
                ("shutdown step", "close the discharge valve before stopping the motor"),
            ],
            "maintenance_schedule": [
                ("bearing inspection", "every 2000 operating hours"),
                ("mechanical seal replacement", "every 8000 operating hours"),
            ],
            "troubleshooting": [
                ("cause of cavitation", "insufficient suction pressure or a blocked strainer"),
                ("cause of excessive vibration", "misalignment or a worn bearing"),
            ],
            "specifications": [
                ("impeller diameter", "220 mm"),
                ("casing material", "cast steel ASTM A216 WCB"),
            ],
        },
    },
    {
        "name": "screw air compressor AC-110",
        "aliases": ["the compressor", "the AC-110", "the air compressor", "compressor AC-110"],
        "facts": {
            "lubrication": [
                ("compressor oil type", "synthetic PAO 46 compressor oil"),
                ("oil separator change", "every 6000 operating hours"),
            ],
            "operating_limits": [
                ("maximum working pressure", "10 bar"),
                ("maximum discharge air temperature", "105 C"),
                ("rated capacity", "18 m3/min"),
            ],
            "startup_shutdown": [
                ("start condition", "oil temperature must be above 10 C before loading"),
                ("shutdown step", "allow a 3-minute unloaded run before full stop"),
            ],
            "maintenance_schedule": [
                ("air filter replacement", "every 2000 operating hours"),
                ("oil filter replacement", "every 4000 operating hours"),
            ],
            "electrical": [
                ("motor rating", "90 kW, 415 V, 3-phase"),
                ("overload setting", "165 A"),
            ],
            "troubleshooting": [
                ("cause of high discharge temperature", "low oil level or a clogged oil cooler"),
                ("cause of frequent load/unload cycling", "an undersized air receiver or a system leak"),
            ],
        },
    },
    {
        "name": "shell-and-tube heat exchanger HX-305",
        "aliases": ["the heat exchanger", "the HX-305", "the exchanger", "unit HX-305"],
        "facts": {
            "operating_limits": [
                ("maximum design pressure", "25 bar on the tube side"),
                ("maximum design temperature", "250 C"),
            ],
            "maintenance_schedule": [
                ("tube bundle cleaning", "every 12 months or when pressure drop exceeds 0.5 bar"),
                ("gasket replacement", "at every bundle removal"),
            ],
            "troubleshooting": [
                ("cause of reduced heat transfer", "fouling or scaling on the tube surfaces"),
                ("cause of rising pressure drop", "tube-side fouling or partial blockage"),
            ],
            "specifications": [
                ("number of tubes", "420 tubes"),
                ("tube material", "stainless steel SS316L"),
            ],
            "environmental": [
                ("cooling water discharge limit", "below 40 C to meet effluent norms"),
            ],
        },
    },
    {
        "name": "pressure relief valve PRV-77",
        "aliases": ["the relief valve", "the PRV-77", "the safety valve", "valve PRV-77"],
        "facts": {
            "safety": [
                ("set pressure", "18 bar"),
                ("test interval", "every 12 months on a certified test bench"),
                ("action if leaking below set pressure", "isolate and replace the valve immediately"),
            ],
            "specifications": [
                ("orifice designation", "API 526 orifice 'J'"),
                ("body material", "forged carbon steel A105"),
            ],
            "maintenance_schedule": [
                ("overhaul interval", "every 24 months"),
            ],
        },
    },
    {
        "name": "storage tank TK-900",
        "aliases": ["the tank", "the TK-900", "the storage tank", "tank TK-900"],
        "facts": {
            "safety": [
                ("maximum fill level", "90 percent of nominal capacity"),
                ("nitrogen blanket pressure", "maintained at 5 mbar to prevent ignition"),
            ],
            "environmental": [
                ("secondary containment", "a bund wall sized for 110 percent of tank volume"),
                ("vapour control", "connected to the vapour recovery unit"),
            ],
            "instrumentation": [
                ("level measurement", "a guided-wave radar transmitter"),
                ("high-level alarm", "trips at 95 percent to close the inlet valve"),
            ],
            "specifications": [
                ("nominal capacity", "500 m3"),
                ("shell material", "carbon steel A36"),
            ],
        },
    },
    {
        "name": "control valve CV-42",
        "aliases": ["the control valve", "the CV-42", "valve CV-42"],
        "facts": {
            "instrumentation": [
                ("signal type", "4-20 mA with HART"),
                ("fail position", "fail-closed on loss of air"),
                ("actuator air supply", "a clean, dry instrument air supply at 1.4 bar"),
            ],
            "maintenance_schedule": [
                ("positioner calibration", "every 12 months"),
                ("packing inspection", "every 6 months"),
            ],
            "troubleshooting": [
                ("cause of valve hunting", "an over-tuned loop or worn packing"),
                ("cause of sticking", "contaminated instrument air or galling of the stem"),
            ],
        },
    },
]

# Question phrasings per category (slot {alias} = equipment, {attr} = fact name).
QUESTION_TEMPLATES = {
    "lubrication": [
        "What is the {attr} for {alias}?",
        "Which lubricant does {alias} use?",
        "Tell me the {attr} of {alias}.",
        "How often should the oil in {alias} be changed?",
        "What oil spec applies to {alias}?",
    ],
    "operating_limits": [
        "What is the {attr} of {alias}?",
        "What are the operating limits of {alias}?",
        "How high can {alias} run before it exceeds its {attr}?",
        "State the {attr} for {alias}.",
    ],
    "startup_shutdown": [
        "What is the {attr} for {alias}?",
        "How do I safely start {alias}?",
        "What is the correct shutdown procedure for {alias}?",
        "List the {attr} of {alias}.",
    ],
    "maintenance_schedule": [
        "What is the {attr} for {alias}?",
        "How often is {attr} required for {alias}?",
        "When should {alias} get its {attr}?",
        "Give the maintenance interval for {alias}.",
    ],
    "safety": [
        "What is the {attr} of {alias}?",
        "What safety limit governs {alias}?",
        "What should I do about {attr} on {alias}?",
        "State the {attr} for {alias}.",
    ],
    "electrical": [
        "What is the {attr} of {alias}?",
        "What is the electrical rating of {alias}?",
        "Tell me the {attr} for {alias}.",
    ],
    "instrumentation": [
        "What is the {attr} for {alias}?",
        "How is {alias} instrumented?",
        "What is the {attr} of {alias}?",
        "Describe the control signal for {alias}.",
    ],
    "environmental": [
        "What is the {attr} for {alias}?",
        "What environmental control applies to {alias}?",
        "State the {attr} of {alias}.",
    ],
    "troubleshooting": [
        "What is the {attr} on {alias}?",
        "Why is {alias} having trouble?",
        "What could cause {attr} on {alias}?",
        "Diagnose the {attr} for {alias}.",
    ],
    "specifications": [
        "What is the {attr} of {alias}?",
        "Give the {attr} for {alias}.",
        "What are the specs of {alias}?",
    ],
}

PREFIXES = ["", "", "", "Quick question: ", "Can you tell me, ", "I need to know, ", "Please confirm: "]

ANSWER_TEMPLATES = [
    "The {attr} for {name} is {value}.",
    "For {name}, the {attr} is {value}.",
    "{value} — that is the {attr} of {name}.",
]


def cap(s: str) -> str:
    return s[0].upper() + s[1:] if s else s


def build():
    cls, qa = [], []
    for eq in EQUIPMENT:
        name = eq["name"]
        for category, facts in eq["facts"].items():
            for attr, value in facts:
                for alias in eq["aliases"]:
                    for tmpl in QUESTION_TEMPLATES[category]:
                        q = tmpl.format(alias=alias, attr=attr)
                        for pre in PREFIXES:
                            text = cap((pre + q).strip())
                            cls.append({"text": text, "label": category, "_group": q})
                        ans = random.choice(ANSWER_TEMPLATES).format(
                            attr=attr, name=name, value=value
                        )
                        qa.append({"instruction": cap(q), "input": "", "output": cap(ans)})
    return cls, qa


def dedup(rows, key):
    seen, out = set(), []
    for r in rows:
        k = key(r)
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out


def split_write(rows, base, val_frac, group_key=None):
    # Group-aware split: all rows sharing a group go to the same side (no leakage).
    if group_key:
        groups = {}
        for r in rows:
            groups.setdefault(group_key(r), []).append(r)
        keys = list(groups)
        random.shuffle(keys)
        n_val = max(1, int(len(keys) * val_frac))
        val_keys = set(keys[:n_val])
        val = [r for k in val_keys for r in groups[k]]
        train = [r for k in keys[n_val:] for r in groups[k]]
    else:
        random.shuffle(rows)
        n_val = max(1, int(len(rows) * val_frac))
        val, train = rows[:n_val], rows[n_val:]

    random.shuffle(train)
    random.shuffle(val)
    for part, data in (("train", train), ("val", val)):
        path = os.path.join(OUT, f"{base}.{part}.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            for r in data:
                r = {k: v for k, v in r.items() if not k.startswith("_")}
                f.write(json.dumps(r) + "\n")
    return len(train), len(val)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--val-frac", type=float, default=0.1)
    args = ap.parse_args()

    random.seed(args.seed)
    os.makedirs(OUT, exist_ok=True)

    cls, qa = build()
    cls = dedup(cls, lambda r: (r["text"], r["label"]))
    qa = dedup(qa, lambda r: r["instruction"])

    ct, cv = split_write(cls, "classification", args.val_frac, group_key=lambda r: r["_group"])
    qt, qv = split_write(qa, "qa", args.val_frac)

    labels = sorted({r["label"] for r in cls})
    with open(os.path.join(OUT, "labels.json"), "w") as f:
        json.dump(labels, f, indent=2)

    print(f"classification: {ct} train / {cv} val  ({len(labels)} labels)")
    print(f"qa:             {qt} train / {qv} val")
    print(f"labels: {labels}")


if __name__ == "__main__":
    main()
