import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Dashboard } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { Legend, TooltipCard } from "./chart-tooltip";

const SERIES = [
  { key: "overall", label: "Overall", color: "var(--series-1)" },
  { key: "ats", label: "ATS", color: "var(--series-2)" },
] as const;

export function TrendChart({ data }: { data: Dashboard["trend"] }) {
  const rows = data.map((d, i) => ({ ...d, idx: i + 1 }));
  return (
    <div>
      <div className="mb-3"><Legend items={SERIES.map((s) => ({ label: s.label, color: s.color }))} /></div>
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={rows} margin={{ top: 8, right: 12, bottom: 0, left: -18 }}>
            <CartesianGrid stroke="var(--grid)" strokeDasharray="0" vertical={false} />
            <XAxis dataKey="idx" tickLine={false} axisLine={{ stroke: "var(--axis)" }} tick={{ fill: "var(--fg-3)", fontSize: 11 }} tickFormatter={(v) => `#${v}`} />
            <YAxis domain={[0, 100]} ticks={[0, 25, 50, 75, 100]} tickLine={false} axisLine={false} tick={{ fill: "var(--fg-3)", fontSize: 11 }} />
            <Tooltip
              cursor={{ stroke: "var(--axis)", strokeWidth: 1 }}
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null;
                const p = payload[0]!.payload as (typeof rows)[number];
                return <TooltipCard title={<>{p.label}<span className="ml-1 font-normal text-fg-3">· {formatDate(p.date)}</span></>}
                  rows={SERIES.map((s) => ({ label: s.label, value: p[s.key], color: s.color }))} />;
              }}
            />
            {SERIES.map((s) => (
              <Line key={s.key} type="monotone" dataKey={s.key} stroke={s.color} strokeWidth={2}
                dot={{ r: 3, strokeWidth: 2, fill: "var(--surface)" }} activeDot={{ r: 5, strokeWidth: 2, stroke: "var(--surface)" }} isAnimationActive />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
