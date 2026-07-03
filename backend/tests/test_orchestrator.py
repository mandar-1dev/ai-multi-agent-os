"""
These tests monkeypatch the Gemini client so the full agent/orchestrator/
workflow pipeline can be verified without a live API key or network access
(useful in CI and in sandboxed dev environments).
"""
import sys
import os
import json
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_agentos.db")

from app.llm import gemini_client as gemini_module


class FakeGeminiClient:
    """Deterministic stand-in for the real Gemini client."""

    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.4) -> str:
        if "Planner Agent" in system_prompt:
            return json.dumps([
                {"id": "t1", "title": "Research the topic", "agent": "research_agent", "depends_on": [], "task_type": "research"},
                {"id": "t2", "title": "Summarize findings", "agent": "documentation_agent", "depends_on": ["t1"], "task_type": "documentation"},
            ])
        if "Reviewer Agent" in system_prompt:
            return "VERDICT: APPROVED\nNo issues found."
        return f"[fake response for prompt: {user_prompt[:60]}]"

    async def embed(self, text: str) -> list[float]:
        # Deterministic pseudo-embedding so vector store calls don't hit the network.
        return [float((hash(text) >> i) % 100) / 100 for i in range(8)]


def patch_gemini():
    fake = FakeGeminiClient()
    gemini_module.gemini_client.generate = fake.generate
    gemini_module.gemini_client.embed = fake.embed


async def _run():
    patch_gemini()
    from app.database import init_db, SessionLocal
    from app.orchestrator.orchestrator import orchestrator

    init_db()
    db = SessionLocal()
    try:
        result = await orchestrator.run(db, "Write a short brief about vector databases")
        assert result["success"] is True, result
        assert len(result["subtasks"]) == 2
        assert result["subtasks"][0]["agent"] == "research_agent"
        assert result["subtasks"][1]["agent"] == "documentation_agent"
        print("Orchestrator end-to-end test passed.")
        print(json.dumps(result["summary"][:200], indent=2))
    finally:
        db.close()


async def _run_workflow():
    patch_gemini()
    from app.database import SessionLocal
    from app.workflow_engine.engine import workflow_engine

    db = SessionLocal()
    try:
        row = await workflow_engine.run(db, "research_workflow", "Explain retrieval augmented generation")
        assert row.status == "completed"
        assert len(row.steps) == 4
        print("Workflow engine test passed:", row.status)
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(_run())
    asyncio.run(_run_workflow())
