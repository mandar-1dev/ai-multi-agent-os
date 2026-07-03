# Agent OS — AI Multi-Agent Operating System

A working multi-agent AI platform: an **orchestrator** decomposes a goal into subtasks,
dispatches them to **9 specialist agents** (in parallel where possible), grounds them
with **RAG** + **long-term memory**, lets them call **tools**, runs predefined
**multi-step workflows**, and builds a **knowledge graph** from what it learns — all
visible live on a React dashboard via WebSocket.

---

## Architecture

```
                         ┌─────────────────────┐
   User goal  ─────────► │   Orchestrator       │
                         │  (plan → DAG → run)  │
                         └──────────┬───────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 ▼                  ▼                  ▼
          Planner Agent      Research Agent      Coding Agent  ...(9 total)
                 │                  │                  │
                 └────────► Tool Execution Agent ◄──────┘
                                    │
                    ┌───────────────┼────────────────┐
                    ▼               ▼                ▼
              RAG Pipeline   Long-Term Memory   Knowledge Graph
             (ChromaDB)      (Postgres/SQLite    (entities/edges,
                               + ChromaDB)         Reasoning Agent)
```

**Agents:** Planner, Research, Memory, Reasoning, Coding, Documentation, Reviewer,
Tool Execution, Decision.

**Workflows:** Research → Summarize → Fact-check → Report · Requirement Analysis →
Plan → Code → Review → Docs → Tests · Knowledge Extraction → Memory → Quiz →
Recommendations.

**Tools:** calculator, restricted Python execution, file reader (PDF/DOCX/CSV/TXT/JSON),
web search (DuckDuckGo HTML, no key needed).

---

## Tech stack

| Layer | Tech |
|---|---|
| Backend | FastAPI, SQLAlchemy, Pydantic, JWT auth, WebSockets, asyncio |
| AI | Google Gemini (`google-genai` SDK) — generation + embeddings |
| Storage | SQLite (default, zero setup) or PostgreSQL, Redis, ChromaDB (vectors) |
| Frontend | React + TypeScript + Vite, Tailwind CSS v4, React Router, ReactFlow |
| Deployment | Docker Compose (backend, frontend, redis) |

---

## What you need

### A Google Gemini API key (required)
Get a free one at **https://aistudio.google.com/apikey**.

### Correct model names
Google retires Gemini model versions on a rolling schedule. If agents start failing
with `ClientError: 404 NOT_FOUND`, check the current model names at
https://ai.google.dev/gemini-api/docs/deprecations and update `GEMINI_MODEL` /
`GEMINI_EMBEDDING_MODEL` below. At the time of writing, the defaults are:
```
GEMINI_MODEL=gemini-3.5-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
```

### Nothing else
SQLite is the default DB (no Postgres install needed) and the web-search tool needs
no key.

---

## Quick start — Docker (recommended)

**1. Create the environment file at the project root** (same folder as
`docker-compose.yml` — this is important, Compose only reads `.env` from here, not
from `backend/.env`):

```bash
cp backend/.env.example .env
```
Edit `.env` and set:
```
GEMINI_API_KEY=your_key_here
```

**2. Build and start everything:**
```bash
docker compose up --build
```

**3. Open:**
- Frontend: **http://localhost**
- API docs (Swagger): **http://localhost:8000/docs**
- WebSocket live feed: `ws://localhost:8000/ws/agent-status`

**4. Register an account** on the frontend — the first account created automatically
becomes admin.

### If a port is already in use

`docker ps` first, to see what's occupying it — you may have another project's
container bound to the same port. Either stop that container, or remap ports in
`docker-compose.yml`:
```yaml
  backend:
    ports:
      - "8010:8000"   # host:container
```
If you remap the backend port, also update the frontend's build arg so the browser
calls the right place:
```yaml
  frontend:
    build:
      context: ./frontend
      args:
        VITE_API_URL: ${VITE_API_URL:-http://localhost:8010}
```

### Full reset (clears all data — accounts, tasks, vector store)
```bash
docker compose down -v
docker compose up --build
```
Useful if you change embedding models mid-project — ChromaDB stores a fixed vector
dimensionality per collection, so switching embedding models after data exists will
throw `InvalidDimensionException` until the old vector data is cleared.

---

## Quick start — local dev (no Docker)

**Backend**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # add your GEMINI_API_KEY
uvicorn app.main:app --reload
```

**Frontend** (separate terminal)
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open **http://localhost:5173**.

---

## Try it out

Go to **Orchestrate** and enter a goal, e.g.:
> "Research vector databases and write a short comparison of Chroma vs Pinecone"

Watch the live execution trace as the Planner Agent decomposes the goal and hands
subtasks to specialist agents. Also try:
- **Workflows** → run the `research_workflow` template
- **Documents** → upload a PDF/CSV to test RAG ingestion
- **Knowledge Graph** → fills in automatically as you run more goals

---

## Project structure

```
backend/
  app/
    agents/            9 specialist agents + registry
    orchestrator/       plan → DAG → parallel/sequential execution engine
    workflow_engine/    predefined multi-step workflow templates
    rag/                chunking, embeddings, ChromaDB vector store, retriever
    memory/             long-term memory manager (6 memory types)
    tools/              calculator, python_exec, file_reader, web_search
    knowledge_graph/    entity/relationship extraction + graph API
    auth/               JWT register/login
    llm/                Gemini client wrapper
    models/             SQLAlchemy models
    routes/             REST endpoints
    websocket/          live agent-status broadcast
  tests/                offline tool tests + mocked-LLM orchestrator/workflow tests
frontend/
  src/
    pages/              Dashboard, Chat (Orchestrate), Tasks, Workflows,
                         KnowledgeGraph, Memory, Documents, Login
    components/         Layout, shared UI primitives
    hooks/               live WebSocket hook
    api/                typed API client
docker-compose.yml
```

---

## Running the tests

```bash
cd backend && source venv/bin/activate
python tests/test_tools.py          # offline: calculator, python_exec sandboxing
python tests/test_orchestrator.py   # mocked-LLM: full orchestrator + workflow engine
```

---

## Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| `port is already allocated` on `docker compose up` | Another container (yours or a different project) already uses that port. Run `docker ps`, stop the conflicting container or remap the port in `docker-compose.yml`. |
| `GEMINI_API_KEY variable is not set` warning | `.env` must be at the **project root**, next to `docker-compose.yml` — not inside `backend/`. |
| All agents show `FAILED` | Check `docker compose logs backend --tail=100` for a `ClientError` line. Usually an invalid/missing key, or a retired model name — see [current model names](https://ai.google.dev/gemini-api/docs/deprecations). |
| `ClientError: 404 NOT_FOUND ... model ... not found` | The model name in `GEMINI_MODEL`/`GEMINI_EMBEDDING_MODEL` has been retired by Google. Update to a current model name. |
| `InvalidDimensionException: Embedding dimension X does not match collection dimensionality Y` | You changed embedding models after data already existed in ChromaDB. Run `docker compose down -v` to reset the vector store, then `docker compose up --build`. |
| Frontend loads but all API calls fail / CORS errors | The frontend's `VITE_API_URL` is baked in at **build time**. If you changed the backend port or are accessing from another machine, rebuild with the correct value: `docker compose build --build-arg VITE_API_URL=http://<host>:<port> frontend`. |
| Backend container restarts / crash-loops | Run `docker compose logs backend` for the traceback — usually a missing env var or a dependency issue. |

---

## Scope notes

This implements the core, hard engineering parts of a multi-agent system end-to-end
and *tested*: orchestration, agent DAG execution with retries, RAG, long-term memory,
tool calling, a workflow engine, and a knowledge graph. It intentionally does **not**
include OAuth login, Celery/task-queue workers, or cloud deployment scripts — JWT
auth and `asyncio` concurrency are used instead. Redis is wired in and ready if you
want to add Celery workers later.

### Extending this later
- **OAuth:** add `authlib` + Google/GitHub OAuth routes alongside the existing JWT flow.
- **Celery:** Redis is already wired in — add a `celery_app.py` and move long-running
  orchestrator runs into a worker + polling/websocket status.
- **Postgres in production:** set `DATABASE_URL` to a Postgres DSN; the SQLAlchemy
  models are dialect-agnostic.
- **More agents/tools:** drop a new file in `app/agents/` or `app/tools/`, register it
  in the respective `registry.py` — the Planner Agent's prompt already knows how to
  route to it.

---

## License

MIT (or your preferred license — add a `LICENSE` file to the repo root).