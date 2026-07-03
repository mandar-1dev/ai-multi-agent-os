from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.task import Task

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("")
def list_tasks(status: str | None = None, limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(Task)
    if status:
        q = q.filter(Task.status == status)
    rows = q.order_by(Task.created_at.desc()).limit(limit).all()
    return [
        {
            "id": t.id, "title": t.title, "task_type": t.task_type,
            "assigned_agent": t.assigned_agent, "status": t.status,
            "result": t.result, "error": t.error, "retries": t.retries,
            "created_at": t.created_at, "completed_at": t.completed_at,
        }
        for t in rows
    ]


@router.get("/{task_id}")
def get_task(task_id: str, db: Session = Depends(get_db)):
    t = db.query(Task).filter(Task.id == task_id).first()
    if not t:
        return {"error": "not found"}
    return {
        "id": t.id, "title": t.title, "task_type": t.task_type,
        "assigned_agent": t.assigned_agent, "status": t.status,
        "result": t.result, "error": t.error, "retries": t.retries,
        "depends_on": t.depends_on, "created_at": t.created_at, "completed_at": t.completed_at,
    }
