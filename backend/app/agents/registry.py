from app.agents.planner_agent import PlannerAgent
from app.agents.research_agent import ResearchAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.reasoning_agent import ReasoningAgent
from app.agents.coding_agent import CodingAgent
from app.agents.documentation_agent import DocumentationAgent
from app.agents.reviewer_agent import ReviewerAgent
from app.agents.tool_execution_agent import ToolExecutionAgent
from app.agents.decision_agent import DecisionAgent

AGENT_REGISTRY = {
    a.name: a for a in [
        PlannerAgent(), ResearchAgent(), MemoryAgent(), ReasoningAgent(),
        CodingAgent(), DocumentationAgent(), ReviewerAgent(),
        ToolExecutionAgent(), DecisionAgent(),
    ]
}


def get_agent(name: str):
    agent = AGENT_REGISTRY.get(name)
    if agent is None:
        raise KeyError(f"Unknown agent '{name}'. Available: {list(AGENT_REGISTRY.keys())}")
    return agent


def list_agents() -> list[dict]:
    return [
        {"name": a.name, "display_name": a.display_name, "role": a.system_prompt if isinstance(a.system_prompt, str) else "(dynamic)"}
        for a in AGENT_REGISTRY.values()
    ]
