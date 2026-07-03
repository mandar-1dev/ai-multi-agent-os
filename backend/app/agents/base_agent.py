import time
import json
import logging
from app.llm.gemini_client import gemini_client

logger = logging.getLogger("agentos.agents")


class AgentOutput:
    def __init__(self, agent_name: str, success: bool, content: str, raw: str = "",
                 duration_ms: float = 0.0, error: str | None = None):
        self.agent_name = agent_name
        self.success = success
        self.content = content
        self.raw = raw
        self.duration_ms = duration_ms
        self.error = error

    def to_dict(self):
        return {
            "agent": self.agent_name,
            "success": self.success,
            "content": self.content,
            "duration_ms": round(self.duration_ms, 2),
            "error": self.error,
        }


class BaseAgent:
    """
    Every specialized agent:
      - owns a dedicated system prompt (its "role")
      - maintains local context (the `context` dict passed per-call)
      - can call the shared LLM client
      - produces a structured AgentOutput
      - retries are handled by the orchestrator, not the agent itself
    """
    name: str = "base_agent"
    display_name: str = "Base Agent"
    system_prompt: str = "You are a helpful AI agent."
    temperature: float = 0.4

    async def run(self, task_description: str, context: dict | None = None) -> AgentOutput:
        context = context or {}
        start = time.time()
        user_prompt = self.build_prompt(task_description, context)
        try:
            raw = await gemini_client.generate(self.system_prompt, user_prompt, self.temperature)
            content = self.parse_output(raw)
            return AgentOutput(self.name, True, content, raw, (time.time() - start) * 1000)
        except Exception as e:  # noqa: BLE001
            logger.exception("Agent %s failed", self.name)
            return AgentOutput(self.name, False, "", "", (time.time() - start) * 1000, str(e))

    def build_prompt(self, task_description: str, context: dict) -> str:
        parts = [f"TASK:\n{task_description}"]
        if context.get("retrieved_context"):
            parts.append(f"\nRELEVANT CONTEXT (from memory/RAG):\n{context['retrieved_context']}")
        if context.get("previous_outputs"):
            parts.append(f"\nOUTPUTS FROM PRIOR AGENTS:\n{json.dumps(context['previous_outputs'], indent=2)[:4000]}")
        return "\n".join(parts)

    def parse_output(self, raw: str) -> str:
        """Override in subclasses that expect structured (e.g. JSON) output."""
        return raw.strip()
