from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.agent import AgentModel
from app.agents.registry import list_agents

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("")
def get_agents(db: Session = Depends(get_db)):
    rows = db.query(AgentModel).all()
    return [
        {
            "name": r.name, "display_name": r.display_name, "status": r.status,
            "total_runs": r.total_runs, "total_failures": r.total_failures,
            "avg_latency_ms": round(r.avg_latency_ms, 2), "last_run_at": r.last_run_at,
        }
        for r in rows
    ]


@router.get("/definitions")
def get_agent_definitions():
    """Static role/prompt info for each agent type (not DB-backed)."""
    return list_agents()
