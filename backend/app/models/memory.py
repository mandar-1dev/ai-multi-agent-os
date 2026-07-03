import uuid
import datetime as dt
from sqlalchemy import Column, String, DateTime, Text, Float
from app.database import Base


class MemoryRecord(Base):
    """
    Long-term memory row. The embedding vector itself is stored in ChromaDB,
    keyed by `vector_id`; this table holds the structured metadata Postgres
    is good at querying/filtering on.
    """
    __tablename__ = "memory"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True)
    memory_type = Column(String, default="conversation")
    # conversation | task | preference | project | semantic | knowledge
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    importance_score = Column(Float, default=0.5)  # 0-1, used to prioritize retrieval/decay
    vector_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    last_accessed_at = Column(DateTime, default=dt.datetime.utcnow)
