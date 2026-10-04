import {
  ArrowRight, Briefcase, CheckCircle2, ChevronDown, FileSearch, Gauge, KeyRound, Layers, ScanLine, ShieldCheck,
  Sparkles, Target, UploadCloud, Wand2,
} from "lucide-react";
import { Link } from "react-router-dom";
import { ScoreRing } from "@/components/charts/score-ring";
import { SubscoreBars } from "@/components/charts/subscore-bars";
import { StatusIcon } from "@/components/analysis/primitives";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import type { Subscore } from "@/lib/types";
import { cn } from "@/lib/utils";

const PREVIEW_SUBS: Subscore[] = [
  { key: "ats", label: "ATS compatibility", score: 92, weight: 0.2, description: "" },
  { key: "impact", label: "Impact", score: 64, weight: 0.28, description: "" },
  { key: "skills", label: "Skills & keywords", score: 81, weight: 0.15, description: "" },
  { key: "match", label: "Job match", score: 73, weight: 0.27, description: "" },
];

function ProductPreview() {
  return (
    <div className="relative mx-auto w-full max-w-5xl">
      <div className="absolute -inset-x-8 -top-10 bottom-0 -z-10 rounded-[40px] bg-gradient-to-b from-accent/10 via-transparent to-transparent blur-2xl" aria-hidden />
      <div className="overflow-hidden rounded-2xl border border-border bg-surface shadow-pop">
        <div className="flex items-center gap-2 border-b border-border bg-surface-2/60 px-4 py-2.5">
          <span className="size-2.5 rounded-full bg-border-strong" /><span className="size-2.5 rounded-full bg-border-strong" /><span className="size-2.5 rounded-full bg-border-strong" />
          <span className="ml-3 truncate text-xs text-fg-3">inserto.app / analyses / senior-backend-engineer</span>
        </div>
        <div className="grid gap-px bg-border md:grid-cols-[280px_1fr]">
          <div className="flex flex-col items-center justify-center gap-3 bg-surface p-6">
            <ScoreRing score={78} size={150} sublabel="Overall · B+" label="Example overall score" />
            <p className="max-w-[200px] text-center text-xs text-fg-3">Strong resume. Biggest opportunity: quantify impact.</p>
          </div>
          <div className="grid gap-px bg-border sm:grid-cols-2">
            <div className="bg-surface p-6">
              <div className="mb-4 text-xs font-semibold uppercase tracking-wider text-fg-3">Breakdown</div>
              <SubscoreBars items={PREVIEW_SUBS} />
            </div>
            <div className="bg-surface p-6">
              <div className="mb-4 text-xs font-semibold uppercase tracking-wider text-fg-3">ATS checks</div>
              <ul className="space-y-3 text-sm">
                {([["pass", "Standard section headings"], ["pass", "Parsable employment dates"], ["warn", "Single-column layout"], ["fail", "Quantified achievements"]] as const).map(([s, l]) => (
                  <li key={l} className="flex items-center gap-2.5"><StatusIcon status={s} />{l}</li>
                ))}
              </ul>
              <div className="mt-5 rounded-lg border border-border bg-surface-2 p-3 text-xs">
                <div className="mb-1 font-medium text-fg-2">Suggested rewrite</div>
                <p className="text-fg-3 line-through decoration-fg-3/50">Responsible for the payments API</p>
                <p className="mt-1 text-fg">Owned the payments API, cutting p99 latency by <span className="rounded bg-accent-soft px-1 text-accent-fg">[X%]</span></p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

const FEATURES = [
  { icon: ScanLine, title: "ATS intelligence", body: "A dozen parser checks — headings, dates, layout, glyphs, contact fields — weighted by how often they cause dropped data." },
  { icon: Layers, title: "Skill extraction", body: "120 skills across 14 categories, matched with evidence snippets so you can see exactly why each was found." },
  { icon: Briefcase, title: "Job match", body: "Paste a posting to see matched and missing skills, keyword coverage, years-of-experience fit and requirement-by-requirement evidence." },
  { icon: Gauge, title: "Resume scoring", body: "A transparent overall score built from six weighted dimensions. Every point traces back to a check you can read." },
  { icon: KeyRound, title: "Keyword intelligence", body: "Top terms, overused words and the role-specific keywords your resume never mentions." },
  { icon: Wand2, title: "Improvement studio", body: "Rewrites for your weakest bullets: stronger verbs, tighter phrasing, and placeholders where only you know the number." },
  { icon: FileSearch, title: "Recruiter lens", body: "What a recruiter takes away in a six-second skim, with the strengths and concerns they are likely to note." },
  { icon: Target, title: "Career insights", body: "Role-fit estimates across 13 role profiles, plus the skills that would most strengthen your target direction." },
];

const FAQ = [
  { q: "Is the score a prediction of whether I’ll get hired?", a: "No. Scores are heuristic estimates based on common recruiter and ATS conventions. They don’t model any specific employer’s system, and they can’t judge things like culture fit or referrals." },
  { q: "Does Inserto use AI?", a: "The core analysis is deterministic and runs without any AI model, so the same resume always gets the same score. An optional LLM provider can add narrative feedback and rewrite suggestions; it never changes the numbers." },
  { q: "What file types are supported?", a: "Text-based PDF, DOCX and TXT up to 5 MB, or pasted text. Scanned image PDFs aren’t supported because they contain no extractable text." },
  { q: "What happens to my data?", a: "Only the extracted text is stored, never the original file. You can delete any resume, analysis or your whole account at any time, and deletion cascades to everything linked to it." },
];

export default function Landing() {
  return (
    <>
      <section className="relative overflow-hidden">
        <div className="bg-grid absolute inset-0 -z-10 opacity-60" aria-hidden />
        <div className="mx-auto max-w-6xl px-4 pb-20 pt-16 sm:px-6 sm:pt-24">
          <div className="mx-auto max-w-3xl text-center">
            <Badge variant="outline" className="mb-6 animate-fade-up rounded-full px-3 py-1 text-[13px]">
              <Sparkles className="text-accent" aria-hidden />Resume intelligence, explained
            </Badge>
            <h1 className="animate-fade-up text-4xl font-semibold leading-[1.05] tracking-[-0.03em] text-balance sm:text-6xl">
              Understand how recruiters see your resume.
            </h1>
            <p className="mx-auto mt-6 max-w-2xl animate-fade-up text-lg leading-relaxed text-fg-2 text-pretty [animation-delay:80ms]">
              Inserto analyzes your resume the way an applicant tracking system and a hiring manager would — scoring
              ATS compatibility, skills, keywords, structure and impact, then measuring alignment with the job you want.
            </p>
            <div className="mt-9 flex animate-fade-up flex-col items-center justify-center gap-3 sm:flex-row [animation-delay:140ms]">
              <Link to="/register" className={cn(buttonVariants({ size: "lg" }), "w-full sm:w-auto")}>
                Analyze my resume <ArrowRight />
              </Link>
              <a href="#how" className={cn(buttonVariants({ variant: "secondary", size: "lg" }), "w-full sm:w-auto")}>See how it works</a>
            </div>
            <p className="mt-4 text-xs text-fg-3">Free to use · PDF, DOCX or plain text · Delete your data any time</p>
          </div>
          <div className="mt-16 animate-fade-up [animation-delay:220ms]"><ProductPreview /></div>
        </div>
      </section>

      <section id="features" className="border-t border-border bg-surface">
        <div className="mx-auto max-w-6xl px-4 py-24 sm:px-6">
          <div className="max-w-2xl">
            <p className="text-sm font-medium text-accent-fg">Capabilities</p>
            <h2 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">Every signal a screener looks for, in one report.</h2>
            <p className="mt-4 text-lg text-fg-2">Eighteen analyses run on every upload. Each finding links to the text that triggered it.</p>
          </div>
          <div className="mt-14 grid gap-px overflow-hidden rounded-2xl border border-border bg-border sm:grid-cols-2 lg:grid-cols-4">
            {FEATURES.map((f) => (
              <div key={f.title} className="group bg-surface p-6 transition-colors hover:bg-surface-2/50">
                <div className="grid size-9 place-items-center rounded-lg border border-border bg-bg text-fg-2 transition-colors group-hover:text-accent-fg"><f.icon className="size-[18px]" aria-hidden /></div>
                <h3 className="mt-5 font-semibold tracking-tight">{f.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-fg-2">{f.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="how" className="border-t border-border">
        <div className="mx-auto max-w-6xl px-4 py-24 sm:px-6">
          <div className="max-w-2xl">
            <p className="text-sm font-medium text-accent-fg">How it works</p>
            <h2 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">From upload to a sharper resume in three steps.</h2>
          </div>
          <ol className="mt-14 grid gap-6 md:grid-cols-3">
            {[
              { icon: UploadCloud, t: "Upload or paste", d: "Drop in a PDF or DOCX, or paste text. Inserto extracts and parses contact details, sections, roles, dates and education." },
              { icon: Briefcase, t: "Add a target (optional)", d: "Paste a job description or pick a target role to unlock job-match scoring and role-specific skill gaps." },
              { icon: Wand2, t: "Fix what matters first", d: "Work through prioritized recommendations and rewrite weak bullets in the studio. Re-analyze and compare versions." },
            ].map((s, i) => (
              <li key={s.t} className="relative rounded-2xl border border-border bg-surface p-6 shadow-card">
                <div className="flex items-center justify-between">
                  <div className="grid size-9 place-items-center rounded-lg bg-primary text-primary-fg"><s.icon className="size-4" aria-hidden /></div>
                  <span className="font-mono text-xs text-fg-3">0{i + 1}</span>
                </div>
                <h3 className="mt-5 font-semibold">{s.t}</h3>
                <p className="mt-2 text-sm leading-relaxed text-fg-2">{s.d}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section id="method" className="border-t border-border bg-surface">
        <div className="mx-auto grid max-w-6xl gap-12 px-4 py-24 sm:px-6 lg:grid-cols-2">
          <div>
            <p className="text-sm font-medium text-accent-fg">Methodology</p>
            <h2 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">Transparent by design.</h2>
            <p className="mt-4 text-lg text-fg-2">
              Black-box scores aren’t useful. Inserto’s engine is deterministic: the same resume always gets the same
              result, and every number is the sum of checks you can inspect.
            </p>
            <ul className="mt-8 space-y-4">
              {[
                "Weighted dimensions: ATS, structure, impact, skills, readability, experience — plus job match when you provide a posting.",
                "Skills come from a curated taxonomy with aliases (“k8s” → Kubernetes), each shown with its evidence.",
                "Rewrites never invent facts. Missing numbers become placeholders for you to fill in.",
                "An optional AI provider adds narrative feedback through a pluggable interface; scores stay deterministic.",
              ].map((t) => (
                <li key={t} className="flex gap-3 text-[15px] text-fg-2"><CheckCircle2 className="mt-0.5 size-5 shrink-0 text-good" aria-hidden />{t}</li>
              ))}
            </ul>
          </div>
          <div className="rounded-2xl border border-border bg-bg p-6">
            <div className="flex items-center gap-2 text-sm font-medium"><ShieldCheck className="size-4 text-good" aria-hidden />Score composition</div>
            <table className="mt-5 w-full text-sm">
              <thead><tr className="text-left text-xs text-fg-3"><th className="pb-2 font-medium">Dimension</th><th className="pb-2 text-right font-medium">Weight</th><th className="pb-2 text-right font-medium">With job</th></tr></thead>
              <tbody className="tabular">
                {[["Impact", 28, 22], ["ATS compatibility", 20, 15], ["Skills & keywords", 15, 10], ["Experience", 13, 10], ["Structure", 12, 8], ["Readability", 12, 8], ["Job match", 0, 27]].map(([l, a, b]) => (
                  <tr key={l} className="border-t border-border"><td className="py-2.5">{l}</td><td className="py-2.5 text-right text-fg-2">{a ? `${a}%` : "—"}</td><td className="py-2.5 text-right text-fg-2">{b}%</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section id="faq" className="border-t border-border">
        <div className="mx-auto max-w-3xl px-4 py-24 sm:px-6">
          <h2 className="text-3xl font-semibold tracking-tight">Questions</h2>
          <div className="mt-8 divide-y divide-border rounded-2xl border border-border bg-surface">
            {FAQ.map((f) => (
              <details key={f.q} className="group px-5 py-4 [&_summary::-webkit-details-marker]:hidden">
                <summary className="flex cursor-pointer list-none items-center justify-between gap-4 font-medium">
                  {f.q}<ChevronDown className="size-4 shrink-0 text-fg-3 transition-transform group-open:rotate-180" aria-hidden />
                </summary>
                <p className="mt-3 text-[15px] leading-relaxed text-fg-2">{f.a}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      <section className="border-t border-border bg-surface">
        <div className="mx-auto max-w-6xl px-4 py-20 text-center sm:px-6">
          <h2 className="text-3xl font-semibold tracking-tight">See your resume the way they do.</h2>
          <p className="mx-auto mt-3 max-w-xl text-fg-2">Your first analysis takes under a minute.</p>
          <Link to="/register" className={cn(buttonVariants({ size: "lg" }), "mt-8")}>Analyze my resume <ArrowRight /></Link>
        </div>
      </section>
    </>
  );
}
