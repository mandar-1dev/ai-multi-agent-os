from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.knowledge_graph.graph_builder import extract_and_store, get_graph

router = APIRouter(prefix="/api/knowledge-graph", tags=["knowledge-graph"])


class ExtractRequest(BaseModel):
    text: str


@router.post("/extract")
async def extract(payload: ExtractRequest, db: Session = Depends(get_db)):
    return await extract_and_store(db, payload.text)


@router.get("")
def graph(db: Session = Depends(get_db)):
    return get_graph(db)
