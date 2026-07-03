import { useEffect, useState } from "react";
import { api } from "../api/client";
import { PageHeader, Panel, StatusPill, EmptyState } from "../components/ui";

export default function Tasks() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [filter, setFilter] = useState<string>("");
  const [expanded, setExpanded] = useState<string | null>(null);

  async function load() {
    setTasks(await api.tasks(filter || undefined));
  }

  useEffect(() => {
    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, [filter]);

  return (
    <div>
      <PageHeader
        title="Tasks"
        subtitle="Every subtask created by the orchestrator, with its assigned agent, status, and result."
        action={
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-panel-raised border border-border rounded-md px-3 py-1.5 text-sm"
          >
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="running">Running</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
        }
      />
      <div className="p-8">
        {tasks.length === 0 ? (
          <EmptyState title="No tasks yet" description="Send a goal from Orchestrate to generate subtasks here." />
        ) : (
          <Panel className="divide-y divide-border">
            {tasks.map((t) => (
              <div key={t.id}>
                <button
                  onClick={() => setExpanded(expanded === t.id ? null : t.id)}
                  className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-panel-raised/50"
                >
                  <div>
                    <div className="text-sm">{t.title}</div>
                    <div className="text-[11px] font-mono text-text-dim mt-0.5">{t.assigned_agent} · {t.task_type}</div>
                  </div>
                  <StatusPill status={t.status} />
                </button>
                {expanded === t.id && (
                  <div className="px-4 pb-4 text-sm text-text-dim whitespace-pre-wrap bg-panel-raised/30">
                    {t.result || t.error || "No output yet."}
                  </div>
                )}
              </div>
            ))}
          </Panel>
        )}
      </div>
    </div>
  );
}
