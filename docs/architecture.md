# Citadel-AI — Architecture (living document)

A private, fully self-hosted ("sovereign / on-premise") agentic AI workbench.
Everything runs locally in Docker. Nothing leaves the machine.

## The services (containers)

| Service   | Role (plain words)                     | Tech (planned)          | Status      |
|-----------|----------------------------------------|-------------------------|-------------|
| redis     | Fast notepad: cache + agent memory     | Redis 7                 | ✅ added     |
| backend   | The receptionist + manager (agent/API) | FastAPI + Python        | ✅ added     |
| llm       | The brain (runs the model locally)     | Ollama (llama3.2:3b)    | ✅ added     |
| vectordb  | Librarian: finds relevant doc chunks   | in-memory + Ollama embed| ✅ (basic)   |
| frontend  | The chat webpage you type into         | React + JS + Tailwind   | ✅ added     |

## Build order
1. ✅ docker-compose with Redis (prove the "building" stands)
2. ✅ Local LLM (Ollama) talking to a plain Python script
3. ✅ Hand-written agent loop (plan -> act -> observe)
4. ✅ Tools exposed via a real MCP server
5. ✅ Redis used for caching + memory (LLM replies + embeddings)
6. ✅ RAG: ingest docs -> embed -> vector search (semantic search tool)
7. ⬜ Multimodal (images / scanned PDFs)
8. ✅ FastAPI backend + React/Tailwind frontend (control-room UI, persisted chats, docs panel)
9. ⬜ Full docker-compose up (containerize backend + frontend alongside redis/ollama)
10. 🔄 Fine-tune models:
    - ✅ Track B: query classifier — TF-IDF baseline vs fine-tuned DistilBERT (+13 acc pts). See `ml/`.
    - ⬜ Track A: QLoRA fine-tune the LLM on `ml/datasets/qa.*.jsonl` (free Colab GPU), run adapter in Ollama.

## Where we are (~65% of the planned build)

**Done:** full local agentic RAG stack end-to-end — Docker (Redis+Ollama), hand-written
agent loop, MCP server/client, Redis caching, RAG semantic search, FastAPI API, polished
React frontend with persisted chats + document upload/view, and Track-B model training
(classifier baseline vs transformer, hardened eval, honest writeup).

**Remaining (next sessions):**
- **Track A — QLoRA LLM fine-tune** (the headline ML skill): train on the synthetic QA
  data on a free GPU, merge to GGUF, load into Ollama locally.
- **Wire the DistilBERT classifier into the agent** as a real query router (so the trained
  model earns its place in the product).
- **Multimodal** (step 7): read images / scanned equipment PDFs.
- **Full containerization** (step 9): Dockerfiles for backend + frontend, one
  `docker compose up` brings the whole workbench online.
- **Persist the vector index** (currently rebuilt per request; move embeddings into a real
  store or cache the index) and **evaluate RAG quality**.
- **Polish for demo/judging:** README with architecture diagram, screenshots, a seeded
  corpus of realistic industrial docs, and a short demo script.

## Immediate next step (tomorrow)

Track A: open `ml/` on a free Colab/Kaggle GPU, QLoRA fine-tune `llama3.2` (or a small
base) on `qa.train.jsonl`, evaluate on `qa.val.jsonl`, export adapter, run in Ollama.
