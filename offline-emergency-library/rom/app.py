"""Rom's HTTP API + chat UI.

Endpoints:
  GET  /            -> chat web UI (static/index.html)
  GET  /health      -> component status (ollama / qdrant / kiwix / index)
  POST /api/ask     -> {question} -> streamed cited answer
  GET  /api/search  -> ?q=...     -> raw retrieval results (debug)
"""
import json
import os

import httpx
from fastapi import FastAPI
from fastapi.responses import (FileResponse, JSONResponse, StreamingResponse)
from pydantic import BaseModel
from qdrant_client import QdrantClient

from common import (COLLECTION, KIWIX_URL, OLLAMA_URL, QDRANT_URL, ROM_MODEL,
                    TOP_K, embed)
from prompts import SYSTEM_PROMPT, build_user_prompt

app = FastAPI(title="Rom — Offline Emergency Library Assistant")
qdrant = QdrantClient(url=QDRANT_URL)
STATIC = os.path.join(os.path.dirname(__file__), "static")


class Ask(BaseModel):
    question: str


def retrieve(question: str, k: int = TOP_K) -> list[dict]:
    if not qdrant.collection_exists(COLLECTION):
        return []
    qvec = embed([question])[0]
    hits = qdrant.search(COLLECTION, query_vector=qvec, limit=k, with_payload=True)
    sources = []
    for i, h in enumerate(hits, 1):
        p = h.payload or {}
        url = p.get("url", "")
        # Split a zim "base.zim::/path" reference into book + path so the UI can
        # build a deep link to whichever host is serving Kiwix. Loose docs have
        # no live link (they're PDFs/text), so we just show the title.
        book, path = "", ""
        if "::/" in url:
            base, path = url.split("::/", 1)
            book = base[:-4] if base.endswith(".zim") else base
        sources.append({
            "n": i, "title": p.get("title", "source"),
            "text": p.get("text", ""),
            "book": book, "path": path, "source": p.get("source", ""),
            "collection": p.get("collection", "general"),
            "score": round(float(h.score), 3),
        })
    return sources


@app.get("/health")
def health():
    status = {}
    with httpx.Client(timeout=5) as c:
        for name, url in (("ollama", f"{OLLAMA_URL}/api/tags"),
                          ("qdrant", f"{QDRANT_URL}/readyz"),
                          ("kiwix", f"{KIWIX_URL}/")):
            try:
                c.get(url)
                status[name] = "ok"
            except Exception as e:
                status[name] = f"down: {e.__class__.__name__}"
    try:
        cnt = qdrant.count(COLLECTION).count if qdrant.collection_exists(COLLECTION) else 0
    except Exception:
        cnt = 0
    status["indexed_chunks"] = cnt
    status["model"] = ROM_MODEL
    return JSONResponse(status)


@app.get("/api/config")
def config():
    # Lets the browser build Kiwix deep links against whichever host it reached.
    return {"kiwix_port": int(os.environ.get("KIWIX_PORT_PUBLIC", "8090")),
            "model": ROM_MODEL}


@app.get("/api/search")
def search(q: str):
    return {"query": q, "results": retrieve(q)}


@app.post("/api/ask")
def ask(body: Ask):
    sources = retrieve(body.question)
    user_prompt = build_user_prompt(body.question, sources)

    def stream():
        # Send the sources first so the UI can render citations immediately.
        yield json.dumps({"type": "sources", "sources": [
            {"n": s["n"], "title": s["title"], "book": s["book"],
             "path": s["path"], "source": s["source"],
             "collection": s["collection"], "score": s["score"]}
            for s in sources]}) + "\n"
        with httpx.Client(timeout=None) as c:
            with c.stream("POST", f"{OLLAMA_URL}/api/chat", json={
                "model": ROM_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": True,
            }) as r:
                for line in r.iter_lines():
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    tok = obj.get("message", {}).get("content", "")
                    if tok:
                        yield json.dumps({"type": "token", "token": tok}) + "\n"
                    if obj.get("done"):
                        yield json.dumps({"type": "done"}) + "\n"

    return StreamingResponse(stream(), media_type="application/x-ndjson")


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC, "index.html"))
