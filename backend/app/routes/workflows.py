from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.workflow_engine.engine import workflow_engine
from app.websocket.manager import broadcast_event
from app.models.workflow import Workflow

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


class WorkflowRequest(BaseModel):
    workflow_name: str
    goal: str
    user_id: str | None = None


@router.get("/templates")
def templates():
    return workflow_engine.list_templates()


@router.get("")
def list_workflows(db: Session = Depends(get_db)):
    rows = db.query(Workflow).order_by(Workflow.created_at.desc()).limit(50).all()
    return [
        {"id": w.id, "name": w.name, "goal": w.goal, "status": w.status, "created_at": w.created_at}
        for w in rows
    ]


@router.post("/run")
async def run_workflow(payload: WorkflowRequest, db: Session = Depends(get_db)):
    row = await workflow_engine.run(db, payload.workflow_name, payload.goal, payload.user_id, on_event=broadcast_event)
    return {
        "id": row.id, "name": row.name, "status": row.status,
        "steps": row.steps, "final_output": row.final_output,
    }
