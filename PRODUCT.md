# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary: engineers, maintenance staff, and safety operators inside a confidential
industrial setting (e.g. a refinery, per SIH26117 / MRPL) who need answers grounded
in internal, sensitive documents without that data ever leaving the premises.

Secondary (inferred): SIH judges, recruiters, and reviewers evaluating the project as
a portfolio artifact. The UI must read as a serious operational tool first, and be
demo-credible second.

## Product Purpose

Citadel AI is a sovereign, fully on-premise agentic AI workbench. It lets a user ask
natural-language questions and get answers grounded in their own confidential
documents, using open-weight local models. Nothing is sent to any external API —
model, retrieval, cache, and storage all run locally. Success = trustworthy,
document-grounded answers with zero data exfiltration.

## Positioning

Air-gapped by construction: the agent loop, LLM (Ollama), RAG embeddings, Redis cache,
and chat history all run on the user's own machine via Docker. The differentiator is
sovereignty/confidentiality, not raw model quality — it is the tool you can hand your
secret papers to.

## Capabilities

- Conversational agent grounded in local documents (RAG over a local corpus).
- Persisted chat history (Redis), reopenable from a sidebar.
- Document management: list, view, upload (.txt/.md), delete; uploads become searchable.
- Tools exposed via a local MCP server; agent is an MCP client.
- Redis caching of LLM responses and embeddings.

## Constraints

- Fully local / air-gapped: no external network calls at runtime.
- Runs on CPU on a developer laptop; the local 3B model is slow for broad questions —
  the UI must set expectations and stay responsive under multi-second latency.
- Stack is fixed by existing code (see Stack).

## Stack

Frontend: React 19 + Vite 8 (SWC) + Tailwind CSS v4.
Backend: FastAPI (Python), MCP server, Ollama (llama3.2:3b + nomic-embed-text), Redis.

## Terminology

- "Citadel" = the private, walled-off local environment.
- "Documents" = the confidential corpus the agent answers from.
- "Workbench" = the main operating surface (chat + docs).

<!-- Inferred fields (secondary audience, constraints) are labeled; all else confirmed from the build history. -->
