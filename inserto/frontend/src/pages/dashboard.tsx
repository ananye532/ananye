import { ArrowRight, ArrowUpRight, FileText, Plus, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";
import { PriorityBadge, Stat } from "@/components/analysis/primitives";
import { MiniScore, ScoreRing } from "@/components/charts/score-ring";
import { TrendChart } from "@/components/charts/trend-chart";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { EmptyState, PageHeader, Skeleton } from "@/components/ui/misc";
import { useAuth } from "@/lib/auth";
import { useDashboard } from "@/lib/queries";
import { cn, relativeTime, toneLabel } from "@/lib/utils";
import { ErrorPanel } from "./states";

function greeting() {
  const h = new Date().getHours();
  return h < 12 ? "Good morning" : h < 18 ? "Good afternoon" : "Good evening";
}

export default function DashboardPage() {
  const { user } = useAuth();
  const { data, isLoading, error, refetch } = useDashboard();
  const first = user?.name.split(" ")[0];

  const header = (
    <PageHeader title={`${greeting()}, ${first}`} description="Your resume performance at a glance."
      actions={<Link to="/app/new" className={buttonVariants()}><Plus />New analysis</Link>} />
  );

  if (isLoading) {
    return (
      <>
        {header}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{[0, 1, 2, 3].map((i) => <Skeleton key={i} className="h-24 rounded-xl" />)}</div>
        <div className="mt-6 grid gap-6 lg:grid-cols-3"><Skeleton className="h-80 rounded-2xl lg:col-span-2" /><Skeleton className="h-80 rounded-2xl" /></div>
      </>
    );
  }
  if (error || !data) return <>{header}<ErrorPanel error={error} onRetry={() => refetch()} /></>;

  if (!data.analysis_count) {
    return (
      <>
        {header}
        <Card>
          <EmptyState icon={<FileText />} title="Analyze your first resume"
            description="Upload a PDF or DOCX, or paste your resume. You’ll get an overall score, ATS checks, skill extraction and prioritized fixes."
            action={<Link to="/app/new" className={buttonVariants({ size: "lg" })}>Start an analysis <ArrowRight /></Link>} />
        </Card>
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          {[
            ["ATS checks", "Find formatting that makes parsers drop your data."],
            ["Job match", "Paste a posting to see missing skills and keywords."],
            ["Improvement studio", "Turn duty-based bullets into outcome-driven ones."],
          ].map(([t, d]) => (
            <div key={t} className="rounded-xl border border-dashed border-border-strong p-5">
              <div className="font-medium">{t}</div><p className="mt-1 text-sm text-fg-3">{d}</p>
            </div>
          ))}
        </div>
      </>
    );
  }

  const latest = data.latest!;
  const delta = data.trend.length >= 2 ? data.trend.at(-1)!.overall - data.trend.at(-2)!.overall : null;

  return (
    <>
      {header}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="Latest score" value={latest.overall_score}
          hint={delta === null ? toneLabel(latest.overall_score) : <span className={cn(delta >= 0 ? "text-good-fg" : "text-bad-fg")}>{delta >= 0 ? "+" : ""}{delta} vs previous</span>} />
        <Stat label="Best score" value={data.best_score ?? "—"} hint="Across all analyses" />
        <Stat label="Analyses" value={data.analysis_count} hint={`${data.resume_count} resume${data.resume_count === 1 ? "" : "s"}`} />
        <Stat label="Latest ATS" value={latest.ats_score} hint={toneLabel(latest.ats_score)} />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="Score trend" description="Overall and ATS scores across your last 20 analyses." />
          <CardBody>
            {data.trend.length >= 2 ? <TrendChart data={data.trend} />
              : <div className="grid h-56 place-items-center text-center text-sm text-fg-3">Run a second analysis to see your trend.<br />Tip: re-analyze after applying the top recommendations.</div>}
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="Latest analysis" description={relativeTime(latest.created_at)}
            action={<Link to={`/app/analyses/${latest.id}`} className={buttonVariants({ variant: "ghost", size: "sm" })}>Open <ArrowUpRight /></Link>} />
          <CardBody className="flex flex-col items-center text-center">
            <ScoreRing score={latest.overall_score} size={150} sublabel={toneLabel(latest.overall_score)} label="Latest overall score" />
            <div className="mt-4 font-medium">{latest.resume_title}</div>
            <div className="mt-0.5 text-sm text-fg-3">{latest.job_title ?? latest.target_role ?? "General analysis"}</div>
          </CardBody>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-5">
        <Card className="lg:col-span-3">
          <CardHeader title="Top priorities" description="From your latest analysis." icon={<Sparkles />}
            action={<Link to={`/app/analyses/${latest.id}/studio`} className={buttonVariants({ variant: "secondary", size: "sm" })}>Open studio</Link>} />
          <CardBody>
            {data.top_recommendations.length ? (
              <ul className="divide-y divide-border">
                {data.top_recommendations.map((r) => (
                  <li key={r.id} className="flex items-start gap-3 py-3 first:pt-0 last:pb-0">
                    <PriorityBadge priority={r.priority} />
                    <div className="min-w-0"><div className="text-sm font-medium">{r.title}</div><p className="mt-0.5 line-clamp-2 text-sm text-fg-3">{r.detail}</p></div>
                  </li>
                ))}
              </ul>
            ) : <p className="text-sm text-fg-3">Nothing urgent. Your latest resume clears every major check.</p>}
          </CardBody>
        </Card>
        <Card className="lg:col-span-2">
          <CardHeader title="Recent activity" action={<Link to="/app/history" className={buttonVariants({ variant: "ghost", size: "sm" })}>View all</Link>} />
          <CardBody className="pt-2">
            <ul className="divide-y divide-border">
              {data.recent.map((a) => (
                <li key={a.id}>
                  <Link to={`/app/analyses/${a.id}`} className="-mx-2 flex items-center justify-between gap-3 rounded-lg px-2 py-2.5 hover:bg-surface-2">
                    <div className="min-w-0">
                      <div className="truncate text-sm font-medium">{a.resume_title}</div>
                      <div className="truncate text-xs text-fg-3">{a.job_title ?? "General"} · {relativeTime(a.created_at)}</div>
                    </div>
                    <MiniScore score={a.overall_score} />
                  </Link>
                </li>
              ))}
            </ul>
          </CardBody>
        </Card>
      </div>
    </>
  );
}
