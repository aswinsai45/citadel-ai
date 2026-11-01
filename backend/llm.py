"""to local ollama from py"""

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"


def ask(prompt: str) -> str:
    """prompt to the model and return its reply."""
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False},
    )
    response.raise_for_status()
    return response.json()["response"]


if __name__ == "__main__":
    reply = ask("Say hello in one short line.")
    print(reply)
