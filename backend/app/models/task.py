import uuid
import datetime as dt
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, JSON
from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    parent_task_id = Column(String, ForeignKey("tasks.id"), nullable=True)  # subtask linkage
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(String, default="general")  # research | coding | reasoning | ...
    assigned_agent = Column(String, nullable=True)

    status = Column(String, default="pending")  # pending | running | completed | failed
    priority = Column(Integer, default=5)
    depends_on = Column(JSON, default=list)  # list of task ids
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    retries = Column(Integer, default=0)

    created_at = Column(DateTime, default=dt.datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class TaskHistory(Base):
    __tablename__ = "task_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    status = Column(String, nullable=False)
    note = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=dt.datetime.utcnow)
