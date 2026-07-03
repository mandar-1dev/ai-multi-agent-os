import uuid
import datetime as dt
from sqlalchemy.orm import Session
from app.models.memory import MemoryRecord
from app.rag import vector_store
from app.rag.embeddings import embed_text


class MemoryManager:
    """
    Implements the memory taxonomy from the spec:
      conversation | task | preference | project | semantic | knowledge
    Structured metadata -> Postgres/SQLite (MemoryRecord)
    Vector representation -> ChromaDB (for semantic similarity retrieval)
    """

    async def store(
        self,
        db: Session,
        content: str,
        memory_type: str = "conversation",
        user_id: str | None = None,
        summary: str | None = None,
        importance_score: float = 0.5,
    ) -> MemoryRecord:
        vector_id = str(uuid.uuid4())
        record = MemoryRecord(
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            summary=summary,
            importance_score=importance_score,
            vector_id=vector_id,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        vec = await embed_text(content)
        vector_store.add_documents(
            ids=[vector_id],
            documents=[content],
            metadatas=[{
                "memory_type": memory_type,
                "user_id": user_id or "anonymous",
                "importance_score": importance_score,
                "record_id": record.id,
            }],
            embeddings=None if vec is None else [vec],
        )
        return record

    async def recall(self, db: Session, query: str, memory_type: str | None = None, top_k: int = 5) -> list[dict]:
        vec = await embed_text(query)
        where = {"memory_type": memory_type} if memory_type else None
        results = vector_store.query(
            query_text=None if vec else query,
            query_embedding=vec,
            n_results=top_k,
            where=where,
        )
        hits = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        for doc, meta in zip(docs, metas):
            hits.append({"content": doc, "metadata": meta})

        # touch last_accessed_at for retrieved records
        record_ids = [m.get("record_id") for m in metas if m.get("record_id")]
        if record_ids:
            db.query(MemoryRecord).filter(MemoryRecord.id.in_(record_ids)).update(
                {"last_accessed_at": dt.datetime.utcnow()}, synchronize_session=False
            )
            db.commit()
        return hits

    def recent(self, db: Session, memory_type: str | None = None, user_id: str | None = None, limit: int = 20):
        q = db.query(MemoryRecord)
        if memory_type:
            q = q.filter(MemoryRecord.memory_type == memory_type)
        if user_id:
            q = q.filter(MemoryRecord.user_id == user_id)
        return q.order_by(MemoryRecord.created_at.desc()).limit(limit).all()


memory_manager = MemoryManager()
