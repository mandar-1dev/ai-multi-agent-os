import json
import re
from app.agents.base_agent import BaseAgent
from app.tools.registry import get_tool, list_tools


class ToolExecutionAgent(BaseAgent):
    """
    Decides which registered tool(s) to call for a task, then actually
    executes them and returns the structured tool result. This is the
    bridge between free-text agent reasoning and deterministic tool calls.
    """
    name = "tool_execution_agent"
    display_name = "Tool Execution Agent"
    temperature = 0.0

    @property
    def system_prompt(self) -> str:
        tools_desc = "\n".join(f"- {t['name']}: {t['description']}" for t in list_tools())
        return (
            "You are the Tool Execution Agent. Given a task, choose the single best tool "
            f"from this list and the arguments to call it with:\n{tools_desc}\n\n"
            'Respond with ONLY JSON, no prose: {"tool": "<name>", "arguments": {...}}. '
            'If no tool applies, respond {"tool": null, "arguments": {}}.'
        )

    async def run(self, task_description: str, context: dict | None = None):
        decision_output = await super().run(task_description, context)
        if not decision_output.success:
            return decision_output

        cleaned = re.sub(r"```json|```", "", decision_output.raw).strip()
        try:
            decision = json.loads(cleaned)
        except Exception:
            decision_output.content = "No valid tool call produced."
            return decision_output

        tool_name = decision.get("tool")
        if not tool_name:
            decision_output.content = "No tool required for this task."
            return decision_output

        try:
            tool = get_tool(tool_name)
            result = tool.run(**decision.get("arguments", {}))
            decision_output.content = json.dumps({"tool": tool_name, "result": result.to_dict()})
        except Exception as e:  # noqa: BLE001
            decision_output.content = json.dumps({"tool": tool_name, "error": str(e)})
        return decision_output
