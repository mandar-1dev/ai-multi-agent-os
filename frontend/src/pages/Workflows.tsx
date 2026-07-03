import { useEffect, useState } from "react";
import { Play, Loader2 } from "lucide-react";
import { api } from "../api/client";
import { PageHeader, Panel, StatusPill, EmptyState } from "../components/ui";

export default function Workflows() {
  const [templates, setTemplates] = useState<any[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [goal, setGoal] = useState("");
  const [running, setRunning] = useState(false);
  const [history, setHistory] = useState<any[]>([]);
  const [lastResult, setLastResult] = useState<any>(null);

  async function loadAll() {
    const [t, h] = await Promise.all([api.workflowTemplates(), api.listWorkflows()]);
    setTemplates(t);
    setHistory(h);
    if (!selected && t[0]) setSelected(t[0].name);
  }

  useEffect(() => {
    loadAll();
  }, []);

  async function run(e: React.FormEvent) {
    e.preventDefault();
    if (!goal.trim() || !selected) return;
    setRunning(true);
    setLastResult(null);
    try {
      const result = await api.runWorkflow(selected, goal);
      setLastResult(result);
      loadAll();
    } finally {
      setRunning(false);
    }
  }

  const active = templates.find((t) => t.name === selected);

  return (
    <div>
      <PageHeader
        title="Workflows"
        subtitle="Predefined multi-step pipelines: Research, Coding, and Learning workflows chain specialist agents in a fixed sequence."
      />
      <div className="p-8 space-y-6">
        <Panel className="p-5">
          <form onSubmit={run} className="space-y-4">
            <div className="grid sm:grid-cols-3 gap-2">
              {templates.map((t) => (
                <button
                  type="button"
                  key={t.name}
                  onClick={() => setSelected(t.name)}
                  className={`text-left p-3 rounded-md border text-sm transition-colors ${
                    selected === t.name ? "border-signal/50 bg-signal/5" : "border-border bg-panel-raised/40"
                  }`}
                >
                  <div className="font-medium">{t.name.replace("_", " ")}</div>
                  <div className="text-[11px] text-text-dim mt-1">{t.steps.join(" → ")}</div>
                </button>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                placeholder={active ? `Goal for ${active.name.replace("_", " ")}…` : "Goal…"}
                className="flex-1 bg-panel-raised border border-border rounded-md px-4 py-2.5 text-sm outline-none focus:border-signal/50"
              />
              <button
                disabled={running}
                className="bg-signal text-bg rounded-md px-4 flex items-center gap-2 text-sm font-medium disabled:opacity-50"
              >
                {running ? <Loader2 size={15} className="animate-spin" /> : <Play size={15} />}
                Run
              </button>
            </div>
          </form>
        </Panel>

        {lastResult && (
          <Panel className="p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="text-[11px] uppercase tracking-widest text-text-dim">Result — {lastResult.name}</div>
              <StatusPill status={lastResult.status} />
            </div>
            <div className="space-y-2 mb-4">
              {lastResult.steps?.map((s: any, i: number) => (
                <div key={i} className="flex items-center justify-between text-sm px-3 py-2 bg-panel-raised/40 rounded">
                  <span>{s.step} <span className="text-text-dim font-mono text-xs">({s.agent})</span></span>
                  <StatusPill status={s.success ? "completed" : "failed"} />
                </div>
              ))}
            </div>
            <div className="text-[11px] uppercase tracking-widest text-text-dim mb-1">Final Output</div>
            <div className="text-sm whitespace-pre-wrap text-text-dim">{lastResult.final_output}</div>
          </Panel>
        )}

        <div>
          <div className="text-[11px] uppercase tracking-widest text-text-dim mb-2">History</div>
          {history.length === 0 ? (
            <EmptyState title="No workflow runs yet" />
          ) : (
            <Panel className="divide-y divide-border">
              {history.map((w) => (
                <div key={w.id} className="flex items-center justify-between px-4 py-2.5 text-sm">
                  <div>
                    <span className="font-mono text-xs text-text-dim">{w.name}</span>
                    <div>{w.goal}</div>
                  </div>
                  <StatusPill status={w.status} />
                </div>
              ))}
            </Panel>
          )}
        </div>
      </div>
    </div>
  );
}
