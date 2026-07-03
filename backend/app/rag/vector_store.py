"""
ChromaDB-backed vector store. Uses Chroma's default local embedding function
for indexing convenience, but exposes `add_with_vectors` for callers (like
the RAG retriever) that want to supply their own Gemini embeddings.
"""
import chromadb
from app.config import settings

_client = None
_collection = None


def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=chromadb.config.Settings(anonymized_telemetry=False),
        )
        _collection = _client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_documents(ids: list[str], documents: list[str], metadatas: list[dict], embeddings: list[list[float]] | None = None):
    collection = get_collection()
    kwargs = dict(ids=ids, documents=documents, metadatas=metadatas)
    if embeddings is not None:
        kwargs["embeddings"] = embeddings
    collection.add(**kwargs)


def query(query_text: str = None, query_embedding: list[float] = None, n_results: int = 5, where: dict = None):
    collection = get_collection()
    kwargs = {"n_results": n_results}
    if where:
        kwargs["where"] = where
    if query_embedding is not None:
        kwargs["query_embeddings"] = [query_embedding]
    else:
        kwargs["query_texts"] = [query_text]
    return collection.query(**kwargs)


def count() -> int:
    return get_collection().count()
