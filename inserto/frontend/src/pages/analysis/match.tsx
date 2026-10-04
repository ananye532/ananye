import { ArrowRight, Briefcase, CheckCircle2, CircleDashed, XCircle } from "lucide-react";
import { Link } from "react-router-dom";
import { Chips, Quote, SectionTitle, Stat } from "@/components/analysis/primitives";
import { ScoreRing } from "@/components/charts/score-ring";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/misc";
import { useAnalysisContext } from "./layout";

const MET = {
  met: { icon: CheckCircle2, cls: "text-good", label: "Met" },
  partial: { icon: CircleDashed, cls: "text-warn", label: "Partial" },
  missing: { icon: XCircle, cls: "text-bad", label: "Missing" },
};

export default function MatchTab() {
  const a = useAnalysisContext();
  const m = a.result.match;
  if (!m) {
    return (
      <Card>
        <EmptyState icon={<Briefcase />} title="No job description on this analysis"
          description="Match this resume against a specific posting to see missing skills, keyword coverage and requirement-level evidence."
          action={<Link to="/app/match" className={buttonVariants()}>Open job matcher <ArrowRight /></Link>} />
      </Card>
    );
  }
  const counts = { met: 0, partial: 0, missing: 0 };
  m.requirements.forEach((r) => counts[r.met]++);
  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="flex flex-col items-center p-6 text-center">
          <ScoreRing score={m.score} size={150} sublabel="Job fit" label="Job match score" />
          <div className="mt-4 font-semibold">{m.job_title ?? "This role"}</div>
          <p className="mt-1 text-sm text-fg-2">{m.verdict}</p>
        </Card>
        <div className="grid gap-4 sm:grid-cols-2 lg:col-span-2">
          <Stat label="Skill coverage" value={`${m.skill_score}%`} hint={`${m.matched_skills.length} of ${m.matched_skills.length + m.missing_skills.length} skills in the posting`} />
          <Stat label="Keyword coverage" value={`${m.keyword_score}%`} hint={`${m.matched_keywords.length} of ${m.matched_keywords.length + m.missing_keywords.length} top terms`} />
          <Stat label="Requirements" value={`${counts.met}/${m.requirements.length}`} hint={`${counts.partial} partial · ${counts.missing} missing`} />
          <Stat label="Experience" value={`${m.years_found} yrs`} hint={m.years_required ? `${m.years_required}+ requested` : "No minimum stated"} />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Skills" />
          <CardBody className="space-y-5">
            <div><SectionTitle>Missing</SectionTitle><Chips variant="bad" items={m.missing_skills} empty="You cover every skill the posting names." /></div>
            <div><SectionTitle>Matched</SectionTitle><Chips variant="good" items={m.matched_skills} empty="No overlap yet." /></div>
            <div><SectionTitle>Your extra strengths</SectionTitle><Chips items={m.extra_skills} empty="—" /></div>
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="Keywords" description="Most frequent terms in the posting." />
          <CardBody className="space-y-5">
            <div><SectionTitle>Not in your resume</SectionTitle><Chips variant="bad" items={m.missing_keywords} empty="Full coverage." /></div>
            <div><SectionTitle>Covered</SectionTitle><Chips variant="good" items={m.matched_keywords} /></div>
          </CardBody>
        </Card>
      </div>

      <Card>
        <CardHeader title="Requirement-by-requirement" description="Each requirement line from the posting, with the closest supporting bullet from your resume." />
        <CardBody>
          {m.requirements.length ? (
            <ul className="divide-y divide-border">
              {m.requirements.map((req) => {
                const s = MET[req.met];
                return (
                  <li key={req.text} className="grid gap-3 py-4 first:pt-0 last:pb-0 md:grid-cols-2">
                    <div className="flex gap-3">
                      <s.icon className={`mt-0.5 size-[18px] shrink-0 ${s.cls}`} aria-label={s.label} />
                      <div><div className="text-sm font-medium">{req.text}</div><div className={`mt-0.5 text-xs ${s.cls}`}>{s.label}</div></div>
                    </div>
                    {req.evidence ? <Quote>{req.evidence}</Quote> : <p className="self-center text-sm text-fg-3">No supporting bullet found.</p>}
                  </li>
                );
              })}
            </ul>
          ) : <p className="text-sm text-fg-3">No requirement lines were detected in the posting.</p>}
        </CardBody>
      </Card>
    </div>
  );
}
