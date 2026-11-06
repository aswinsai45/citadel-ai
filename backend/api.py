import os
import json
import time
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis

from agent import run

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ALLOWED_EXT = {".txt", ".md"}

db = redis.Redis(host="localhost", port=6379, decode_responses=True)
app = FastAPI(title="Citadel AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- health ----------
@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- documents ----------
@app.get("/documents")
def list_documents():
    files = sorted(f for f in os.listdir(DATA_DIR) if not f.startswith("."))
    return {"documents": files}


@app.get("/documents/{name}")
def get_document(name: str):
    path = os.path.join(DATA_DIR, os.path.basename(name))
    if not os.path.isfile(path):
        raise HTTPException(404, "Document not found")
    with open(path, encoding="utf-8") as f:
        return {"name": name, "content": f.read()}


@app.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    name = os.path.basename(file.filename)
    ext = os.path.splitext(name)[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(400, "Only .txt and .md files are supported")
    data = await file.read()
    with open(os.path.join(DATA_DIR, name), "wb") as f:
        f.write(data)
    return {"name": name}


@app.delete("/documents/{name}")
def delete_document(name: str):
    path = os.path.join(DATA_DIR, os.path.basename(name))
    if not os.path.isfile(path):
        raise HTTPException(404, "Document not found")
    os.remove(path)
    return {"ok": True}


# ---------- chats ----------
def _key(cid: str) -> str:
    return f"chat:{cid}"


@app.get("/chats")
def list_chats():
    ids = db.lrange("chat_ids", 0, -1)
    chats = []
    for cid in ids:
        raw = db.get(_key(cid))
        if raw:
            c = json.loads(raw)
            chats.append({"id": c["id"], "title": c["title"], "updated": c["updated"]})
    chats.sort(key=lambda c: c["updated"], reverse=True)
    return {"chats": chats}


@app.get("/chats/{cid}")
def get_chat(cid: str):
    raw = db.get(_key(cid))
    if not raw:
        raise HTTPException(404, "Chat not found")
    return json.loads(raw)


@app.delete("/chats/{cid}")
def delete_chat(cid: str):
    db.delete(_key(cid))
    db.lrem("chat_ids", 0, cid)
    return {"ok": True}


# ---------- ask ----------
class Query(BaseModel):
    question: str
    chat_id: str | None = None


@app.post("/ask")
async def ask(q: Query):
    answer = await run(q.question)

    cid = q.chat_id
    raw = db.get(_key(cid)) if cid else None
    chat = json.loads(raw) if raw else None

    if chat is None:
        cid = uuid.uuid4().hex[:12]
        chat = {"id": cid, "title": q.question[:48], "messages": [], "updated": 0}
        db.rpush("chat_ids", cid)

    chat["messages"].append({"role": "user", "text": q.question})
    chat["messages"].append({"role": "assistant", "text": answer})
    chat["updated"] = int(time.time())
    db.set(_key(cid), json.dumps(chat))

    return {"answer": answer, "chat_id": cid}
