import { ArrowLeft, FileText, MoreHorizontal, Pencil, Play, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { MiniScore } from "@/components/charts/score-ring";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { ConfirmDialog } from "@/components/ui/dialog";
import { Input } from "@/components/ui/field";
import { EmptyState, PageHeader, Skeleton } from "@/components/ui/misc";
import { ApiError, api } from "@/lib/api";
import { useAnalyses, useAnalyze, useInvalidateWorkspace, useResume, useResumes } from "@/lib/queries";
import { useToast } from "@/lib/toast";
import type { Resume } from "@/lib/types";
import { formatDate, relativeTime } from "@/lib/utils";
import { ErrorPanel, NotFound } from "./states";

const SOURCE: Record<Resume["source"], string> = { pdf: "PDF", docx: "DOCX", txt: "TXT", paste: "Pasted" };

function ResumeRow({ r }: { r: Resume }) {
  const [menu, setMenu] = useState(false);
  const [confirm, setConfirm] = useState(false);
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(r.title);
  const invalidate = useInvalidateWorkspace();
  const toast = useToast();
  async function rename() {
    setEditing(false);
    if (!title.trim() || title === r.title) return setTitle(r.title);
    try { await api.renameResume(r.id, title.trim()); await invalidate(); } catch { setTitle(r.title); toast({ kind: "error", title: "Rename failed" }); }
  }
  async function remove() {
    try { await api.deleteResume(r.id); await invalidate(); toast({ kind: "success", title: "Resume deleted" }); }
    catch { toast({ kind: "error", title: "Delete failed" }); }
    setConfirm(false);
  }
  return (
    <li className="flex items-center gap-4 px-5 py-4">
      <div className="grid size-10 shrink-0 place-items-center rounded-lg border border-border bg-surface-2 text-fg-2"><FileText className="size-[18px]" aria-hidden /></div>
      <div className="min-w-0 flex-1">
        {editing ? (
          <Input autoFocus value={title} onChange={(e) => setTitle(e.target.value)} onBlur={rename} onKeyDown={(e) => e.key === "Enter" && rename()} className="h-8" aria-label="Resume name" />
        ) : (
          <Link to={`/app/resumes/${r.id}`} className="block truncate font-medium hover:underline">{title}</Link>
        )}
        <div className="mt-0.5 flex flex-wrap items-center gap-x-3 text-xs text-fg-3">
          <span>{SOURCE[r.source]}</span><span>{r.word_count} words</span><span>Added {relativeTime(r.created_at)}</span>
          <span>{r.analysis_count} analys{r.analysis_count === 1 ? "is" : "es"}</span>
        </div>
      </div>
      {r.latest_score !== null ? <MiniScore score={r.latest_score} /> : <Badge variant="outline">Not analyzed</Badge>}
      <div className="relative">
        <Button variant="ghost" size="icon" onClick={() => setMenu((m) => !m)} aria-label="Resume actions" aria-expanded={menu}><MoreHorizontal /></Button>
        {menu && (
          <div className="absolute right-0 top-10 z-10 w-40 animate-fade-up rounded-xl border border-border bg-surface p-1 shadow-pop" onMouseLeave={() => setMenu(false)} role="menu">
            <button role="menuitem" className="flex w-full items-center gap-2 rounded-md px-2.5 py-2 text-sm hover:bg-surface-2" onClick={() => { setEditing(true); setMenu(false); }}><Pencil className="size-4" />Rename</button>
            <button role="menuitem" className="flex w-full items-center gap-2 rounded-md px-2.5 py-2 text-sm text-bad-fg hover:bg-surface-2" onClick={() => { setConfirm(true); setMenu(false); }}><Trash2 className="size-4" />Delete</button>
          </div>
        )}
      </div>
      <ConfirmDialog open={confirm} title={`Delete “${r.title}”?`} description="This permanently deletes the resume and all of its analyses." onConfirm={remove} onCancel={() => setConfirm(false)} />
    </li>
  );
}

export function ResumesPage() {
  const { data, isLoading, error, refetch } = useResumes();
  return (
    <>
      <PageHeader title="Resumes" description="Every version you’ve uploaded. Open one to see exactly what the parser extracted."
        actions={<Link to="/app/new" className={buttonVariants()}><Plus />Add resume</Link>} />
      {isLoading ? <Skeleton className="h-64 rounded-2xl" /> : error ? <ErrorPanel error={error} onRetry={() => refetch()} /> : (
        <Card>
          {data?.length ? <ul className="divide-y divide-border">{data.map((r) => <ResumeRow key={r.id} r={r} />)}</ul>
            : <EmptyState icon={<FileText />} title="No resumes yet" description="Upload a PDF or DOCX, or paste your resume text."
                action={<Link to="/app/new" className={buttonVariants()}>Add your first resume</Link>} />}
        </Card>
      )}
    </>
  );
}

export function ResumeDetailPage() {
  const id = Number(useParams().id);
  const { data, isLoading, error, refetch } = useResume(id);
  const { data: analyses } = useAnalyses({ resume_id: id });
  const analyze = useAnalyze();
  const nav = useNavigate();
  const toast = useToast();
  if (isLoading) return <Skeleton className="h-96 rounded-2xl" />;
  if (error instanceof ApiError && error.status === 404) return <NotFound inApp />;
  if (error || !data) return <ErrorPanel error={error} onRetry={() => refetch()} />;

  return (
    <>
      <Link to="/app/resumes" className="inline-flex items-center gap-1.5 text-sm text-fg-3 hover:text-fg"><ArrowLeft className="size-4" />Resumes</Link>
      <div className="mt-3"><PageHeader title={data.title} description={`${SOURCE[data.source]}${data.filename ? ` · ${data.filename}` : ""} · added ${formatDate(data.created_at)}`}
        actions={<Button loading={analyze.isPending} onClick={() => analyze.mutate({ resume_id: id }, {
          onSuccess: (a) => nav(`/app/analyses/${a.id}`),
          onError: () => toast({ kind: "error", title: "Analysis failed" }),
        })}><Play />Analyze</Button>} /></div>
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader title="Extracted text" description="Exactly what Inserto (and most ATS) can read from your file." />
          <CardBody><pre className="max-h-[640px] overflow-auto whitespace-pre-wrap rounded-xl bg-surface-2 p-4 font-mono text-[12.5px] leading-relaxed text-fg-2">{data.text}</pre></CardBody>
        </Card>
        <Card>
          <CardHeader title="Analyses" />
          <CardBody>
            {analyses?.length ? (
              <ul className="divide-y divide-border">
                {analyses.map((a) => (
                  <li key={a.id}><Link to={`/app/analyses/${a.id}`} className="-mx-2 flex items-center justify-between rounded-lg px-2 py-2.5 hover:bg-surface-2">
                    <div className="min-w-0"><div className="truncate text-sm">{a.job_title ?? "General"}</div><div className="text-xs text-fg-3">{relativeTime(a.created_at)}</div></div>
                    <MiniScore score={a.overall_score} /></Link></li>
                ))}
              </ul>
            ) : <p className="text-sm text-fg-3">Not analyzed yet.</p>}
          </CardBody>
        </Card>
      </div>
    </>
  );
}
