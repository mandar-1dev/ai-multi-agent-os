from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.orchestrator.orchestrator import orchestrator
from app.websocket.manager import broadcast_event

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    user_id: str | None = None


@router.post("")
async def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Main entry point: send a natural-language goal, the orchestrator plans,
    dispatches to specialist agents, and returns the combined result.
    Progress is also streamed live over /ws/agent-status.
    """
    result = await orchestrator.run(db, payload.message, payload.user_id, on_event=broadcast_event)
    return result
