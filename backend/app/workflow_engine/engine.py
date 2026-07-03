import datetime as dt
from sqlalchemy.orm import Session
from app.workflow_engine.workflows import WORKFLOW_TEMPLATES
from app.agents.registry import get_agent
from app.models.workflow import Workflow
from app.models.execution_log import ExecutionLog


class WorkflowEngine:
    def list_templates(self) -> list[dict]:
        return [
            {"name": w["name"], "steps": [s["step"] for s in w["steps"]]}
            for w in WORKFLOW_TEMPLATES.values()
        ]

    async def run(self, db: Session, workflow_name: str, goal: str, user_id: str | None = None,
                   on_event=None) -> Workflow:
        template = WORKFLOW_TEMPLATES.get(workflow_name)
        if not template:
            raise KeyError(f"Unknown workflow '{workflow_name}'. Available: {list(WORKFLOW_TEMPLATES.keys())}")

        row = Workflow(user_id=user_id, name=workflow_name, goal=goal, status="running", steps=[])
        db.add(row)
        db.commit()
        db.refresh(row)

        prev_output = ""
        step_records = []
        for step_def in template["steps"]:
            agent = get_agent(step_def["agent"])
            prompt = step_def["prompt"].format(goal=goal, prev=prev_output or "(none yet)")

            if on_event:
                await on_event({"type": "workflow_step_started", "workflow_id": row.id, "step": step_def["step"], "agent": agent.name})

            output = await agent.run(prompt, {})
            step_records.append({
                "step": step_def["step"], "agent": agent.name,
                "success": output.success, "output": output.content, "error": output.error,
            })
            db.add(ExecutionLog(
                workflow_id=row.id, agent_name=agent.name, event="completed" if output.success else "failed",
                detail=output.content[:2000] if output.success else output.error,
            ))
            db.commit()

            if on_event:
                await on_event({"type": "workflow_step_completed", "workflow_id": row.id, "step": step_def["step"], "success": output.success})

            prev_output = output.content if output.success else prev_output

        row.steps = step_records
        row.final_output = prev_output
        row.status = "completed" if all(s["success"] for s in step_records) else "failed"
        row.completed_at = dt.datetime.utcnow()
        db.commit()
        db.refresh(row)

        if on_event:
            await on_event({"type": "workflow_completed", "workflow_id": row.id, "status": row.status})

        return row


workflow_engine = WorkflowEngine()
