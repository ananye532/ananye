import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Legend, TooltipCard } from "./chart-tooltip";

export function CompareBars({ data, labelA, labelB }: {
  data: { label: string; a: number | null; b: number | null }[]; labelA: string; labelB: string;
}) {
  return (
    <div>
      <div className="mb-3"><Legend items={[{ label: labelA, color: "var(--series-1)" }, { label: labelB, color: "var(--series-2)" }]} /></div>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -18 }} barGap={2} barCategoryGap="24%">
            <CartesianGrid stroke="var(--grid)" vertical={false} />
            <XAxis dataKey="label" tickLine={false} axisLine={{ stroke: "var(--axis)" }} tick={{ fill: "var(--fg-3)", fontSize: 11 }} interval={0} />
            <YAxis domain={[0, 100]} ticks={[0, 25, 50, 75, 100]} tickLine={false} axisLine={false} tick={{ fill: "var(--fg-3)", fontSize: 11 }} />
            <Tooltip cursor={{ fill: "var(--surface-2)" }}
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null;
                const p = payload[0]!.payload as (typeof data)[number];
                return <TooltipCard title={p.label} rows={[
                  { label: labelA, value: p.a ?? "—", color: "var(--series-1)" },
                  { label: labelB, value: p.b ?? "—", color: "var(--series-2)" },
                ]} />;
              }} />
            <Bar dataKey="a" fill="var(--series-1)" radius={[4, 4, 0, 0]} maxBarSize={22} />
            <Bar dataKey="b" fill="var(--series-2)" radius={[4, 4, 0, 0]} maxBarSize={22} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
