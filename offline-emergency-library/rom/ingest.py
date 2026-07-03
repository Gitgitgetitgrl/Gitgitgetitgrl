"""Build Rom's searchable index.

Walks the mounted content library:
  - every *.zim file in /content/zim   (via libzim)
  - every *.pdf / *.txt / *.md in /content (guides, manuals, personal docs)
chunks it, embeds each chunk with Ollama, and upserts into Qdrant.

Run:  docker compose exec rom python ingest.py
Re-run any time you add content (it upserts; stale entries for changed files
are replaced by deterministic IDs).
"""
import glob
import hashlib
import os
import sys

import httpx
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from tqdm import tqdm

from common import (COLLECTION, QDRANT_URL, chunk_text, classify_collection,
                    embed, embed_dim)

CONTENT_DIR = "/content"
ZIM_DIR = "/content/zim"


def _point_id(source: str, idx: int) -> int:
    h = hashlib.sha1(f"{source}#{idx}".encode()).hexdigest()
    return int(h[:15], 16)  # stable positive 60-bit id


def iter_pdf(path):
    from pypdf import PdfReader
    try:
        reader = PdfReader(path)
    except Exception as e:  # corrupt / encrypted
        print(f"  ! skip {path}: {e}")
        return
    for page in reader.pages:
        try:
            yield page.extract_text() or ""
        except Exception:
            yield ""


def iter_text(path):
    with open(path, "r", errors="ignore") as f:
        yield f.read()


def iter_zim(path):
    """Yield (article_title, text, url) for readable articles in a .zim."""
    from libzim.reader import Archive
    from bs4 import BeautifulSoup
    zim = Archive(path)
    base = os.path.basename(path)
    count = zim.all_entry_count
    for i in range(count):
        try:
            entry = zim._get_entry_by_id(i)
            item = entry.get_item()
            mime = item.mimetype
            if "html" not in mime:
                continue
            html = bytes(item.content).decode("utf-8", errors="ignore")
            text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
            if len(text) < 200:
                continue
            url = f"{base}::/{entry.path}"
            yield entry.title or entry.path, text, url
        except Exception:
            continue


def gather_documents():
    """Yield (source_id, title, text, url) documents from the whole library."""
    # ZIM archives
    for zim_path in sorted(glob.glob(os.path.join(ZIM_DIR, "*.zim"))):
        print(f"[zim] {os.path.basename(zim_path)}")
        for title, text, url in iter_zim(zim_path):
            yield zim_path, title, text, url

    # Loose PDFs / text / markdown anywhere under /content (excluding private)
    patterns = ("**/*.pdf", "**/*.txt", "**/*.md")
    for pat in patterns:
        for path in sorted(glob.glob(os.path.join(CONTENT_DIR, pat), recursive=True)):
            if "/private/" in path or "/zim/" in path:
                continue
            title = os.path.relpath(path, CONTENT_DIR)
            print(f"[doc] {title}")
            joiner = iter_pdf if path.lower().endswith(".pdf") else iter_text
            text = " ".join(joiner(path))
            if text.strip():
                yield path, title, text, title


def main():
    client = QdrantClient(url=QDRANT_URL)
    http = httpx.Client(timeout=120)

    dim = embed_dim(http)
    if not client.collection_exists(COLLECTION):
        client.create_collection(
            COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        print(f"Created Qdrant collection '{COLLECTION}' (dim={dim})")

    batch, total = [], 0
    BATCH = 64

    def flush():
        nonlocal batch, total
        if not batch:
            return
        vectors = embed([b["text"] for b in batch], http)
        points = [
            PointStruct(id=b["id"], vector=v, payload={
                "title": b["title"], "text": b["text"],
                "url": b["url"], "collection": b["collection"],
                "source": b["source"],
            })
            for b, v in zip(batch, vectors)
        ]
        client.upsert(COLLECTION, points=points)
        total += len(points)
        batch = []

    for source, title, text, url in gather_documents():
        collection = classify_collection(url or source, text)
        for i, ch in enumerate(chunk_text(text)):
            batch.append({
                "id": _point_id(f"{source}:{url}", i),
                "title": title, "text": ch, "url": url,
                "collection": collection, "source": os.path.basename(source),
            })
            if len(batch) >= BATCH:
                flush()
                print(f"  indexed {total} chunks...", end="\r")

    flush()
    http.close()
    print(f"\nDone. Indexed {total} chunks into '{COLLECTION}'.")
    if total == 0:
        print("No content found. Put .zim files in content/zim/ or PDFs in content/,"
              " then run scripts/02-download-content.sh.", file=sys.stderr)


if __name__ == "__main__":
    main()
