import { useEffect, useState } from "react";
import { api } from "../api/client";
import { PageHeader, Panel, StatCard, StatusPill } from "../components/ui";
import { useAgentSocket } from "../hooks/useAgentSocket";

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [agents, setAgents] = useState<any[]>([]);
  const [runningAgents, setRunningAgents] = useState<Set<string>>(new Set());

  async function refresh() {
    const [s, a] = await Promise.all([api.dashboardStats(), api.agents()]);
    setStats(s);
    setAgents(a);
  }

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 6000);
    return () => clearInterval(t);
  }, []);

  useAgentSocket((e) => {
    if (e.type === "agent_started") setRunningAgents((prev) => new Set(prev).add(e.agent));
    if (e.type === "agent_completed" || e.type === "agent_failed") {
      setRunningAgents((prev) => {
        const next = new Set(prev);
        next.delete(e.agent);
        return next;
      });
      refresh();
    }
  });

  return (
    <div>
      <PageHeader
        title="System Overview"
        subtitle="Live status of the orchestrator, specialist agents, and knowledge stores."
      />
      <div className="p-8 space-y-8">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <StatCard label="Total Tasks" value={stats?.tasks?.total ?? "—"} />
          <StatCard label="Running" value={stats?.tasks?.running ?? "—"} />
          <StatCard label="Completed" value={stats?.tasks?.completed ?? "—"} />
          <StatCard label="Failed" value={stats?.tasks?.failed ?? "—"} />
          <StatCard label="Vector Entries" value={stats?.vector_entries ?? "—"} hint="Chunks + memories embedded" />
        </div>

        <div>
          <h2 className="font-display text-sm uppercase tracking-widest text-text-dim mb-3">Agent Fleet</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {agents.map((a) => {
              const isRunning = runningAgents.has(a.name);
              return (
                <Panel key={a.name} className={`p-4 ${isRunning ? "border-signal/50" : ""}`}>
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-medium text-sm">{a.display_name}</div>
                      <div className="text-[11px] text-text-dim font-mono mt-0.5">{a.name}</div>
                    </div>
                    <span className={`h-2 w-2 rounded-full mt-1 ${isRunning ? "bg-signal node-pulse" : "bg-border"}`} />
                  </div>
                  <div className="flex items-center justify-between mt-4 text-xs text-text-dim">
                    <span>{a.total_runs} runs</span>
                    <span>{a.avg_latency_ms ? `${a.avg_latency_ms}ms avg` : "—"}</span>
                  </div>
                  <div className="mt-2">
                    <StatusPill status={isRunning ? "running" : "idle"} />
                  </div>
                </Panel>
              );
            })}
          </div>
        </div>

        <div>
          <h2 className="font-display text-sm uppercase tracking-widest text-text-dim mb-3">Recent Execution Log</h2>
          <Panel className="divide-y divide-border">
            {(stats?.recent_logs ?? []).length === 0 && (
              <div className="p-4 text-text-dim text-sm">No executions yet — send a goal from Orchestrate to get started.</div>
            )}
            {(stats?.recent_logs ?? []).map((log: any, i: number) => (
              <div key={i} className="flex items-center justify-between px-4 py-2.5 text-sm">
                <span className="font-mono text-text-dim">{log.agent_name || "system"}</span>
                <StatusPill status={log.event} />
                <span className="text-text-dim text-xs">{new Date(log.timestamp).toLocaleTimeString()}</span>
              </div>
            ))}
          </Panel>
        </div>
      </div>
    </div>
  );
}
