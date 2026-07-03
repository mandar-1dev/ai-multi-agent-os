"""
Central Orchestrator Engine.

Responsibilities (per spec):
  - receive user requests
  - break complex tasks into subtasks (via Planner Agent)
  - assign tasks to appropriate agents
  - manage dependencies (via TaskGraph)
  - schedule execution (sequential batches of parallel-safe subtasks)
  - monitor progress (emits events via `on_event` callback -> WebSocket)
  - combine outputs
  - handle failures + retry mechanism
  - return final response
"""
import asyncio
import datetime as dt
import json
import logging
from typing import Callable, Awaitable
from sqlalchemy.orm import Session

from app.agents.registry import get_agent, AGENT_REGISTRY
from app.orchestrator.task_graph import TaskGraph
from app.models.task import Task, TaskHistory
from app.models.agent import AgentModel
from app.models.execution_log import ExecutionLog
from app.rag.retriever import retrieve_context
from app.memory.memory_manager import memory_manager
from app.config import settings

logger = logging.getLogger("agentos.orchestrator")

EventCallback = Callable[[dict], Awaitable[None]]


class Orchestrator:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(settings.MAX_PARALLEL_AGENTS)

    async def _emit(self, on_event: EventCallback | None, event: dict):
        if on_event:
            try:
                await on_event(event)
            except Exception:  # noqa: BLE001
                logger.debug("event emit failed", exc_info=True)

    def _log_db(self, db: Session, **kwargs):
        db.add(ExecutionLog(**kwargs))
        db.commit()

    def _touch_agent_stats(self, db: Session, agent_name: str, success: bool, duration_ms: float):
        row = db.query(AgentModel).filter(AgentModel.name == agent_name).first()
        if not row:
            return
        prev_total = row.total_runs
        row.total_runs += 1
        if not success:
            row.total_failures += 1
        row.avg_latency_ms = ((row.avg_latency_ms * prev_total) + duration_ms) / row.total_runs
        row.last_run_at = dt.datetime.utcnow()
        row.status = "idle"
        db.commit()

    async def _run_subtask_with_retry(self, db: Session, task_row: Task, context: dict,
                                       on_event: EventCallback | None) -> dict:
        agent_name = task_row.assigned_agent
        attempts = 0
        last_error = None

        async with self.semaphore:
            row = db.query(AgentModel).filter(AgentModel.name == agent_name).first()
            if row:
                row.status = "running"
                db.commit()

            await self._emit(on_event, {"type": "agent_started", "agent": agent_name, "task_id": task_row.id, "title": task_row.title})
            self._log_db(db, task_id=task_row.id, agent_name=agent_name, event="started")

            while attempts <= settings.MAX_TASK_RETRIES:
                try:
                    agent = get_agent(agent_name)
                    output = await agent.run(task_row.title, context)
                    if not output.success:
                        raise RuntimeError(output.error or "agent returned failure")

                    task_row.status = "completed"
                    task_row.result = output.content
                    task_row.completed_at = dt.datetime.utcnow()
                    db.commit()

                    self._touch_agent_stats(db, agent_name, True, output.duration_ms)
                    self._log_db(db, task_id=task_row.id, agent_name=agent_name, event="completed", duration_ms=output.duration_ms)
                    await self._emit(on_event, {"type": "agent_completed", "agent": agent_name, "task_id": task_row.id, "content": output.content[:2000]})
                    return {"id": task_row.id, "agent": agent_name, "title": task_row.title, "success": True, "output": output.content}

                except Exception as e:  # noqa: BLE001
                    last_error = str(e)
                    attempts += 1
                    task_row.retries = attempts
                    db.commit()
                    self._log_db(db, task_id=task_row.id, agent_name=agent_name, event="retry", detail=last_error)
                    await self._emit(on_event, {"type": "agent_retry", "agent": agent_name, "task_id": task_row.id, "attempt": attempts, "error": last_error})

            task_row.status = "failed"
            task_row.error = last_error
            db.commit()
            self._touch_agent_stats(db, agent_name, False, 0.0)
            self._log_db(db, task_id=task_row.id, agent_name=agent_name, event="failed", detail=last_error)
            await self._emit(on_event, {"type": "agent_failed", "agent": agent_name, "task_id": task_row.id, "error": last_error})
            return {"id": task_row.id, "agent": agent_name, "title": task_row.title, "success": False, "error": last_error}

    async def run(self, db: Session, user_goal: str, user_id: str | None = None,
                   on_event: EventCallback | None = None) -> dict:
        """
        Full lifecycle: plan -> retrieve context -> execute DAG -> combine -> return.
        """
        await self._emit(on_event, {"type": "orchestrator_started", "goal": user_goal})

        # 1. Retrieve grounding context (RAG over documents + long-term memory)
        rag_hits = await retrieve_context(user_goal, top_k=4)
        memory_hits = await memory_manager.recall(db, user_goal, top_k=4)
        retrieved_context = "\n---\n".join(
            [h["text"] for h in rag_hits] + [h["content"] for h in memory_hits]
        )[:6000]

        # 2. Plan: decompose the goal into a subtask DAG
        planner = get_agent("planner_agent")
        plan_output = await planner.run(user_goal, {"retrieved_context": retrieved_context})
        try:
            subtasks = json.loads(plan_output.content)
        except Exception:
            subtasks = [{"id": "t1", "title": user_goal, "agent": "reasoning_agent", "depends_on": [], "task_type": "general"}]

        await self._emit(on_event, {"type": "plan_ready", "subtasks": subtasks})

        # 3. Materialize Task rows
        task_rows: dict[str, Task] = {}
        for st in subtasks:
            agent_name = st.get("agent") if st.get("agent") in AGENT_REGISTRY else "reasoning_agent"
            row = Task(
                user_id=user_id,
                title=st.get("title", "Untitled subtask"),
                task_type=st.get("task_type", "general"),
                assigned_agent=agent_name,
                status="pending",
                depends_on=st.get("depends_on", []),
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            task_rows[st["id"]] = row
            self._log_db(db, task_id=row.id, agent_name=agent_name, event="queued")

        # map planner-local ids -> real Task rows for dependency batching
        id_map = {local_id: row.id for local_id, row in task_rows.items()}
        graph_input = [
            {"id": local_id, "depends_on": st.get("depends_on", [])}
            for local_id, st in zip(task_rows.keys(), subtasks)
        ]
        graph = TaskGraph(graph_input)

        outputs_by_local_id: dict[str, dict] = {}
        all_results = []

        # 4. Execute in dependency-respecting batches (parallel within a batch)
        for batch in graph.batches():
            batch_local_ids = [b["id"] for b in batch]
            await self._emit(on_event, {"type": "batch_started", "tasks": batch_local_ids})

            coros = []
            for local_id in batch_local_ids:
                row = task_rows[local_id]
                row.status = "running"
                row.started_at = dt.datetime.utcnow()
                db.commit()
                dep_outputs = {d: outputs_by_local_id.get(d) for d in row.depends_on}
                context = {"retrieved_context": retrieved_context, "previous_outputs": dep_outputs}
                coros.append(self._run_subtask_with_retry(db, row, context, on_event))

            results = await asyncio.gather(*coros)
            for local_id, result in zip(batch_local_ids, results):
                outputs_by_local_id[local_id] = result
                all_results.append(result)

        # 5. Combine outputs via Documentation Agent, then quality-check via Reviewer Agent
        combined_input = json.dumps(all_results, indent=2)[:8000]
        doc_agent = get_agent("documentation_agent")
        summary_output = await doc_agent.run(
            f"Summarize the results of this multi-agent execution for the original goal: '{user_goal}'",
            {"previous_outputs": all_results},
        )

        reviewer = get_agent("reviewer_agent")
        review_output = await reviewer.run(
            f"Review the combined output below for the goal: '{user_goal}'",
            {"previous_outputs": all_results, "retrieved_context": summary_output.content},
        )

        final_response = {
            "goal": user_goal,
            "subtasks": all_results,
            "summary": summary_output.content,
            "review": review_output.content,
            "success": all(r["success"] for r in all_results),
        }

        # 6. Persist to long-term memory
        await memory_manager.store(
            db, content=f"GOAL: {user_goal}\nSUMMARY: {summary_output.content}",
            memory_type="task", user_id=user_id, importance_score=0.6,
        )

        await self._emit(on_event, {"type": "orchestrator_completed", "result": final_response})
        return final_response


orchestrator = Orchestrator()
