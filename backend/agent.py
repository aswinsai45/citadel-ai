import json
import os
import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"


def search_docs(query: str) -> str:
    words = query.lower().split()
    scored = []
    for name in os.listdir(DATA_DIR):
        path = os.path.join(DATA_DIR, name)
        with open(path, encoding="utf-8") as f:
            text = f.read().lower()
        score = sum(1 for w in words if w in text)
        if score:
            scored.append((score, name))
    scored.sort(reverse=True)
    return ", ".join(name for _, name in scored) if scored else "No matching documents."


def read_file(name: str) -> str:
    path = os.path.join(DATA_DIR, name)
    with open(path, encoding="utf-8") as f:
        return f.read()


TOOLS = {"search_docs": search_docs, "read_file": read_file}

SYSTEM = """You are an agent that answers questions using internal documents.

Available tools:
- search_docs(query): returns filenames that contain the query text
- read_file(name): returns the full text of a document by filename

Reply with ONLY a JSON object, nothing else.
To use a tool: {"tool": "search_docs", "input": "pump maintenance"}
To answer the user: {"answer": "your final answer"}

Always ground answers in the documents. First search, then read the relevant
file, then answer using what you read.

Example:
User: What oil does the pump use?
You: {"tool": "search_docs", "input": "pump oil"}
User: Tool result: pump_manual.txt
You: {"tool": "read_file", "input": "pump_manual.txt"}
User: Tool result: ...Use ISO VG 68 oil...
You: {"answer": "The pump uses ISO VG 68 oil."}
"""


def chat(messages: list) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0},
        },
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def run(question: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]

    for _ in range(8):
        reply = chat(messages)
        messages.append({"role": "assistant", "content": reply})

        step = json.loads(reply)

        if "answer" in step:
            return step["answer"]

        tool = TOOLS[step["tool"]]
        result = tool(step["input"])
        print(f"[tool] {step['tool']}({step['input']}) = {result}")

        messages.append({"role": "user", "content": f"Tool result: {result}"})

    return "Gave up after too many steps."


if __name__ == "__main__":
    print(run("What oil does the pump use?"))
