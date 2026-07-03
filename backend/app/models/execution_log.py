import uuid
import datetime as dt
from sqlalchemy import Column, String, DateTime, Text, Float
from app.database import Base


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, nullable=True)
    workflow_id = Column(String, nullable=True)
    agent_name = Column(String, nullable=True)
    tool_name = Column(String, nullable=True)
    event = Column(String, nullable=False)   # started | completed | failed | retry
    detail = Column(Text, nullable=True)
    duration_ms = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=dt.datetime.utcnow)
