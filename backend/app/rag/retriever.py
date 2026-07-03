import uuid
from app.rag.chunking import chunk_text
from app.rag.embeddings import embed_text
from app.rag import vector_store


async def ingest_document(document_id: str, text: str, source_filename: str) -> list[str]:
    """Chunk a document, embed each chunk, and store it in the vector DB."""
    chunks = chunk_text(text)
    if not chunks:
        return []

    ids, embeddings, metadatas = [], [], []
    any_embedding_failed = False

    for i, chunk in enumerate(chunks):
        vec = await embed_text(chunk)
        if vec is None:
            any_embedding_failed = True
        ids.append(f"{document_id}_{i}")
        embeddings.append(vec)
        metadatas.append({"document_id": document_id, "chunk_index": i, "source": source_filename})

    # If any embedding failed, drop to Chroma's built-in embedder for the whole batch
    # (Chroma requires a consistent embedding source per collection.add call).
    final_embeddings = None if any_embedding_failed else embeddings
    vector_store.add_documents(ids=ids, documents=chunks, metadatas=metadatas, embeddings=final_embeddings)
    return ids


async def retrieve_context(query_text: str, top_k: int = 5, where: dict | None = None) -> list[dict]:
    """Hybrid-ish retrieval: try Gemini embedding first, fall back to text query."""
    vec = await embed_text(query_text)
    results = vector_store.query(
        query_text=None if vec else query_text,
        query_embedding=vec,
        n_results=top_k,
        where=where,
    )

    hits = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0] if results.get("distances") else [None] * len(docs)
    for doc, meta, dist in zip(docs, metas, dists):
        hits.append({"text": doc, "metadata": meta, "distance": dist})
    return hits


def new_document_id() -> str:
    return str(uuid.uuid4())
