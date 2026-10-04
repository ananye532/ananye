import { ArrowRight, Eye, ThumbsDown, ThumbsUp } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { PriorityBadge, Quote, ScorePill, SectionTitle } from "@/components/analysis/primitives";
import { ScoreRing } from "@/components/charts/score-ring";
import { SubscoreBars } from "@/components/charts/subscore-bars";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { Progress } from "@/components/ui/misc";
import { useAnalysisContext } from "./layout";

const TAB_FOR: Record<string, string> = { ats: "ats", structure: "resume", impact: "content", skills: "skills", readability: "content", experience: "content", match: "match" };

export default function Overview() {
  const a = useAnalysisContext();
  const r = a.result;
  const nav = useNavigate();
  const ai = r.ai;

  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="flex flex-col items-center justify-center p-6 text-center">
          <ScoreRing score={r.overall.score} sublabel={`Grade ${r.overall.grade}`} label="Overall resume score" />
          <div className="mt-4 text-lg font-semibold tracking-tight">{r.overall.label}</div>
          <p className="mt-1 max-w-xs text-sm text-fg-2">{r.overall.summary}</p>
          {r.match && (
            <div className="mt-5 w-full rounded-xl border border-border bg-surface-2 p-3 text-left">
              <div className="flex items-center justify-between text-sm"><span className="font-medium">Job match</span><ScorePill score={r.match.score} /></div>
              <p className="mt-1 text-xs text-fg-3">{r.match.verdict}</p>
            </div>
          )}
        </Card>
        <Card className="lg:col-span-2">
          <CardHeader title="Score breakdown" description="Weighted dimensions. Select one to see the checks behind it." />
          <CardBody>
            <SubscoreBars items={r.subscores} onSelect={(k) => nav(`/app/analyses/${a.id}/${TAB_FOR[k] ?? ""}`)} />
            <div className="mt-5 flex flex-wrap gap-x-5 gap-y-1 text-xs text-fg-3">
              {r.subscores.map((s) => <span key={s.key} className="tabular">{s.label}: {Math.round(s.weight * 100)}% weight</span>)}
            </div>
          </CardBody>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <Card className="lg:col-span-3">
          <CardHeader title="Recruiter lens" description="What a screener likely takes away in a six-second skim." icon={<Eye />} />
          <CardBody className="space-y-5">
            <Quote>{ai?.first_impression ?? r.recruiter.first_impression}</Quote>
            <div>
              <SectionTitle>What they see first</SectionTitle>
              <ol className="space-y-1.5 text-sm">
                {r.recruiter.skim.map((s, i) => <li key={s} className="flex gap-3"><span className="w-4 tabular text-fg-3">{i + 1}</span><span className="text-fg">{s}</span></li>)}
              </ol>
            </div>
            <div className="grid gap-5 sm:grid-cols-2">
              <div>
                <SectionTitle>Strengths</SectionTitle>
                <ul className="space-y-2">
                  {(ai?.strengths.length ? ai.strengths : r.recruiter.strengths).map((s) => <li key={s} className="flex gap-2 text-sm text-fg-2"><ThumbsUp className="mt-0.5 size-4 shrink-0 text-good" aria-hidden />{s}</li>)}
                  {!r.recruiter.strengths.length && !ai?.strengths.length && <li className="text-sm text-fg-3">No standout strengths yet.</li>}
                </ul>
              </div>
              <div>
                <SectionTitle>Concerns</SectionTitle>
                <ul className="space-y-2">
                  {(ai?.concerns.length ? ai.concerns : r.recruiter.concerns).map((s) => <li key={s} className="flex gap-2 text-sm text-fg-2"><ThumbsDown className="mt-0.5 size-4 shrink-0 text-bad" aria-hidden />{s}</li>)}
                  {!r.recruiter.concerns.length && !ai?.concerns.length && <li className="text-sm text-fg-3">No major concerns.</li>}
                </ul>
              </div>
            </div>
            <div className="rounded-lg bg-surface-2 px-3.5 py-2.5 text-sm"><span className="font-medium">Verdict: </span><span className="text-fg-2">{r.recruiter.verdict}</span></div>
          </CardBody>
        </Card>
        <Card className="lg:col-span-2">
          <CardHeader title="Career insights" description={`Career level: ${r.insights.career_level}`} />
          <CardBody className="space-y-5">
            <div>
              <SectionTitle>Role fit</SectionTitle>
              <ul className="space-y-3">
                {r.insights.role_fits.map((f) => (
                  <li key={f.role}>
                    <div className="mb-1 flex justify-between text-sm"><span>{f.role}</span><span className="tabular font-medium">{f.fit}%</span></div>
                    <Progress value={f.fit} />
                  </li>
                ))}
              </ul>
              <p className="mt-2 text-xs text-fg-3">Share of each role profile’s core and common skills your resume shows.</p>
            </div>
            {r.insights.growth_skills.length > 0 && (
              <div>
                <SectionTitle>Skills to build{r.skills.target_role ? ` for ${r.skills.target_role}` : ""}</SectionTitle>
                <div className="flex flex-wrap gap-1.5">
                  {r.insights.growth_skills.map((g) => <Badge key={g.name} variant={g.importance === "core" ? "warn" : "neutral"}>{g.name}</Badge>)}
                </div>
              </div>
            )}
            {ai?.career_advice.length ? (
              <div><SectionTitle>Advice</SectionTitle><ul className="list-disc space-y-1 pl-4 text-sm text-fg-2">{ai.career_advice.map((c) => <li key={c}>{c}</li>)}</ul></div>
            ) : null}
          </CardBody>
        </Card>
      </div>

      <Card>
        <CardHeader title="Recommendations" description={`${r.recommendations.length} improvements, highest impact first.`}
          action={<Link to={`/app/analyses/${a.id}/studio`} className={buttonVariants({ variant: "secondary", size: "sm" })}>Open studio <ArrowRight /></Link>} />
        <CardBody>
          {r.recommendations.length ? (
            <ul className="divide-y divide-border">
              {r.recommendations.map((rec) => (
                <li key={rec.id} className="grid gap-3 py-4 first:pt-0 last:pb-0 sm:grid-cols-[96px_1fr]">
                  <div className="flex items-start gap-2 sm:flex-col"><PriorityBadge priority={rec.priority} /><span className="text-xs text-fg-3">{rec.category}</span></div>
                  <div className="min-w-0">
                    <div className="font-medium">{rec.title}</div>
                    <p className="mt-1 text-sm text-fg-2">{rec.detail}</p>
                    {rec.before && (
                      <div className="mt-3 grid gap-2 md:grid-cols-2">
                        <Quote tone="bad"><span className="mb-1 block text-[11px] font-semibold uppercase tracking-wider text-fg-3">Before</span>{rec.before}</Quote>
                        {rec.after && <Quote tone="good"><span className="mb-1 block text-[11px] font-semibold uppercase tracking-wider text-fg-3">After</span>{rec.after}</Quote>}
                      </div>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          ) : <p className="text-sm text-fg-3">No recommendations — this resume clears every check.</p>}
        </CardBody>
      </Card>
    </div>
  );
}
