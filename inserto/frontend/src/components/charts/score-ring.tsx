import { cn, scoreTone, toneLabel, toneVar } from "@/lib/utils";

/** A single headline score: the number is the chart; the ring adds glanceable status. */
export function ScoreRing({ score, size = 168, stroke = 12, label, sublabel, className }: {
  score: number; size?: number; stroke?: number; label?: string; sublabel?: string; className?: string;
}) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const tone = scoreTone(score);
  const offset = c * (1 - Math.max(0, Math.min(100, score)) / 100);
  return (
    <div className={cn("relative inline-grid place-items-center", className)} style={{ width: size, height: size }}
      role="img" aria-label={`${label ?? "Score"}: ${score} out of 100, ${toneLabel(score)}`}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--surface-3)" strokeWidth={stroke} />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={toneVar[tone]} strokeWidth={stroke} strokeLinecap="round"
          strokeDasharray={c} strokeDashoffset={offset} style={{ transition: "stroke-dashoffset 900ms cubic-bezier(.2,.7,.2,1)" }} />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="tabular font-semibold tracking-tight" style={{ fontSize: size * 0.3, lineHeight: 1 }}>{score}</span>
        {sublabel && <span className="mt-1.5 text-xs font-medium text-fg-3">{sublabel}</span>}
      </div>
    </div>
  );
}

export function MiniScore({ score, className }: { score: number; className?: string }) {
  const tone = scoreTone(score);
  return (
    <span className={cn("inline-flex items-center gap-1.5 tabular text-sm font-semibold", className)}>
      <span className="size-2 rounded-full" style={{ background: toneVar[tone] }} aria-hidden />
      {score}
    </span>
  );
}
