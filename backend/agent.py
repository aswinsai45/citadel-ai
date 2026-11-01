import asyncio
import hashlib
import json
import requests
import redis

cache = redis.Redis(host="localhost", port=6379, decode_responses=True)
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"

ARG_NAME = {"search": "query", "search_docs": "query", "read_file": "name"}

SYSTEM = """You are an agent that answers questions using internal documents.

Available tools:
- search(query): semantic search, returns the most relevant document chunks
- read_file(name): returns the full text of a document by filename

Reply with ONLY a JSON object, nothing else.
To use a tool: {"tool": "search", "input": "pump lubricant"}
To answer the user: {"answer": "your final answer"}

Always ground answers in the documents. Search first, then answer using the
chunks returned.

Example:
User: What oil does the pump use?
You: {"tool": "search", "input": "pump lubricant oil"}
User: Tool result: [pump_manual.txt] ...Use ISO VG 68 oil...
You: {"answer": "The pump uses ISO VG 68 oil."}
"""


def chat(messages: list) -> str:
    key = "llm:" + hashlib.sha256(json.dumps(messages).encode()).hexdigest()
    cached = cache.get(key)
    if cached is not None:
        print("[cache] hit")
        return cached

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
    reply = response.json()["message"]["content"]
    cache.set(key, reply)
    return reply


async def run(question: str) -> str:
    params = StdioServerParameters(command="python", args=["mcp_server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

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

                name = step["tool"]
                args = {ARG_NAME[name]: step["input"]}
                result = await session.call_tool(name, args)
                text = result.content[0].text
                print(f"[mcp] {name}({step['input']}) -> {text[:60]}...")

                messages.append({"role": "user", "content": f"Tool result: {text}"})

            return "Gave up after too many steps."


if __name__ == "__main__":
    print(asyncio.run(run("What oil does the pump use?")))
