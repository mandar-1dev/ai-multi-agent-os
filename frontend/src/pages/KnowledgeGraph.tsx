import { useCallback, useEffect, useState } from "react";
import ReactFlow, { Background, Controls, type Node, type Edge } from "reactflow";
import "reactflow/dist/style.css";
import { api } from "../api/client";
import { PageHeader, Panel, EmptyState } from "../components/ui";

const TYPE_COLORS: Record<string, string> = {
  technology: "#45e0c4",
  topic: "#7c8cf5",
  project: "#f5a524",
  person: "#f0556b",
  company: "#8891a3",
  task: "#45e0c4",
  agent: "#7c8cf5",
  document: "#f5a524",
  user: "#f0556b",
};

export default function KnowledgeGraph() {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [text, setText] = useState("");
  const [extracting, setExtracting] = useState(false);
  const [empty, setEmpty] = useState(false);

  const load = useCallback(async () => {
    const graph = await api.knowledgeGraph();
    setEmpty(graph.nodes.length === 0);
    const angleStep = (2 * Math.PI) / Math.max(graph.nodes.length, 1);
    setNodes(
      graph.nodes.map((n, i) => ({
        id: n.id,
        data: { label: n.label },
        position: {
          x: 400 + 260 * Math.cos(i * angleStep),
          y: 300 + 260 * Math.sin(i * angleStep),
        },
        style: {
          background: "#11151d",
          border: `1px solid ${TYPE_COLORS[n.type] || "#232a38"}`,
          color: "#e6e9ef",
          borderRadius: 8,
          fontSize: 12,
          padding: "6px 10px",
        },
      }))
    );
    setEdges(
      graph.edges.map((e, i) => ({
        id: `e${i}`,
        source: e.source,
        target: e.target,
        label: e.relation,
        style: { stroke: "#232a38" },
        labelStyle: { fill: "#8891a3", fontSize: 10 },
        animated: true,
      }))
    );
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function extract(e: React.FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;
    setExtracting(true);
    try {
      await api.extractGraph(text);
      setText("");
      await load();
    } finally {
      setExtracting(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      <PageHeader
        title="Knowledge Graph"
        subtitle="Entities and relationships extracted from tasks, documents, and conversations by the Reasoning Agent."
      />
      <div className="p-8 pb-0">
        <Panel className="p-4">
          <form onSubmit={extract} className="flex gap-2">
            <input
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste text to extract entities/relationships from…"
              className="flex-1 bg-panel-raised border border-border rounded-md px-3 py-2 text-sm outline-none focus:border-signal/50"
            />
            <button disabled={extracting} className="bg-signal text-bg rounded-md px-4 text-sm font-medium disabled:opacity-50">
              {extracting ? "Extracting…" : "Extract"}
            </button>
          </form>
        </Panel>
      </div>
      <div className="flex-1 m-8 mt-4 rounded-lg border border-border overflow-hidden bg-panel relative">
        {empty ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <EmptyState title="No graph data yet" description="Extract entities above, or run a few goals from Orchestrate — the graph grows automatically." />
          </div>
        ) : (
          <ReactFlow nodes={nodes} edges={edges} fitView>
            <Background color="#232a38" gap={20} />
            <Controls />
          </ReactFlow>
        )}
      </div>
    </div>
  );
}
