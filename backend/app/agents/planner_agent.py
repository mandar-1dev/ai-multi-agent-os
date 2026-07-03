import json
import re
from app.agents.base_agent import BaseAgent


class PlannerAgent(BaseAgent):
    name = "planner_agent"
    display_name = "Planner Agent"
    temperature = 0.2
    system_prompt = (
        "You are the Planner Agent inside a multi-agent operating system. "
        "Given a complex user goal, break it into a minimal set of concrete subtasks. "
        "Each subtask must be assignable to exactly one specialist agent from this list: "
        "research_agent, memory_agent, reasoning_agent, coding_agent, documentation_agent, "
        "reviewer_agent, tool_execution_agent, decision_agent. "
        "Respond with ONLY a JSON array, no prose, no markdown fences. Each item: "
        '{"id": "t1", "title": "...", "agent": "research_agent", "depends_on": [], "task_type": "research"}. '
        "Keep it to 3-7 subtasks. Use depends_on ids to express ordering; independent tasks can run in parallel."
    )

    def parse_output(self, raw: str) -> str:
        cleaned = re.sub(r"```json|```", "", raw).strip()
        try:
            plan = json.loads(cleaned)
            if not isinstance(plan, list):
                raise ValueError("Planner did not return a JSON list")
            return json.dumps(plan)
        except Exception:
            # Fallback: single-step plan so the orchestrator can still proceed
            return json.dumps([{
                "id": "t1", "title": cleaned[:200], "agent": "reasoning_agent",
                "depends_on": [], "task_type": "general",
            }])
