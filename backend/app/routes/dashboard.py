from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.task import Task
from app.models.agent import AgentModel
from app.models.workflow import Workflow
from app.models.execution_log import ExecutionLog
from app.models.document import Document
from app.rag import vector_store

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    total_tasks = db.query(Task).count()
    pending = db.query(Task).filter(Task.status == "pending").count()
    running = db.query(Task).filter(Task.status == "running").count()
    completed = db.query(Task).filter(Task.status == "completed").count()
    failed = db.query(Task).filter(Task.status == "failed").count()

    try:
        vector_count = vector_store.count()
    except Exception:
        vector_count = 0

    return {
        "tasks": {"total": total_tasks, "pending": pending, "running": running, "completed": completed, "failed": failed},
        "agents": db.query(AgentModel).count(),
        "workflows": db.query(Workflow).count(),
        "documents": db.query(Document).count(),
        "vector_entries": vector_count,
        "recent_logs": [
            {"agent_name": l.agent_name, "event": l.event, "timestamp": l.timestamp}
            for l in db.query(ExecutionLog).order_by(ExecutionLog.timestamp.desc()).limit(15).all()
        ],
    }
