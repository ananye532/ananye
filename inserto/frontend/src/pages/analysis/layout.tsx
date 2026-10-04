import { ArrowLeft, Briefcase, Calendar, FileText, GitCompareArrows, Sparkles, Trash2 } from "lucide-react";
import { useState } from "react";
import { Link, Outlet, useLocation, useNavigate, useOutletContext, useParams } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { ConfirmDialog } from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/misc";
import { TabNav } from "@/components/ui/tabs";
import { ApiError, api } from "@/lib/api";
import { useAnalysis, useInvalidateWorkspace } from "@/lib/queries";
import { useToast } from "@/lib/toast";
import type { Analysis } from "@/lib/types";
import { formatDateTime } from "@/lib/utils";
import { ErrorPanel, NotFound } from "../states";

export function useAnalysisContext() {
  return useOutletContext<Analysis>();
}

export default function AnalysisLayout() {
  const id = Number(useParams().id);
  const { data, isLoading, error, refetch } = useAnalysis(id);
  const location = useLocation();
  const nav = useNavigate();
  const toast = useToast();
  const invalidate = useInvalidateWorkspace();
  const [confirm, setConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);

  if (isLoading) {
    return (
      <div>
        <Skeleton className="h-4 w-24" /><Skeleton className="mt-4 h-8 w-80" /><Skeleton className="mt-8 h-10 w-full" />
        <div className="mt-6 grid gap-6 lg:grid-cols-3"><Skeleton className="h-72 rounded-2xl" /><Skeleton className="h-72 rounded-2xl lg:col-span-2" /></div>
      </div>
    );
  }
  if (error instanceof ApiError && error.status === 404) return <NotFound inApp />;
  if (error || !data) return <ErrorPanel error={error} onRetry={() => refetch()} />;

  const r = data.result;
  const base = `/app/analyses/${id}`;
  const tabs = [
    { to: base, label: "Overview", end: true },
    { to: `${base}/resume`, label: "Parsed resume" },
    { to: `${base}/ats`, label: "ATS", badge: r.ats.checks.filter((c) => c.status !== "pass").length || undefined },
    { to: `${base}/skills`, label: "Skills & keywords" },
    { to: `${base}/content`, label: "Content" },
    { to: `${base}/match`, label: "Job match" },
    { to: `${base}/studio`, label: "Studio", badge: r.rewrites.length || undefined },
  ];

  async function remove() {
    setDeleting(true);
    try {
      await api.deleteAnalysis(id);
      await invalidate();
      toast({ kind: "success", title: "Analysis deleted" });
      nav("/app/history", { replace: true });
    } catch {
      toast({ kind: "error", title: "Couldn’t delete the analysis" });
      setDeleting(false);
    }
  }

  return (
    <div>
      <Link to="/app/history" className="inline-flex items-center gap-1.5 text-sm text-fg-3 hover:text-fg"><ArrowLeft className="size-4" />History</Link>
      <div className="mt-3 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <h1 className="truncate text-2xl font-semibold tracking-tight sm:text-[28px]">{data.resume_title}</h1>
          <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-sm text-fg-3">
            <span className="inline-flex items-center gap-1.5"><Calendar className="size-3.5" aria-hidden />{formatDateTime(data.created_at)}</span>
            {data.job_title && <span className="inline-flex items-center gap-1.5"><Briefcase className="size-3.5" aria-hidden />{data.job_title}</span>}
            {data.target_role && <span className="inline-flex items-center gap-1.5"><FileText className="size-3.5" aria-hidden />{data.target_role} profile</span>}
            {r.provider.ai_enhanced && <Badge variant="accent"><Sparkles aria-hidden />AI-enhanced</Badge>}
          </div>
        </div>
        <div className="flex shrink-0 gap-2">
          <Link to={`/app/compare?a=${id}`} className={buttonVariants({ variant: "secondary", size: "sm" })}><GitCompareArrows />Compare</Link>
          <Button variant="secondary" size="sm" onClick={() => setConfirm(true)} aria-label="Delete analysis"><Trash2 /></Button>
        </div>
      </div>
      {r.provider.note && <p className="mt-4 rounded-lg bg-warn-soft px-3 py-2 text-sm text-warn-fg">{r.provider.note}</p>}
      <div className="mt-6"><TabNav items={tabs} /></div>
      <div className="mt-6 animate-fade-up" key={location.pathname}><Outlet context={data} /></div>
      <p className="mt-10 text-xs leading-relaxed text-fg-3">{r.disclaimer} Engine v{r.engine_version}.</p>
      <ConfirmDialog open={confirm} title="Delete this analysis?" loading={deleting}
        description="The analysis will be removed from your history. The resume itself is kept." onConfirm={remove} onCancel={() => setConfirm(false)} />
    </div>
  );
}
