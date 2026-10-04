import type { ReactNode } from "react";

export function TooltipCard({ title, rows }: { title: ReactNode; rows: { label: string; value: ReactNode; color?: string }[] }) {
  return (
    <div className="min-w-40 rounded-lg border border-border bg-surface px-3 py-2 text-xs shadow-pop">
      <div className="mb-1.5 font-medium text-fg">{title}</div>
      {rows.map((r) => (
        <div key={r.label} className="flex items-center justify-between gap-4 py-0.5">
          <span className="flex items-center gap-1.5 text-fg-2">
            {r.color && <span className="size-2 rounded-sm" style={{ background: r.color }} aria-hidden />}
            {r.label}
          </span>
          <span className="tabular font-semibold text-fg">{r.value}</span>
        </div>
      ))}
    </div>
  );
}

export function Legend({ items }: { items: { label: string; color: string }[] }) {
  return (
    <div className="flex flex-wrap items-center gap-4 text-xs text-fg-2">
      {items.map((i) => (
        <span key={i.label} className="inline-flex items-center gap-1.5">
          <span className="h-0.5 w-3 rounded-full" style={{ background: i.color, height: 3 }} aria-hidden />
          {i.label}
        </span>
      ))}
    </div>
  );
}
