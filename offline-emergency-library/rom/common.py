"""Shared helpers for Rom: config, embeddings (via Ollama), Qdrant access,
text chunking, and content classification (clinical vs. holistic, etc.)."""
import os
import re
import httpx

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
KIWIX_URL = os.environ.get("KIWIX_URL", "http://kiwix:8090")
ROM_MODEL = os.environ.get("ROM_MODEL", "llama3.1:8b")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
TOP_K = int(os.environ.get("TOP_K", "6"))

COLLECTION = "rom_library"

# Keyword hints used to tag a chunk's "collection" so Rom can distinguish
# evidence-based medicine from traditional/holistic practice, etc.
_HOLISTIC_HINTS = re.compile(
    r"\b(herbal|herb|holistic|folk|traditional medicine|naturopath|"
    r"homeopath|tincture|poultice|remedy|ayurved|essential oil)\b", re.I)
_CLINICAL_HINTS = re.compile(
    r"\b(clinical|diagnosis|dosage|milligram|contraindicat|WHO|CDC|"
    r"randomized|systematic review|first aid|CPR|trauma|antibiotic)\b", re.I)


def classify_collection(path: str, text: str) -> str:
    """Best-effort content category, used for safety labelling in answers."""
    p = path.lower()
    if "holistic" in p or "herbal" in p or "traditional" in p:
        return "holistic"
    if any(k in p for k in ("medical", "medicine", "wikimed", "doctor", "first-aid", "health")):
        return "clinical"
    sample = text[:2000]
    if _HOLISTIC_HINTS.search(sample) and not _CLINICAL_HINTS.search(sample):
        return "holistic"
    if _CLINICAL_HINTS.search(sample):
        return "clinical"
    if any(k in p for k in ("radio", "comm", "meshtastic")):
        return "comms"
    if any(k in p for k in ("map", "geo", "flood", "fault", "topo")):
        return "geo"
    if any(k in p for k in ("defense", "tactical", "military", "field-manual")):
        return "defense"
    return "general"


def chunk_text(text: str, size: int = 1200, overlap: int = 150) -> list[str]:
    """Split text into overlapping word-ish chunks, respecting sentence-ish
    boundaries where possible."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        # try to break on a sentence boundary near the end
        if end < len(text):
            m = list(re.finditer(r"[.!?]\s", text[start:end]))
            if m and m[-1].end() > size * 0.5:
                end = start + m[-1].end()
        chunks.append(text[start:end].strip())
        start = max(end - overlap, end) if end <= start else end - overlap
        if start <= 0:
            break
    return [c for c in chunks if len(c) > 40]


def embed(texts: list[str], client: httpx.Client | None = None) -> list[list[float]]:
    """Embed a list of texts via Ollama. Returns one vector per input."""
    own = client is None
    client = client or httpx.Client(timeout=120)
    out = []
    try:
        for t in texts:
            r = client.post(f"{OLLAMA_URL}/api/embeddings",
                            json={"model": EMBED_MODEL, "prompt": t})
            r.raise_for_status()
            out.append(r.json()["embedding"])
    finally:
        if own:
            client.close()
    return out


def embed_dim(client: httpx.Client | None = None) -> int:
    """Probe the embedding dimension for collection creation."""
    return len(embed(["dimension probe"], client)[0])
