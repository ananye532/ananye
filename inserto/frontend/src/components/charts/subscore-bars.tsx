import type { Subscore } from "@/lib/types";
import { cn } from "@/lib/utils";

/** Horizontal magnitude bars, one series color; values labeled directly. */
export function SubscoreBars({ items, className, onSelect }: { items: Subscore[]; className?: string; onSelect?: (key: string) => void }) {
  return (
    <ul className={cn("space-y-3.5", className)}>
      {items.map((s) => (
        <li key={s.key}>
          <button type="button" onClick={() => onSelect?.(s.key)} disabled={!onSelect}
            className="group block w-full text-left disabled:cursor-default" title={s.description}>
            <div className="mb-1.5 flex items-baseline justify-between gap-3">
              <span className="text-sm font-medium text-fg group-enabled:group-hover:underline">{s.label}</span>
              <span className="tabular text-sm font-semibold text-fg">{s.score}<span className="font-normal text-fg-3">/100</span></span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-surface-3">
              <div className="h-full rounded-full transition-[width] duration-700 ease-out" style={{ width: `${s.score}%`, background: "var(--series-1)" }} />
            </div>
          </button>
        </li>
      ))}
    </ul>
  );
}
