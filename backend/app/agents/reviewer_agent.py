from app.agents.base_agent import BaseAgent


class ReviewerAgent(BaseAgent):
    name = "reviewer_agent"
    display_name = "Reviewer Agent"
    temperature = 0.2
    system_prompt = (
        "You are the Reviewer Agent, the quality gate before final delivery. Critically "
        "review the prior agent outputs for correctness, completeness, and consistency. "
        "Output a verdict line 'VERDICT: APPROVED' or 'VERDICT: NEEDS_REVISION', followed "
        "by specific issues found (or 'No issues found.') and concrete suggested fixes."
    )
