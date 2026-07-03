import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, SessionLocal
from app.models.agent import AgentModel
from app.agents.registry import list_agents

from app.auth.routes import router as auth_router
from app.routes.agents import router as agents_router
from app.routes.tasks import router as tasks_router
from app.routes.chat import router as chat_router
from app.routes.workflows import router as workflows_router
from app.routes.memory import router as memory_router
from app.routes.documents import router as documents_router
from app.routes.knowledge_graph import router as kg_router
from app.routes.dashboard import router as dashboard_router
from app.websocket.routes import router as ws_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

app = FastAPI(
    title=settings.APP_NAME,
    description="A multi-agent AI operating system: orchestrator, specialist agents, RAG, "
                "long-term memory, tool calling, workflows, and a knowledge graph.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in [auth_router, agents_router, tasks_router, chat_router, workflows_router,
          memory_router, documents_router, kg_router, dashboard_router]:
    app.include_router(r)

app.include_router(ws_router)


@app.on_event("startup")
def on_startup():
    init_db()
    # Seed the agents table from the code-level agent registry so the
    # dashboard has status rows to display/update.
    db = SessionLocal()
    try:
        existing = {a.name for a in db.query(AgentModel).all()}
        for definition in list_agents():
            if definition["name"] not in existing:
                db.add(AgentModel(
                    name=definition["name"],
                    display_name=definition["display_name"],
                    role=definition["role"][:2000] if isinstance(definition["role"], str) else "dynamic",
                ))
        db.commit()
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "status": "running",
        "docs": "/docs",
        "websocket": "/ws/agent-status",
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}
