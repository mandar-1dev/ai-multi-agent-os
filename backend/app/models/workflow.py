import uuid
import datetime as dt
from sqlalchemy import Column, String, DateTime, Text, JSON
from app.database import Base


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True)
    name = Column(String, nullable=False)          # research_workflow | coding_workflow | learning_workflow
    goal = Column(Text, nullable=False)
    status = Column(String, default="pending")      # pending | running | completed | failed
    steps = Column(JSON, default=list)               # ordered step definitions
    final_output = Column(Text, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
