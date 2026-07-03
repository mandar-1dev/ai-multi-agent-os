import uuid
import datetime as dt
from sqlalchemy import Column, String, DateTime, Text
from app.database import Base


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    label = Column(String, nullable=False)         # entity name, e.g. "FastAPI"
    node_type = Column(String, default="topic")    # user|project|topic|task|agent|document|technology|company|person
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String, nullable=False)
    target_id = Column(String, nullable=False)
    relation = Column(String, default="related_to")  # e.g. "uses", "part_of", "created_by"
    weight = Column(String, default="1")
    created_at = Column(DateTime, default=dt.datetime.utcnow)
