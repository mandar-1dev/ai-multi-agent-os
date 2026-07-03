import { useEffect, useState } from "react";
import { Search } from "lucide-react";
import { api } from "../api/client";
import { PageHeader, Panel, EmptyState } from "../components/ui";

const TYPES = ["conversation", "task", "preference", "project", "semantic", "knowledge"];

export default function Memory() {
  const [items, setItems] = useState<any[]>([]);
  const [type, setType] = useState("");
  const [query, setQuery] = useState("");
  const [searching, setSearching] = useState(false);

  async function load() {
    setItems(await api.recentMemory(type || undefined));
  }

  useEffect(() => {
    load();
  }, [type]);

  async function search(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return load();
    setSearching(true);
    try {
      const results = await api.recallMemory(query, type || undefined);
      setItems(results.map((r: any) => ({ content: r.content, memory_type: r.metadata?.memory_type, created_at: null })));
    } finally {
      setSearching(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Long-Term Memory"
        subtitle="Conversation, task, preference, project, semantic, and knowledge memory — vector-searchable across every agent."
      />
      <div className="p-8 space-y-4">
        <div className="flex gap-2">
          <form onSubmit={search} className="flex-1 flex gap-2">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Semantic search over memory…"
              className="flex-1 bg-panel-raised border border-border rounded-md px-4 py-2.5 text-sm outline-none focus:border-signal/50"
            />
            <button className="bg-signal text-bg rounded-md px-4 flex items-center gap-2 text-sm font-medium">
              <Search size={15} /> {searching ? "Searching…" : "Search"}
            </button>
          </form>
          <select
            value={type}
            onChange={(e) => setType(e.target.value)}
            className="bg-panel-raised border border-border rounded-md px-3 py-1.5 text-sm"
          >
            <option value="">All types</option>
            {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>

        {items.length === 0 ? (
          <EmptyState title="No memories yet" description="Memory fills up as the orchestrator runs goals and stores summaries." />
        ) : (
          <Panel className="divide-y divide-border">
            {items.map((m, i) => (
              <div key={i} className="px-4 py-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[11px] font-mono uppercase text-text-dim">{m.memory_type}</span>
                  {m.created_at && <span className="text-[11px] text-text-dim">{new Date(m.created_at).toLocaleString()}</span>}
                </div>
                <div className="text-sm text-text-dim whitespace-pre-wrap">{m.content}</div>
              </div>
            ))}
          </Panel>
        )}
      </div>
    </div>
  );
}
