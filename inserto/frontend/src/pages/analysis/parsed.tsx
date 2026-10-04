import { Award, Briefcase, GraduationCap, Link2, Mail, MapPin, Phone, User } from "lucide-react";
import { Chips, SectionTitle, StatusIcon } from "@/components/analysis/primitives";
import { Badge } from "@/components/ui/badge";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { useAnalysisContext } from "./layout";

function months(m: number | null) {
  if (!m) return null;
  const y = Math.floor(m / 12), r = m % 12;
  return [y && `${y} yr${y > 1 ? "s" : ""}`, r && `${r} mo`].filter(Boolean).join(" ");
}

export default function ParsedResume() {
  const r = useAnalysisContext().result;
  const p = r.parsed;
  const contact = [
    { icon: User, label: "Name", value: p.contact.name },
    { icon: Mail, label: "Email", value: p.contact.email },
    { icon: Phone, label: "Phone", value: p.contact.phone },
    { icon: MapPin, label: "Location", value: p.contact.location },
  ];
  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="space-y-6">
        <Card>
          <CardHeader title="Contact" description={`Parse confidence ${r.ats.parse_confidence}%`} />
          <CardBody>
            <dl className="space-y-3">
              {contact.map((c) => (
                <div key={c.label} className="flex items-start gap-3">
                  <c.icon className="mt-0.5 size-4 shrink-0 text-fg-3" aria-hidden />
                  <div className="min-w-0 flex-1">
                    <dt className="text-xs text-fg-3">{c.label}</dt>
                    <dd className={cn("break-words text-sm", !c.value && "text-fg-3 italic")}>{c.value ?? "Not detected"}</dd>
                  </div>
                  <StatusIcon status={c.value ? "pass" : c.label === "Location" ? "warn" : "fail"} />
                </div>
              ))}
              {p.contact.links.map((l) => (
                <div key={l} className="flex items-center gap-3 text-sm"><Link2 className="size-4 text-fg-3" aria-hidden /><span className="truncate">{l}</span></div>
              ))}
            </dl>
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="Detected sections" description={`${p.word_count} words · ~${p.page_estimate} page(s) · ${p.bullet_count} bullets`} />
          <CardBody>
            <ul className="space-y-2">
              {r.structure.sections.map((s) => (
                <li key={s.key} className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2.5"><StatusIcon status={s.present ? "pass" : s.required ? "fail" : "warn"} />{s.label}</span>
                  <span className="text-xs text-fg-3">{s.present ? (p.sections.find((x) => x.key === s.key)?.title ?? "Found") : s.required ? "Required" : "Optional"}</span>
                </li>
              ))}
            </ul>
            {r.structure.notes.length > 0 && <ul className="mt-4 space-y-1.5 border-t border-border pt-4 text-sm text-fg-2">{r.structure.notes.map((n) => <li key={n}>{n}</li>)}</ul>}
          </CardBody>
        </Card>
      </div>

      <div className="space-y-6 lg:col-span-2">
        {p.summary && (
          <Card><CardHeader title="Summary" /><CardBody><p className="text-sm leading-relaxed text-fg-2">{p.summary}</p></CardBody></Card>
        )}
        <Card>
          <CardHeader title="Experience" icon={<Briefcase />} description={`${r.experience.total_years} years · ${r.experience.role_count} roles · ${r.experience.seniority}`} />
          <CardBody>
            {p.roles.length ? (
              <ol className="relative space-y-6 border-l border-border pl-6">
                {p.roles.map((role, i) => (
                  <li key={i} className="relative">
                    <span className={cn("absolute -left-[29px] top-1.5 size-2.5 rounded-full ring-4 ring-surface", role.is_current ? "bg-accent" : "bg-border-strong")} aria-hidden />
                    <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
                      <div className="font-medium">{role.title}{role.company && <span className="font-normal text-fg-2"> · {role.company}</span>}</div>
                      <div className="flex items-center gap-2 text-xs text-fg-3">
                        {role.start ? <span className="tabular">{role.start} – {role.end}</span> : <Badge variant="warn">No dates</Badge>}
                        {months(role.duration_months) && <span>· {months(role.duration_months)}</span>}
                      </div>
                    </div>
                    {role.bullets.length > 0 && (
                      <ul className="mt-2 list-disc space-y-1 pl-4 text-sm text-fg-2 marker:text-fg-3">{role.bullets.map((b) => <li key={b}>{b}</li>)}</ul>
                    )}
                  </li>
                ))}
              </ol>
            ) : <p className="text-sm text-fg-3">No roles could be parsed. Use a clear “Experience” heading, and give each role a title, company and date range.</p>}
          </CardBody>
        </Card>
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader title="Education" icon={<GraduationCap />} />
            <CardBody>
              {p.education.length ? (
                <ul className="space-y-4">
                  {p.education.map((e, i) => (
                    <li key={i} className="text-sm">
                      <div className="font-medium">{e.institution ?? "Institution not detected"}</div>
                      <div className="text-fg-2">{e.degree ?? e.degree_level ?? "Degree not detected"}</div>
                      <div className="mt-0.5 text-xs text-fg-3">{[e.year, e.gpa && `GPA ${e.gpa}`].filter(Boolean).join(" · ")}</div>
                    </li>
                  ))}
                </ul>
              ) : <p className="text-sm text-fg-3">No education entries detected.</p>}
            </CardBody>
          </Card>
          <Card>
            <CardHeader title="Certifications" icon={<Award />} />
            <CardBody>
              {p.certifications.length ? <ul className="space-y-1.5 text-sm text-fg-2">{p.certifications.map((c) => <li key={c}>{c}</li>)}</ul>
                : <p className="text-sm text-fg-3">None listed.</p>}
            </CardBody>
          </Card>
        </div>
        <Card>
          <CardHeader title="Skills section" description="Items exactly as listed on your resume." />
          <CardBody><SectionTitle>{p.skills_listed.length} items</SectionTitle><Chips items={p.skills_listed} empty="No skills section detected." /></CardBody>
        </Card>
      </div>
    </div>
  );
}
