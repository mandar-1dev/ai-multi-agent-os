import { useState, useRef, useEffect } from "react";
import { Send, Loader2 } from "lucide-react";
import { api } from "../api/client";
import { PageHeader, Panel, StatusPill } from "../components/ui";
import { useAgentSocket, type AgentEvent } from "../hooks/useAgentSocket";

interface Run {
  goal: string;
  status: "planning" | "running" | "done" | "error";
  trace: AgentEvent[];
  result?: any;
}

export default function Chat() {
  const [goal, setGoal] = useState("");
  const [run, setRun] = useState<Run | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useAgentSocket((e) => {
    setRun((prev) => {
      if (!prev || prev.status === "done" || prev.status === "error") return prev;
      if (e.type === "plan_ready") return { ...prev, status: "running", trace: [...prev.trace, e] };
      return { ...prev, trace: [...prev.trace, e] };
    });
  });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [run?.trace.length]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!goal.trim()) return;
    setRun({ goal, status: "planning", trace: [] });
    try {
      const result = await api.chat(goal);
      setRun((prev) => (prev ? { ...prev, status: "done", result } : prev));
    } catch {
      setRun((prev) => (prev ? { ...prev, status: "error" } : prev));
    }
    setGoal("");
  }

  return (
    <div className="flex flex-col h-full">
      <PageHeader
        title="Orchestrate"
        subtitle="Describe a goal. The Planner Agent decomposes it, specialist agents execute in parallel where possible, and a Reviewer Agent checks the result."
      />

      <div className="flex-1 overflow-y-auto p-8 space-y-4">
        {!run && (
          <Panel className="p-6 text-sm text-text-dim">
            Try something like: <span className="text-text">"Research vector databases and write a short comparison of Chroma vs Pinecone"</span>
          </Panel>
        )}

        {run && (
          <div className="space-y-4">
            <Panel className="p-4">
              <div className="text-[11px] uppercase tracking-widest text-text-dim mb-1">Goal</div>
              <div className="text-sm">{run.goal}</div>
              <div className="mt-3"><StatusPill status={run.status === "done" ? "completed" : run.status === "error" ? "failed" : "running"} /></div>
            </Panel>

            <div>
              <div className="text-[11px] uppercase tracking-widest text-text-dim mb-2">Execution Trace</div>
              <div className="space-y-1.5">
                {run.trace.map((e, i) => (
                  <TraceLine key={i} event={e} />
                ))}
                {run.status !== "done" && run.status !== "error" && (
                  <div className="flex items-center gap-2 text-text-dim text-xs px-3 py-2">
                    <Loader2 size={12} className="animate-spin" /> working…
                  </div>
                )}
              </div>
            </div>

            {run.result && (
              <div className="grid md:grid-cols-2 gap-4">
                <Panel className="p-4">
                  <div className="text-[11px] uppercase tracking-widest text-text-dim mb-2">Summary</div>
                  <div className="text-sm whitespace-pre-wrap leading-relaxed">{run.result.summary}</div>
                </Panel>
                <Panel className="p-4">
                  <div className="text-[11px] uppercase tracking-widest text-text-dim mb-2">Reviewer Verdict</div>
                  <div className="text-sm whitespace-pre-wrap leading-relaxed">{run.result.review}</div>
                </Panel>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <form onSubmit={submit} className="border-t border-border p-4 flex gap-2">
        <input
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="Describe a goal for the agent fleet…"
          className="flex-1 bg-panel-raised border border-border rounded-md px-4 py-2.5 text-sm outline-none focus:border-signal/50"
        />
        <button
          type="submit"
          className="bg-signal text-bg rounded-md px-4 flex items-center gap-2 text-sm font-medium disabled:opacity-50"
          disabled={run?.status === "planning" || run?.status === "running"}
        >
          <Send size={15} /> Send
        </button>
      </form>
    </div>
  );
}

function TraceLine({ event }: { event: AgentEvent }) {
  const label: Record<string, string> = {
    orchestrator_started: "Orchestrator received goal",
    plan_ready: `Planner produced ${event.subtasks?.length ?? 0} subtasks`,
    batch_started: `Batch started: ${event.tasks?.join(", ")}`,
    agent_started: `${event.agent} started — ${event.title ?? ""}`,
    agent_completed: `${event.agent} completed`,
    agent_retry: `${event.agent} retrying (attempt ${event.attempt})`,
    agent_failed: `${event.agent} failed — ${event.error ?? ""}`,
    orchestrator_completed: "Orchestrator finished",
  };
  const tone =
    event.type === "agent_failed" ? "text-danger" :
    event.type === "agent_completed" ? "text-signal" :
    event.type === "agent_retry" ? "text-warn" : "text-text-dim";

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-panel border border-border rounded-md text-xs font-mono">
      <span className={`h-1.5 w-1.5 rounded-full bg-current ${tone}`} />
      <span className={tone}>{label[event.type] || event.type}</span>
    </div>
  );
}
