import { Check, Copy, Lightbulb, Sparkles, Wand2 } from "lucide-react";
import { useState } from "react";
import { Quote, SectionTitle } from "@/components/analysis/primitives";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { Field, Textarea } from "@/components/ui/field";
import { EmptyState } from "@/components/ui/misc";
import { ApiError, api } from "@/lib/api";
import { useToast } from "@/lib/toast";
import { useAnalysisContext } from "./layout";

function Highlight({ text }: { text: string }) {
  const parts = text.split(/(\[[^\]]+\])/g);
  return <>{parts.map((p, i) => p.startsWith("[") ? <mark key={i} className="rounded bg-accent-soft px-1 text-accent-fg">{p}</mark> : <span key={i}>{p}</span>)}</>;
}

function CopyButton({ text }: { text: string }) {
  const [done, setDone] = useState(false);
  return (
    <Button variant="ghost" size="sm" aria-label="Copy rewrite" onClick={async () => {
      try { await navigator.clipboard.writeText(text); setDone(true); setTimeout(() => setDone(false), 1500); } catch { /* clipboard blocked */ }
    }}>{done ? <Check /> : <Copy />}{done ? "Copied" : "Copy"}</Button>
  );
}

function Workbench() {
  const toast = useToast();
  const [bullet, setBullet] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<{ provider: string; options: string[] } | null>(null);
  async function go() {
    if (bullet.trim().length < 3) return;
    setBusy(true);
    try { setResult(await api.rewrite(bullet.trim())); }
    catch (e) { toast({ kind: "error", title: "Rewrite failed", body: e instanceof ApiError ? e.message : undefined }); }
    finally { setBusy(false); }
  }
  return (
    <Card>
      <CardHeader title="Rewrite any bullet" description="Paste a line from your resume to get a stronger version." icon={<Wand2 />} />
      <CardBody className="space-y-4">
        <Field label="Original bullet" htmlFor="wb"><Textarea id="wb" className="min-h-24" value={bullet} onChange={(e) => setBullet(e.target.value)} placeholder="e.g. Responsible for managing the company website" /></Field>
        <Button onClick={go} loading={busy} disabled={bullet.trim().length < 3}><Sparkles />Improve</Button>
        {result && (
          <div className="space-y-2">
            <SectionTitle aside={<Badge variant="outline">{result.provider === "deterministic" ? "Rule-based" : "AI"}</Badge>}>Suggestions</SectionTitle>
            {result.options.map((o) => (
              <div key={o} className="flex items-start justify-between gap-3 rounded-lg border border-border bg-surface-2 p-3 text-sm">
                <p className="leading-relaxed"><Highlight text={o} /></p><CopyButton text={o} />
              </div>
            ))}
          </div>
        )}
      </CardBody>
    </Card>
  );
}

export default function StudioTab() {
  const r = useAnalysisContext().result;
  const aiRewrites = r.ai?.rewrites ?? [];
  return (
    <div className="grid gap-6 lg:grid-cols-5">
      <div className="space-y-6 lg:col-span-3">
        <Card>
          <CardHeader title="Suggested rewrites" description="Your weakest bullets, rewritten. Bracketed text marks numbers only you know." icon={<Lightbulb />} />
          <CardBody>
            {r.rewrites.length || aiRewrites.length ? (
              <ul className="space-y-5">
                {r.rewrites.map((rw) => (
                  <li key={rw.original} className="rounded-xl border border-border p-4">
                    <SectionTitle>Before</SectionTitle>
                    <Quote tone="bad">{rw.original}</Quote>
                    <div className="mt-4"><SectionTitle aside={<CopyButton text={rw.improved} />}>After</SectionTitle></div>
                    <div className="rounded-lg border-l-2 border-good bg-good-soft/50 px-3.5 py-2.5 text-sm leading-relaxed"><Highlight text={rw.improved} /></div>
                    <div className="mt-3 flex flex-wrap gap-1.5">
                      {rw.reasons.map((x) => <Badge key={x} variant="outline">{x}</Badge>)}
                      {rw.needs_input && <Badge variant="accent">Fill in your numbers</Badge>}
                    </div>
                  </li>
                ))}
                {aiRewrites.map((rw) => (
                  <li key={`ai-${rw.original}`} className="rounded-xl border border-border p-4">
                    <SectionTitle aside={<Badge variant="accent"><Sparkles />AI</Badge>}>Before</SectionTitle>
                    <Quote tone="bad">{rw.original}</Quote>
                    <div className="mt-4"><SectionTitle aside={<CopyButton text={rw.improved} />}>After</SectionTitle></div>
                    <div className="rounded-lg border-l-2 border-good bg-good-soft/50 px-3.5 py-2.5 text-sm"><Highlight text={rw.improved} /></div>
                    <p className="mt-2 text-xs text-fg-3">{rw.rationale}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState icon={<Check />} title="No weak bullets found" description="Every bullet already opens with an action verb and carries a measurable result." />
            )}
          </CardBody>
        </Card>
      </div>
      <div className="space-y-6 lg:col-span-2">
        <Workbench />
        <Card>
          <CardHeader title="Bullet formula" />
          <CardBody className="space-y-3 text-sm text-fg-2">
            <p><span className="font-medium text-fg">Action verb</span> + <span className="font-medium text-fg">what you did</span> + <span className="font-medium text-fg">measurable result</span>.</p>
            <Quote tone="good">Reduced checkout latency 38% by moving pricing rules into an edge cache, lifting conversion 2.1 points.</Quote>
            <ul className="list-disc space-y-1 pl-4">
              <li>One idea per bullet, under ~30 words.</li>
              <li>Prefer outcomes (revenue, time, quality) over duties.</li>
              <li>Use real numbers. Estimates are fine if you can defend them.</li>
            </ul>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
