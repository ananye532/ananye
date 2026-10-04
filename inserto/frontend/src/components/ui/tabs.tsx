import { NavLink } from "react-router-dom";
import { cn } from "@/lib/utils";

export function TabNav({ items }: { items: { to: string; label: string; end?: boolean; badge?: string | number }[] }) {
  return (
    <nav className="-mx-4 overflow-x-auto px-4 sm:mx-0 sm:px-0" aria-label="Analysis sections">
      <div className="flex min-w-max gap-1 border-b border-border">
        {items.map((it) => (
          <NavLink key={it.to} to={it.to} end={it.end}
            className={({ isActive }) => cn(
              "relative -mb-px flex items-center gap-1.5 border-b-2 px-3 py-2.5 text-sm font-medium transition-colors",
              isActive ? "border-fg text-fg" : "border-transparent text-fg-3 hover:text-fg",
            )}>
            {it.label}
            {it.badge !== undefined && <span className="rounded-full bg-surface-2 px-1.5 text-[11px] tabular text-fg-2">{it.badge}</span>}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}

export function Segmented<T extends string>({ value, onChange, options, label }: {
  value: T; onChange: (v: T) => void; options: { value: T; label: string }[]; label: string;
}) {
  return (
    <div role="radiogroup" aria-label={label} className="inline-flex rounded-lg border border-border bg-surface-2 p-0.5">
      {options.map((o) => (
        <button key={o.value} role="radio" aria-checked={value === o.value} onClick={() => onChange(o.value)}
          className={cn("rounded-md px-3 py-1.5 text-[13px] font-medium transition",
            value === o.value ? "bg-surface text-fg shadow-card" : "text-fg-3 hover:text-fg")}>
          {o.label}
        </button>
      ))}
    </div>
  );
}
