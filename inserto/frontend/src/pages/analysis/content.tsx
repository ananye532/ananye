import { Activity, BookOpenText, GraduationCap, Hash, Trophy, Type } from "lucide-react";
import type { ReactNode } from "react";
import { Chips, Notes, Quote, ScorePill, SectionTitle, Stat } from "@/components/analysis/primitives";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { Progress } from "@/components/ui/misc";
import { pct } from "@/lib/utils";
import { useAnalysisContext } from "./layout";

function Block({ title, icon, score, description, children }: { title: string; icon: ReactNode; score: number; description: string; children: ReactNode }) {
  return (
    <Card>
      <CardHeader title={title} description={description} icon={icon} action={<ScorePill score={score} />} />
      <CardBody className="space-y-5">{children}</CardBody>
    </Card>
  );
}

export default function ContentTab() {
  const r = useAnalysisContext().result;
  const q = r.quantification, v = r.action_verbs, rd = r.readability, ex = r.experience, ed = r.education, ach = r.achievements;
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Block title="Quantification" icon={<Hash />} score={q.score} description="Bullets that show scale, speed or quality with numbers.">
        <div>
          <div className="mb-2 flex justify-between text-sm"><span>{q.quantified} of {q.total} bullets quantified</span><span className="tabular font-medium">{pct(q.ratio)}</span></div>
          <Progress value={q.ratio * 100} />
          <p className="mt-2 text-xs text-fg-3">Aim for 60% or more.</p>
        </div>
        {q.examples.length > 0 && <div><SectionTitle>Good examples</SectionTitle><div className="space-y-2">{q.examples.slice(0, 2).map((e) => <Quote key={e} tone="good">{e}</Quote>)}</div></div>}
        {q.unquantified.length > 0 && <div><SectionTitle>Needs a number</SectionTitle><div className="space-y-2">{q.unquantified.slice(0, 3).map((e) => <Quote key={e} tone="bad">{e}</Quote>)}</div></div>}
      </Block>

      <Block title="Action verbs" icon={<Activity />} score={v.score} description="Ownership-driven language at the start of each bullet.">
        <div>
          <div className="mb-2 flex justify-between text-sm"><span>Bullets opening with an action verb</span><span className="tabular font-medium">{pct(v.starts_with_verb_ratio)}</span></div>
          <Progress value={v.starts_with_verb_ratio * 100} />
        </div>
        <div><SectionTitle>Strong verbs used</SectionTitle><Chips variant="good" items={v.strong.map((s) => `${s.verb} ×${s.count}`)} empty="None detected." /></div>
        {v.weak.length > 0 && (
          <div>
            <SectionTitle>Weak phrasing</SectionTitle>
            <ul className="divide-y divide-border rounded-xl border border-border text-sm">
              {v.weak.map((w) => <li key={w.phrase} className="flex flex-wrap justify-between gap-2 px-3 py-2"><span>“{w.phrase}” <span className="text-fg-3">×{w.count}</span></span><span className="text-fg-2">→ {w.suggestion}</span></li>)}
            </ul>
          </div>
        )}
        {v.repeated.length > 0 && <Notes items={[`Repeated openers: ${v.repeated.map((x) => `${x.verb} (${x.count}×)`).join(", ")}`]} />}
      </Block>

      <Block title="Achievements" icon={<Trophy />} score={ach.score} description="Results-oriented bullets that pair an outcome verb with a measure.">
        <div className="grid grid-cols-2 gap-3"><Stat label="Achievement bullets" value={ach.count} /><Stat label="Total bullets" value={q.total} /></div>
        {ach.examples.length > 0 ? <div className="space-y-2">{ach.examples.slice(0, 3).map((e) => <Quote key={e} tone="good">{e}</Quote>)}</div> : null}
        <Notes items={ach.notes} />
      </Block>

      <Block title="Readability" icon={<Type />} score={rd.score} description="Concise, scannable writing without filler.">
        <div className="grid grid-cols-3 gap-3">
          <Stat label="Avg. bullet" value={rd.avg_bullet_words} hint="words" />
          <Stat label="Reading ease" value={rd.flesch} hint="Flesch" />
          <Stat label="Pronouns" value={rd.first_person} hint="first-person" />
        </div>
        {rd.buzzwords.length > 0 && <div><SectionTitle>Buzzwords</SectionTitle><Chips variant="warn" items={rd.buzzwords.map((b) => b.term)} /></div>}
        {rd.long_bullets.length > 0 && <div><SectionTitle>Too long</SectionTitle><Quote tone="bad">{rd.long_bullets[0]}</Quote></div>}
        <Notes items={rd.notes} />
      </Block>

      <Block title="Experience" icon={<BookOpenText />} score={ex.score} description="Clarity of roles, dates and progression.">
        <div className="grid grid-cols-3 gap-3">
          <Stat label="Years" value={ex.total_years} hint={ex.seniority} />
          <Stat label="Roles" value={ex.role_count} hint={ex.avg_tenure_months ? `${ex.avg_tenure_months} mo avg.` : undefined} />
          <Stat label="Bullets / role" value={ex.bullets_per_role} />
        </div>
        {ex.gaps.length > 0 && (
          <div><SectionTitle>Gaps</SectionTitle>
            <ul className="space-y-1 text-sm text-fg-2">{ex.gaps.map((g) => <li key={g.start}>{g.start} → {g.end} <span className="text-fg-3">({g.months} months)</span></li>)}</ul></div>
        )}
        <Notes items={ex.notes.filter((n) => !n.includes("gap between"))} />
      </Block>

      <Block title="Education" icon={<GraduationCap />} score={ed.score} description="Degrees, institutions and dates.">
        <div className="grid grid-cols-2 gap-3"><Stat label="Highest level" value={ed.highest ?? "—"} /><Stat label="Entries" value={ed.entries} /></div>
        <Notes items={ed.notes} />
      </Block>
    </div>
  );
}
