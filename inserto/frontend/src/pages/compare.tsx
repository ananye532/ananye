import { ArrowDown, ArrowUp, GitCompareArrows, Minus, Trophy } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { Link } from "react-router-dom";
import { Chips, SectionTitle } from "@/components/analysis/primitives";
import { CompareBars } from "@/components/charts/compare-bars";
import { ScoreRing } from "@/components/charts/score-ring";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { Field, Select } from "@/components/ui/field";
import { EmptyState, PageHeader, Skeleton } from "@/components/ui/misc";
import { api } from "@/lib/api";
import { useAnalyses } from "@/lib/queries";
import type { AnalysisSummary } from "@/lib/types";
import { cn, formatDate } from "@/lib/utils";
import { ErrorPanel } from "./states";

function Delta({ v, invert = false }: { v: number | null; invert?: boolean }) {
  if (v === null || v === 0) return <span className="inline-flex items-center gap-1 text-fg-3"><Minus className="size-3.5" aria-hidden />0</span>;
  const good = invert ? v < 0 : v > 0;
  const Icon = v > 0 ? ArrowUp : ArrowDown;
  return <span className={cn("inline-flex items-center gap-0.5 tabular font-medium", good ? "text-good-fg" : "text-bad-fg")}><Icon className="size-3.5" aria-hidden />{Math.abs(v)}</span>;
}

const label = (a: AnalysisSummary) => `${a.resume_title} · ${a.job_title ?? "General"} · ${formatDate(a.created_at)}`;

export default function ComparePage() {
  const [params, setParams] = useSearchParams();
  const a = Number(params.get("a")) || 0;
  const b = Number(params.get("b")) || 0;
  const { data: list, isLoading } = useAnalyses({ limit: 200 });
  const cmp = useQuery({ queryKey: ["compare", a, b], queryFn: () => api.compare(a, b), enabled: a > 0 && b > 0 && a !== b });
  const set = (k: "a" | "b", v: string) => { const p = new URLSearchParams(params); v ? p.set(k, v) : p.delete(k); setParams(p, { replace: true }); };

  if (isLoading) return <Skeleton className="h-64 rounded-2xl" />;
  if ((list?.length ?? 0) < 2) {
    return (
      <>
        <PageHeader title="Compare analyses" description="Put two versions side by side." />
        <Card><EmptyState icon={<GitCompareArrows />} title="You need two analyses to compare" description="Analyze another version of your resume — or the same resume against a different job — then come back."
          action={<Link to="/app/new" className={buttonVariants()}>New analysis</Link>} /></Card>
      </>
    );
  }
  const c = cmp.data;
  return (
    <>
      <PageHeader title="Compare analyses" description="See exactly what changed between two versions or two job targets." />
      <Card>
        <CardBody className="grid gap-4 pt-5 md:grid-cols-2">
          <Field label={<span className="inline-flex items-center gap-2"><span className="size-2.5 rounded-sm" style={{ background: "var(--series-1)" }} />Version A</span>} htmlFor="cmp-a">
            <Select id="cmp-a" value={a || ""} onChange={(e) => set("a", e.target.value)}>
              <option value="">Choose…</option>{list!.map((x) => <option key={x.id} value={x.id} disabled={x.id === b}>{label(x)}</option>)}
            </Select>
          </Field>
          <Field label={<span className="inline-flex items-center gap-2"><span className="size-2.5 rounded-sm" style={{ background: "var(--series-2)" }} />Version B</span>} htmlFor="cmp-b">
            <Select id="cmp-b" value={b || ""} onChange={(e) => set("b", e.target.value)}>
              <option value="">Choose…</option>{list!.map((x) => <option key={x.id} value={x.id} disabled={x.id === a}>{label(x)}</option>)}
            </Select>
          </Field>
        </CardBody>
      </Card>

      {!(a && b) ? <p className="mt-8 text-center text-sm text-fg-3">Pick two analyses to compare.</p>
        : cmp.isLoading ? <Skeleton className="mt-6 h-80 rounded-2xl" />
        : cmp.error || !c ? <div className="mt-6"><ErrorPanel error={cmp.error} onRetry={() => cmp.refetch()} /></div> : (
          <div className="mt-6 space-y-6">
            <div className="grid gap-6 md:grid-cols-2">
              {(["a", "b"] as const).map((k) => (
                <Card key={k} className={cn("flex items-center gap-5 p-5", c.winner === k && "ring-2 ring-good/40")}>
                  <ScoreRing score={c[k].overall_score} size={96} stroke={9} label={`Version ${k.toUpperCase()} overall`} />
                  <div className="min-w-0">
                    <div className="text-xs font-medium uppercase tracking-wider text-fg-3">Version {k.toUpperCase()}</div>
                    <div className="mt-1 truncate font-semibold">{c[k].resume_title}</div>
                    <div className="truncate text-sm text-fg-3">{c[k].job_title ?? "General"} · {formatDate(c[k].created_at)}</div>
                    {c.winner === k && <div className="mt-2 inline-flex items-center gap-1.5 text-xs font-medium text-good-fg"><Trophy className="size-3.5" aria-hidden />Higher overall</div>}
                  </div>
                </Card>
              ))}
            </div>
            <Card>
              <CardHeader title="Dimension by dimension" />
              <CardBody>
                <CompareBars data={c.subscores} labelA="Version A" labelB="Version B" />
                <table className="mt-6 w-full text-sm">
                  <thead><tr className="border-b border-border text-left text-xs text-fg-3"><th className="py-2 font-medium">Dimension</th><th className="py-2 text-right font-medium">A</th><th className="py-2 text-right font-medium">B</th><th className="py-2 text-right font-medium">Change</th></tr></thead>
                  <tbody className="divide-y divide-border tabular">
                    {c.subscores.map((s) => <tr key={s.key}><td className="py-2.5">{s.label}</td><td className="py-2.5 text-right">{s.a ?? "—"}</td><td className="py-2.5 text-right">{s.b ?? "—"}</td><td className="py-2.5 text-right"><Delta v={s.delta} /></td></tr>)}
                    {c.metrics.map((m) => <tr key={m.label} className="text-fg-2"><td className="py-2.5">{m.label}</td><td className="py-2.5 text-right">{m.a}</td><td className="py-2.5 text-right">{m.b}</td><td className="py-2.5 text-right"><Delta v={m.delta} invert={m.label === "Recommendations"} /></td></tr>)}
                  </tbody>
                </table>
              </CardBody>
            </Card>
            <Card>
              <CardHeader title="Skills" />
              <CardBody className="grid gap-6 md:grid-cols-3">
                <div><SectionTitle>Only in A</SectionTitle><Chips items={c.skills_only_a} empty="—" /></div>
                <div><SectionTitle>Only in B</SectionTitle><Chips variant="accent" items={c.skills_only_b} empty="—" /></div>
                <div><SectionTitle>Shared ({c.skills_shared.length})</SectionTitle><Chips items={c.skills_shared} empty="—" /></div>
              </CardBody>
            </Card>
          </div>
        )}
    </>
  );
}
