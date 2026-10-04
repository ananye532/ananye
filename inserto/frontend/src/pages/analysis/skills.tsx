import { Search } from "lucide-react";
import { useMemo, useState } from "react";
import { Chips, SectionTitle } from "@/components/analysis/primitives";
import { CategoryBars } from "@/components/charts/category-bars";
import { Badge } from "@/components/ui/badge";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { Input } from "@/components/ui/field";
import { Segmented } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import { useAnalysisContext } from "./layout";

type Filter = "all" | "hard" | "soft" | "unlisted";

export default function SkillsTab() {
  const r = useAnalysisContext().result;
  const [q, setQ] = useState("");
  const [filter, setFilter] = useState<Filter>("all");
  const [open, setOpen] = useState<string | null>(null);

  const skills = useMemo(() => r.skills.found.filter((s) =>
    (filter === "all" || (filter === "hard" && !s.soft) || (filter === "soft" && s.soft) || (filter === "unlisted" && !s.in_skills_section && !s.soft))
    && s.name.toLowerCase().includes(q.toLowerCase())), [r.skills.found, q, filter]);

  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-5">
        <Card className="lg:col-span-3">
          <CardHeader title="Extracted skills" description={`${r.skills.hard_count} hard · ${r.skills.soft_count} soft · select a skill to see where it was found`} />
          <CardBody>
            <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="relative sm:w-56">
                <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-fg-3" aria-hidden />
                <Input placeholder="Filter skills" className="h-9 pl-9" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Filter skills" />
              </div>
              <Segmented label="Skill type" value={filter} onChange={setFilter}
                options={[{ value: "all", label: "All" }, { value: "hard", label: "Hard" }, { value: "soft", label: "Soft" }, { value: "unlisted", label: "Not in list" }]} />
            </div>
            {skills.length ? (
              <ul className="divide-y divide-border rounded-xl border border-border">
                {skills.map((s) => (
                  <li key={s.name}>
                    <button className="flex w-full items-center justify-between gap-3 px-4 py-2.5 text-left hover:bg-surface-2" onClick={() => setOpen(open === s.name ? null : s.name)} aria-expanded={open === s.name}>
                      <span className="flex min-w-0 items-center gap-2">
                        <span className="text-sm font-medium">{s.name}</span>
                        {!s.in_skills_section && !s.soft && <Badge variant="outline">not in skills list</Badge>}
                      </span>
                      <span className="flex shrink-0 items-center gap-3 text-xs text-fg-3"><span className="hidden sm:inline">{s.category}</span><span className="tabular">{s.count}×</span></span>
                    </button>
                    {open === s.name && <p className="border-t border-border bg-surface-2 px-4 py-2.5 font-mono text-xs leading-relaxed text-fg-2">{s.evidence}</p>}
                  </li>
                ))}
              </ul>
            ) : <p className="py-8 text-center text-sm text-fg-3">No skills match this filter.</p>}
          </CardBody>
        </Card>
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <CardHeader title="By category" />
            <CardBody>{r.skills.by_category.length ? <CategoryBars data={r.skills.by_category} /> : <p className="text-sm text-fg-3">No recognized skills.</p>}</CardBody>
          </Card>
          <Card>
            <CardHeader title={`Gaps${r.skills.target_role ? ` for ${r.skills.target_role}` : ""}`} description="Commonly expected skills the resume doesn’t show." />
            <CardBody className="space-y-4">
              <div><SectionTitle>Core</SectionTitle><Chips variant="warn" items={r.skills.missing.filter((g) => g.importance === "core").map((g) => g.name)} empty="All core skills shown." /></div>
              <div><SectionTitle>Nice to have</SectionTitle><Chips items={r.skills.missing.filter((g) => g.importance === "nice").map((g) => g.name)} empty="None missing." /></div>
              {r.skills.unsupported.length > 0 && (
                <div><SectionTitle>Listed without evidence</SectionTitle><Chips variant="outline" items={r.skills.unsupported} />
                  <p className="mt-2 text-xs text-fg-3">These appear in your skills list but not in any bullet. Mention how you used them.</p></div>
              )}
            </CardBody>
          </Card>
        </div>
      </div>

      <Card>
        <CardHeader title="Keyword intelligence" description={`Keyword score ${r.keywords.score}/100 · ${r.keywords.density} distinct hard skills per 100 words`} />
        <CardBody className="grid gap-8 md:grid-cols-3">
          <div>
            <SectionTitle>Most frequent terms</SectionTitle>
            <div className="flex flex-wrap gap-1.5">
              {r.keywords.top.map((t) => (
                <span key={t.term} className={cn("inline-flex items-center gap-1 rounded-md bg-surface-2 px-2 py-1 text-[13px] ring-1 ring-inset ring-border")}>
                  {t.term}<span className="tabular text-xs text-fg-3">{t.count}</span>
                </span>
              ))}
            </div>
          </div>
          <div>
            <SectionTitle>Expected but missing</SectionTitle>
            <Chips variant="bad" items={r.keywords.missing} empty={r.match || r.skills.target_role ? "Nothing missing." : "Pick a target role or add a job description to check."} />
          </div>
          <div>
            <SectionTitle>Overused</SectionTitle>
            {r.keywords.overused.length
              ? <ul className="space-y-1.5 text-sm">{r.keywords.overused.map((t) => <li key={t.term} className="flex justify-between"><span>{t.term}</span><span className="tabular text-fg-3">{t.count}×</span></li>)}</ul>
              : <p className="text-sm text-fg-3">No repetitive terms.</p>}
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
