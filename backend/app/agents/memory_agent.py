from app.agents.base_agent import BaseAgent


class MemoryAgent(BaseAgent):
    name = "memory_agent"
    display_name = "Memory Agent"
    temperature = 0.2
    system_prompt = (
        "You are the Memory Agent. Given retrieved long-term memory snippets and the "
        "current task, synthesize what is relevant, flag contradictions, and produce a "
        "concise 'memory brief' the other agents can use as grounding context. If nothing "
        "relevant is in memory, say so explicitly."
    )
