import { AlertTriangle, CheckCircle2, CircleAlert, Info, XCircle } from "lucide-react";
import type { ReactNode } from "react";
import { Badge } from "@/components/ui/badge";
import type { Check, Priority, Status } from "@/lib/types";
import { cn, scoreTone, toneBg, toneLabel, toneText } from "@/lib/utils";

const STATUS: Record<Status, { icon: typeof CheckCircle2; cls: string; label: string }> = {
  pass: { icon: CheckCircle2, cls: "text-good", label: "Pass" },
  warn: { icon: AlertTriangle, cls: "text-warn", label: "Review" },
  fail: { icon: XCircle, cls: "text-bad", label: "Fail" },
};

export function StatusIcon({ status, className }: { status: Status; className?: string }) {
  const S = STATUS[status];
  return <S.icon className={cn("size-[18px] shrink-0", S.cls, className)} aria-label={S.label} />;
}

export function CheckRow({ check }: { check: Check }) {
  return (
    <li className="flex items-start gap-3 py-3">
      <StatusIcon status={check.status} className="mt-0.5" />
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm font-medium">{check.label}</span>
          <span className="text-[11px] uppercase tracking-wide text-fg-3">{check.impact} impact</span>
        </div>
        <p className="mt-0.5 break-words text-sm text-fg-2">{check.detail}</p>
      </div>
      <span className={cn("shrink-0 text-xs font-medium", STATUS[check.status].cls)}>{STATUS[check.status].label}</span>
    </li>
  );
}

const PRIORITY: Record<Priority, { variant: "bad" | "warn" | "accent" | "neutral"; label: string }> = {
  critical: { variant: "bad", label: "Critical" },
  high: { variant: "warn", label: "High" },
  medium: { variant: "accent", label: "Medium" },
  low: { variant: "neutral", label: "Low" },
};

export function PriorityBadge({ priority }: { priority: Priority }) {
  const p = PRIORITY[priority];
  return <Badge variant={p.variant}>{priority === "critical" && <CircleAlert aria-hidden />}{p.label}</Badge>;
}

export function ScorePill({ score, className }: { score: number; className?: string }) {
  const tone = scoreTone(score);
  return (
    <span className={cn("inline-flex items-center gap-1.5 rounded-md px-2 py-0.5 text-xs font-semibold tabular", toneBg[tone], toneText[tone], className)}>
      {score}<span className="font-medium opacity-80">· {toneLabel(score)}</span>
    </span>
  );
}

export function Stat({ label, value, hint, className }: { label: string; value: ReactNode; hint?: ReactNode; className?: string }) {
  return (
    <div className={cn("rounded-xl border border-border bg-surface p-4", className)}>
      <div className="text-xs font-medium text-fg-3">{label}</div>
      <div className="mt-1.5 tabular text-2xl font-semibold tracking-tight">{value}</div>
      {hint && <div className="mt-1 text-xs text-fg-3">{hint}</div>}
    </div>
  );
}

export function Chips({ items, variant = "neutral", empty }: { items: string[]; variant?: "neutral" | "good" | "bad" | "accent" | "warn" | "outline"; empty?: string }) {
  if (!items.length) return <p className="text-sm text-fg-3">{empty ?? "None"}</p>;
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.map((s) => <Badge key={s} variant={variant} className="px-2.5 py-1 text-[13px]">{s}</Badge>)}
    </div>
  );
}

export function Quote({ children, tone }: { children: ReactNode; tone?: "good" | "bad" }) {
  return (
    <blockquote className={cn("rounded-lg border-l-2 bg-surface-2 px-3.5 py-2.5 text-sm leading-relaxed text-fg-2",
      tone === "good" ? "border-good" : tone === "bad" ? "border-bad" : "border-border-strong")}>
      {children}
    </blockquote>
  );
}

export function Notes({ items }: { items: string[] }) {
  if (!items.length) return null;
  return (
    <ul className="space-y-2">
      {items.map((n) => (
        <li key={n} className="flex gap-2.5 text-sm text-fg-2">
          <Info className="mt-0.5 size-4 shrink-0 text-fg-3" aria-hidden />
          <span>{n}</span>
        </li>
      ))}
    </ul>
  );
}

export function SectionTitle({ children, aside }: { children: ReactNode; aside?: ReactNode }) {
  return (
    <div className="mb-3 flex items-center justify-between gap-3">
      <h4 className="text-xs font-semibold uppercase tracking-wider text-fg-3">{children}</h4>
      {aside}
    </div>
  );
}
