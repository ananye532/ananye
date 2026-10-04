import { ArrowRight, Briefcase } from "lucide-react";
import { useState } from "react";
import { AnalyzingState, ResumeSource, validateSource, type SourceState } from "@/components/analysis/resume-source";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { Field, Input, Textarea } from "@/components/ui/field";
import { PageHeader } from "@/components/ui/misc";
import { ApiError } from "@/lib/api";
import { useResumes } from "@/lib/queries";
import { useRunAnalysis } from "@/lib/use-run-analysis";

export default function JobMatcher() {
  const { data: resumes, isLoading } = useResumes();
  const { run, stage, running, error } = useRunAnalysis();
  const [source, setSource] = useState<SourceState>({ mode: "existing", file: null, title: "", text: "", resumeId: null });
  const [jobTitle, setJobTitle] = useState("");
  const [jd, setJd] = useState("");
  const [touched, setTouched] = useState(false);

  const effective = resumes && resumes.length === 0 && source.mode === "existing" ? { ...source, mode: "upload" as const } : source;
  const sourceError = validateSource(effective);
  const jdError = jd.trim().length < 80 ? "Paste the full job description (at least 80 characters)." : null;
  if (running) return <AnalyzingState stage={stage} />;

  return (
    <>
      <PageHeader eyebrow="Job matcher" title="How well do you fit this job?"
        description="Compare a resume against a specific posting: matched and missing skills, keyword coverage, experience fit and requirement-level evidence." />
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="1. Resume" />
          <CardBody>
            <ResumeSource state={effective} onChange={setSource} resumes={resumes} resumesLoading={isLoading} />
            {touched && sourceError && <p className="mt-3 text-sm text-bad-fg" role="alert">{sourceError}</p>}
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="2. Job description" icon={<Briefcase />} />
          <CardBody className="space-y-4">
            <Field label="Job title" htmlFor="m-jt" hint="Optional — detected from the posting if blank."><Input id="m-jt" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} placeholder="e.g. Product Designer" /></Field>
            <Field label="Description" htmlFor="m-jd" error={touched ? jdError : null}>
              <Textarea id="m-jd" className="min-h-72" value={jd} onChange={(e) => setJd(e.target.value)} placeholder="Paste the posting: responsibilities, requirements, nice-to-haves…" />
            </Field>
          </CardBody>
        </Card>
      </div>
      {error != null && <p className="mt-4 rounded-lg bg-bad-soft px-3 py-2 text-sm text-bad-fg" role="alert">{error instanceof ApiError ? error.message : "Analysis failed. Please try again."}</p>}
      <div className="mt-6 flex justify-end">
        <Button size="lg" onClick={() => {
          setTouched(true);
          if (!sourceError && !jdError) void run(effective, { job_title: jobTitle.trim() || undefined, job_description: jd.trim() }, "/match");
        }}>Match against job <ArrowRight /></Button>
      </div>
    </>
  );
}
