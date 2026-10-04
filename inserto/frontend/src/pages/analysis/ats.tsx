import { ScanLine } from "lucide-react";
import { CheckRow, SectionTitle } from "@/components/analysis/primitives";
import { ScoreRing } from "@/components/charts/score-ring";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { Progress } from "@/components/ui/misc";
import type { Status } from "@/lib/types";
import { useAnalysisContext } from "./layout";

const ORDER: Record<Status, number> = { fail: 0, warn: 1, pass: 2 };

export default function AtsTab() {
  const r = useAnalysisContext().result;
  const checks = [...r.ats.checks].sort((a, b) => ORDER[a.status] - ORDER[b.status]);
  const counts = { pass: 0, warn: 0, fail: 0 } as Record<Status, number>;
  r.ats.checks.forEach((c) => counts[c.status]++);
  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="space-y-6">
        <Card className="flex flex-col items-center p-6 text-center">
          <ScoreRing score={r.ats.score} size={150} sublabel="ATS score" label="ATS compatibility score" />
          <p className="mt-4 text-sm text-fg-2">{r.ats.summary}</p>
          <div className="mt-5 grid w-full grid-cols-3 divide-x divide-border rounded-xl border border-border text-center">
            {(["pass", "warn", "fail"] as const).map((s) => (
              <div key={s} className="py-3">
                <div className="tabular text-lg font-semibold">{counts[s]}</div>
                <div className="text-xs text-fg-3">{s === "pass" ? "Passed" : s === "warn" ? "Review" : "Failed"}</div>
              </div>
            ))}
          </div>
        </Card>
        <Card>
          <CardHeader title="Parse confidence" description="How completely standard fields were recovered." />
          <CardBody>
            <div className="mb-2 flex justify-between text-sm"><span>Fields recovered</span><span className="tabular font-medium">{r.ats.parse_confidence}%</span></div>
            <Progress value={r.ats.parse_confidence} />
            <p className="mt-3 text-xs text-fg-3">Name, email, phone, dated roles, education and a skills list. Missing fields are often what ATS forms leave blank.</p>
          </CardBody>
        </Card>
      </div>
      <Card className="lg:col-span-2">
        <CardHeader title="Compatibility checks" description="Weighted by how often each issue causes lost or misfiled data." icon={<ScanLine />} />
        <CardBody>
          <SectionTitle>Issues first</SectionTitle>
          <ul className="divide-y divide-border">{checks.map((c) => <CheckRow key={c.id} check={c} />)}</ul>
          <div className="mt-5 rounded-xl bg-surface-2 p-4 text-sm text-fg-2">
            <span className="font-medium text-fg">About these checks. </span>
            ATS products differ. These checks target failure modes common across mainstream parsers — multi-column layouts,
            non-standard headings, unparseable dates and icon fonts — rather than any one vendor’s behavior.
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
