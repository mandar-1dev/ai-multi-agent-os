from app.agents.base_agent import BaseAgent


class ReasoningAgent(BaseAgent):
    name = "reasoning_agent"
    display_name = "Reasoning Agent"
    temperature = 0.3
    system_prompt = (
        "You are the Reasoning Agent. Perform careful multi-step reasoning over the task "
        "and any provided context/prior agent outputs. Show your key inference steps "
        "briefly, then give a clear final conclusion or answer under a 'CONCLUSION:' label."
    )
