# Citadel-AI — Architecture (living document)

A private, fully self-hosted ("sovereign / on-premise") agentic AI workbench.
Everything runs locally in Docker. Nothing leaves the machine.

## The services (containers)

| Service   | Role (plain words)                     | Tech (planned)          | Status      |
|-----------|----------------------------------------|-------------------------|-------------|
| redis     | Fast notepad: cache + agent memory     | Redis 7                 | ✅ added     |
| backend   | The receptionist + manager (agent/API) | FastAPI + Python        | ⬜ later     |
| llm       | The brain (runs the model locally)     | Ollama                  | ⬜ later     |
| vectordb  | Librarian: finds relevant doc chunks   | Postgres+pgvector/Chroma| ⬜ later     |
| frontend  | The chat webpage you type into         | React + JS + Tailwind   | ⬜ later     |

## Build order
1. ✅ docker-compose with Redis (prove the "building" stands)
2. ⬜ Local LLM (Ollama) talking to a plain Python script
3. ⬜ Hand-written agent loop (plan -> act -> observe)
4. ⬜ Tools exposed via a real MCP server
5. ⬜ Redis used for caching + memory
6. ⬜ RAG: ingest docs -> embed -> vector search
7. ⬜ Multimodal (images / scanned PDFs)
8. ⬜ FastAPI backend + React/Tailwind frontend
9. ⬜ Full docker-compose up
10. ⬜ Fine-tune a small model (LoRA/QLoRA on free Colab GPU)
