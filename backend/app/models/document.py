import uuid
import datetime as dt
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)   # pdf | docx | csv | txt | md | json
    summary = Column(Text, nullable=True)
    num_chunks = Column(Integer, default=0)
    status = Column(String, default="processing")  # processing | ready | failed
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class EmbeddingRecord(Base):
    """Metadata row for each chunk stored in the vector DB (actual vectors live in ChromaDB)."""
    __tablename__ = "embeddings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    chunk_index = Column(Integer, default=0)
    chunk_text = Column(Text, nullable=False)
    vector_id = Column(String, nullable=False)  # id inside chroma collection
    created_at = Column(DateTime, default=dt.datetime.utcnow)
