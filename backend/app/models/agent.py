import uuid
import datetime as dt
from sqlalchemy import Column, String, DateTime, Text, Integer, Float
from app.database import Base


class AgentModel(Base):
    """Persisted record of each specialized agent for dashboard/monitoring."""
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)          # e.g. "planner_agent"
    display_name = Column(String, nullable=False)                 # e.g. "Planner Agent"
    role = Column(Text, nullable=False)                           # system prompt / responsibility
    status = Column(String, default="idle")                       # idle | running | error
    total_runs = Column(Integer, default=0)
    total_failures = Column(Integer, default=0)
    avg_latency_ms = Column(Float, default=0.0)
    last_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
