import asyncio
import json
import requests
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"

ARG_NAME = {"search_docs": "query", "read_file": "name"}

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
