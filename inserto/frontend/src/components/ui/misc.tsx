import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Skeleton({ className, ...p }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-shimmer rounded-md bg-surface-2", className)}
      style={{ backgroundImage: "linear-gradient(90deg, transparent, var(--surface-3), transparent)", backgroundSize: "400px 100%", backgroundRepeat: "no-repeat" }}
      {...p}
    />
  );
}

export function Progress({ value, className, tone }: { value: number; className?: string; tone?: string }) {
  const v = Math.max(0, Math.min(100, value));
  return (
    <div className={cn("h-1.5 w-full overflow-hidden rounded-full bg-surface-3", className)} role="progressbar" aria-valuenow={v} aria-valuemin={0} aria-valuemax={100}>
      <div className="h-full rounded-full transition-[width] duration-700 ease-out" style={{ width: `${v}%`, background: tone ?? "var(--series-1)" }} />
    </div>
  );
}

export function Separator({ className }: { className?: string }) {
  return <div role="separator" className={cn("h-px w-full bg-border", className)} />;
}

export function Kbd({ children }: { children: ReactNode }) {
  return <kbd className="rounded border border-border bg-surface-2 px-1.5 py-0.5 font-mono text-[11px] text-fg-2">{children}</kbd>;
}

export function Switch({ checked, onChange, id, label }: { checked: boolean; onChange: (v: boolean) => void; id: string; label: string }) {
  return (
    <button id={id} role="switch" aria-checked={checked} aria-label={label} onClick={() => onChange(!checked)}
      className={cn("relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors", checked ? "bg-accent" : "bg-surface-3 ring-1 ring-inset ring-border-strong")}>
      <span className={cn("inline-block size-4 rounded-full bg-white shadow transition-transform", checked ? "translate-x-[18px]" : "translate-x-0.5")} />
    </button>
  );
}

export function EmptyState({ icon, title, description, action, className }: {
  icon: ReactNode; title: string; description: ReactNode; action?: ReactNode; className?: string;
}) {
  return (
    <div className={cn("flex flex-col items-center justify-center px-6 py-14 text-center", className)}>
      <div className="relative mb-5">
        <div className="absolute inset-0 -m-3 rounded-full bg-accent-soft blur-xl" aria-hidden />
        <div className="relative grid size-12 place-items-center rounded-2xl border border-border bg-surface text-fg-2 shadow-card [&_svg]:size-5">{icon}</div>
      </div>
      <h3 className="text-base font-semibold tracking-tight">{title}</h3>
      <p className="mt-1.5 max-w-sm text-sm text-fg-3">{description}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

export function PageHeader({ title, description, actions, eyebrow }: { title: ReactNode; description?: ReactNode; actions?: ReactNode; eyebrow?: ReactNode }) {
  return (
    <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div className="min-w-0">
        {eyebrow && <div className="mb-2 text-xs font-medium uppercase tracking-wider text-fg-3">{eyebrow}</div>}
        <h1 className="text-2xl font-semibold tracking-tight sm:text-[28px]">{title}</h1>
        {description && <p className="mt-1.5 max-w-2xl text-[15px] text-fg-2">{description}</p>}
      </div>
      {actions && <div className="flex shrink-0 flex-wrap items-center gap-2">{actions}</div>}
    </div>
  );
}
