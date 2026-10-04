import { ArrowRight, History, Search } from "lucide-react";
import { useDeferredValue, useState } from "react";
import { Link } from "react-router-dom";
import { MiniScore } from "@/components/charts/score-ring";
import { buttonVariants } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/field";
import { EmptyState, PageHeader, Skeleton } from "@/components/ui/misc";
import { useAnalyses } from "@/lib/queries";
import { formatDateTime } from "@/lib/utils";
import { ErrorPanel } from "./states";

export default function HistoryPage() {
  const [q, setQ] = useState("");
  const dq = useDeferredValue(q.trim());
  const { data, isLoading, error, refetch } = useAnalyses({ q: dq || undefined, limit: 200 });

  return (
    <>
      <PageHeader title="Analysis history" description="Every analysis you’ve run, newest first."
        actions={<Link to="/app/compare" className={buttonVariants({ variant: "secondary" })}>Compare two</Link>} />
      <div className="relative mb-4 max-w-sm">
        <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-fg-3" aria-hidden />
        <Input placeholder="Search by resume or job title" className="pl-9" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search analyses" />
      </div>
      {isLoading ? <Skeleton className="h-80 rounded-2xl" /> : error ? <ErrorPanel error={error} onRetry={() => refetch()} /> : !data?.length ? (
        <Card>
          {dq ? <EmptyState icon={<Search />} title="No matches" description={`No analyses match “${dq}”.`} />
            : <EmptyState icon={<History />} title="No analyses yet" description="Run your first analysis to start building a history you can compare against."
                action={<Link to="/app/new" className={buttonVariants()}>New analysis</Link>} />}
        </Card>
      ) : (
        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-sm">
              <thead className="border-b border-border bg-surface-2/60 text-left text-xs text-fg-3">
                <tr><th className="px-5 py-3 font-medium">Resume</th><th className="px-3 py-3 font-medium">Target</th><th className="px-3 py-3 font-medium">Date</th>
                  <th className="px-3 py-3 text-right font-medium">Overall</th><th className="px-3 py-3 text-right font-medium">ATS</th><th className="px-3 py-3 text-right font-medium">Match</th><th className="w-10" /></tr>
              </thead>
              <tbody className="divide-y divide-border">
                {data.map((a) => (
                  <tr key={a.id} className="group hover:bg-surface-2/60">
                    <td className="px-5 py-3"><Link to={`/app/analyses/${a.id}`} className="font-medium group-hover:underline">{a.resume_title}</Link></td>
                    <td className="max-w-[220px] truncate px-3 py-3 text-fg-2">{a.job_title ?? a.target_role ?? "General"}</td>
                    <td className="whitespace-nowrap px-3 py-3 text-fg-3">{formatDateTime(a.created_at)}</td>
                    <td className="px-3 py-3 text-right"><MiniScore score={a.overall_score} /></td>
                    <td className="px-3 py-3 text-right tabular text-fg-2">{a.ats_score}</td>
                    <td className="px-3 py-3 text-right tabular text-fg-2">{a.match_score ?? "—"}</td>
                    <td className="pr-4"><Link to={`/app/analyses/${a.id}`} aria-label={`Open analysis of ${a.resume_title}`} className="text-fg-3 hover:text-fg"><ArrowRight className="size-4" /></Link></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </>
  );
}
