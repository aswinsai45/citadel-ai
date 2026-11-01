import os
import math
import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

_index = []  # list of (source, chunk_text, vector)


def embed(text: str) -> list:
    r = requests.post(EMBED_URL, json={"model": EMBED_MODEL, "prompt": text})
    r.raise_for_status()
    return r.json()["embedding"]


def chunk(text: str) -> list:
    parts = [p.strip() for p in text.split("\n\n")]
    return [p for p in parts if p]


def build_index():
    _index.clear()
    for name in os.listdir(DATA_DIR):
        with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
            for piece in chunk(f.read()):
                _index.append((name, piece, embed(piece)))


def cosine(a: list, b: list) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb)


def search(query: str, k: int = 3) -> str:
    if not _index:
        build_index()
    qv = embed(query)
    ranked = sorted(_index, key=lambda row: cosine(qv, row[2]), reverse=True)
    top = ranked[:k]
    return "\n\n".join(f"[{src}]\n{text}" for src, text, _ in top)


if __name__ == "__main__":
    print(search("what lubricant does the pump need"))
