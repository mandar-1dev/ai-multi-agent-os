import type { ReactNode } from "react";

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
  return (
    <div className="flex items-start justify-between px-8 pt-8 pb-6 border-b border-border">
      <div>
        <h1 className="font-display text-2xl font-semibold tracking-tight">{title}</h1>
        {subtitle && <p className="text-text-dim text-sm mt-1 max-w-xl">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

export function Panel({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`bg-panel border border-border rounded-lg ${className}`}>
      {children}
    </div>
  );
}

export function StatCard({ label, value, hint }: { label: string; value: string | number; hint?: string }) {
  return (
    <Panel className="p-4">
      <div className="text-[11px] uppercase tracking-widest text-text-dim">{label}</div>
      <div className="font-display text-3xl font-semibold mt-2">{value}</div>
      {hint && <div className="text-xs text-text-dim mt-1">{hint}</div>}
    </Panel>
  );
}

const STATUS_STYLES: Record<string, string> = {
  idle: "text-text-dim border-border bg-panel-raised",
  pending: "text-text-dim border-border bg-panel-raised",
  running: "text-warn border-warn/40 bg-warn/10",
  completed: "text-signal border-signal/40 bg-signal/10",
  approved: "text-signal border-signal/40 bg-signal/10",
  failed: "text-danger border-danger/40 bg-danger/10",
  error: "text-danger border-danger/40 bg-danger/10",
};

export function StatusPill({ status }: { status: string }) {
  const cls = STATUS_STYLES[status?.toLowerCase()] || STATUS_STYLES.idle;
  return (
    <span className={`inline-flex items-center gap-1.5 text-[11px] font-mono uppercase tracking-wide px-2 py-0.5 rounded border ${cls}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {status}
    </span>
  );
}

export function EmptyState({ title, description }: { title: string; description?: string }) {
  return (
    <div className="text-center py-16 text-text-dim">
      <p className="font-display text-lg text-text">{title}</p>
      {description && <p className="text-sm mt-1 max-w-md mx-auto">{description}</p>}
    </div>
  );
}
