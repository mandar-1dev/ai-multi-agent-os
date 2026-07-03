"""
Predefined workflow templates. Each step names the agent to run and a
prompt template; {goal} and {prev} are substituted at run time, where
{prev} is the previous step's output (empty for the first step).
"""

RESEARCH_WORKFLOW = {
    "name": "research_workflow",
    "steps": [
        {"step": "Research", "agent": "research_agent", "prompt": "Research the following topic in depth: {goal}"},
        {"step": "Summarization", "agent": "documentation_agent", "prompt": "Summarize this research clearly:\n{prev}"},
        {"step": "Fact Verification", "agent": "reviewer_agent", "prompt": "Fact-check and flag unsupported claims in this summary:\n{prev}"},
        {"step": "Final Report", "agent": "documentation_agent", "prompt": "Produce a final polished report for the goal '{goal}' using this verified content:\n{prev}"},
    ],
}

CODING_WORKFLOW = {
    "name": "coding_workflow",
    "steps": [
        {"step": "Requirement Analysis", "agent": "reasoning_agent", "prompt": "Analyze the requirements for: {goal}"},
        {"step": "Planning", "agent": "planner_agent", "prompt": "Plan the implementation steps for: {goal}"},
        {"step": "Code Generation", "agent": "coding_agent", "prompt": "Implement code for: {goal}\nPlan:\n{prev}"},
        {"step": "Code Review", "agent": "reviewer_agent", "prompt": "Review this code for bugs, style, and edge cases:\n{prev}"},
        {"step": "Documentation", "agent": "documentation_agent", "prompt": "Write documentation for this code:\n{prev}"},
        {"step": "Testing", "agent": "coding_agent", "prompt": "Write unit tests for this code:\n{prev}"},
    ],
}

LEARNING_WORKFLOW = {
    "name": "learning_workflow",
    "steps": [
        {"step": "Knowledge Extraction", "agent": "research_agent", "prompt": "Extract the key concepts and facts from this material: {goal}"},
        {"step": "Memory Storage", "agent": "memory_agent", "prompt": "Produce a memory-ready brief of these key concepts:\n{prev}"},
        {"step": "Quiz Generation", "agent": "reasoning_agent", "prompt": "Generate 5 quiz questions with answers testing understanding of:\n{prev}"},
        {"step": "Learning Recommendations", "agent": "documentation_agent", "prompt": "Recommend a study plan/next topics based on:\n{prev}"},
    ],
}

WORKFLOW_TEMPLATES = {
    w["name"]: w for w in [RESEARCH_WORKFLOW, CODING_WORKFLOW, LEARNING_WORKFLOW]
}
