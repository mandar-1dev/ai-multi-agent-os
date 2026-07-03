from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.memory.memory_manager import memory_manager

router = APIRouter(prefix="/api/memory", tags=["memory"])


class StoreMemoryRequest(BaseModel):
    content: str
    memory_type: str = "conversation"
    user_id: str | None = None
    importance_score: float = 0.5


class RecallRequest(BaseModel):
    query: str
    memory_type: str | None = None
    top_k: int = 5


@router.post("/store")
async def store(payload: StoreMemoryRequest, db: Session = Depends(get_db)):
    record = await memory_manager.store(
        db, payload.content, payload.memory_type, payload.user_id, importance_score=payload.importance_score
    )
    return {"id": record.id, "memory_type": record.memory_type}


@router.post("/recall")
async def recall(payload: RecallRequest, db: Session = Depends(get_db)):
    return await memory_manager.recall(db, payload.query, payload.memory_type, payload.top_k)


@router.get("/recent")
def recent(memory_type: str | None = None, user_id: str | None = None, limit: int = 20, db: Session = Depends(get_db)):
    rows = memory_manager.recent(db, memory_type, user_id, limit)
    return [
        {"id": r.id, "memory_type": r.memory_type, "content": r.content[:500],
         "importance_score": r.importance_score, "created_at": r.created_at}
        for r in rows
    ]
