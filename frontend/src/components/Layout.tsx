import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  LayoutGrid, MessagesSquare, ListTree, Workflow, Share2, Brain,
  FileStack, LogOut, Radio,
} from "lucide-react";
import { clearToken } from "../api/client";
import { useAgentSocket } from "../hooks/useAgentSocket";

const NAV = [
  { to: "/", label: "Overview", icon: LayoutGrid, end: true },
  { to: "/chat", label: "Orchestrate", icon: MessagesSquare },
  { to: "/tasks", label: "Tasks", icon: ListTree },
  { to: "/workflows", label: "Workflows", icon: Workflow },
  { to: "/knowledge-graph", label: "Knowledge Graph", icon: Share2 },
  { to: "/memory", label: "Memory", icon: Brain },
  { to: "/documents", label: "Documents", icon: FileStack },
];

export default function Layout() {
  const navigate = useNavigate();
  const { connected } = useAgentSocket();

  return (
    <div className="flex h-screen w-full bg-bg text-text">
      <aside className="w-60 shrink-0 border-r border-border bg-panel flex flex-col">
        <div className="px-5 py-5 border-b border-border">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-md bg-signal/10 border border-signal/30 flex items-center justify-center">
              <Share2 size={16} className="text-signal" />
            </div>
            <div>
              <div className="font-display font-semibold text-sm tracking-tight leading-none">AGENT&nbsp;OS</div>
              <div className="text-[10px] text-text-dim uppercase tracking-widest mt-0.5">Multi-Agent Console</div>
            </div>
          </div>
        </div>

        <nav className="flex-1 py-3 px-2 space-y-0.5">
          {NAV.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                  isActive
                    ? "bg-panel-raised text-text border border-border"
                    : "text-text-dim hover:text-text hover:bg-panel-raised/60"
                }`
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="px-3 py-3 border-t border-border space-y-2">
          <div className="flex items-center gap-2 px-2 text-xs text-text-dim">
            <Radio size={12} className={connected ? "text-signal" : "text-danger"} />
            {connected ? "Live feed connected" : "Reconnecting…"}
          </div>
          <button
            onClick={() => {
              clearToken();
              navigate("/login");
            }}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm text-text-dim hover:text-danger hover:bg-panel-raised/60 transition-colors"
          >
            <LogOut size={16} /> Sign out
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
