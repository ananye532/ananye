import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { TooltipCard } from "./chart-tooltip";

export function CategoryBars({ data }: { data: { category: string; count: number }[] }) {
  const height = Math.max(160, data.length * 34 + 20);
  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 28, bottom: 0, left: 0 }} barCategoryGap={8}>
          <CartesianGrid stroke="var(--grid)" horizontal={false} />
          <XAxis type="number" allowDecimals={false} tickLine={false} axisLine={false} tick={{ fill: "var(--fg-3)", fontSize: 11 }} />
          <YAxis type="category" dataKey="category" width={150} tickLine={false} axisLine={false} tick={{ fill: "var(--fg-2)", fontSize: 12 }} />
          <Tooltip cursor={{ fill: "var(--surface-2)" }}
            content={({ active, payload }) => active && payload?.length
              ? <TooltipCard title={(payload[0]!.payload as { category: string }).category} rows={[{ label: "Skills", value: payload[0]!.value as number, color: "var(--series-1)" }]} />
              : null} />
          <Bar dataKey="count" fill="var(--series-1)" radius={[0, 4, 4, 0]} maxBarSize={18}
            label={{ position: "right", fill: "var(--fg-2)", fontSize: 11 }} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
