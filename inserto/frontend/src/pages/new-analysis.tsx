import { ArrowRight, Briefcase, Target } from "lucide-react";
import { useState } from "react";
import { AnalyzingState, ResumeSource, validateSource, type SourceState } from "@/components/analysis/resume-source";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { Field, Input, Select, Textarea } from "@/components/ui/field";
import { PageHeader } from "@/components/ui/misc";
import { ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useMeta, useResumes } from "@/lib/queries";
import { useRunAnalysis } from "@/lib/use-run-analysis";

export default function NewAnalysis() {
  const { user } = useAuth();
  const { data: resumes, isLoading } = useResumes();
  const { data: meta } = useMeta();
  const { run, stage, running, error } = useRunAnalysis();
  const [source, setSource] = useState<SourceState>({ mode: "upload", file: null, title: "", text: "", resumeId: null });
  const [targetRole, setTargetRole] = useState(user?.target_role ?? "");
  const [jobTitle, setJobTitle] = useState("");
  const [jd, setJd] = useState("");
  const [touched, setTouched] = useState(false);

  const sourceError = validateSource(source);
  const jdError = jd.trim() && jd.trim().length < 80 ? "Paste the full job description (at least 80 characters)." : null;

  if (running) return <AnalyzingState stage={stage} />;

  function submit() {
    setTouched(true);
    if (sourceError || jdError) return;
    void run(source, { target_role: targetRole || undefined, job_title: jobTitle.trim() || undefined, job_description: jd.trim() || undefined });
  }

  return (
    <>
      <PageHeader eyebrow="New analysis" title="Analyze a resume" description="Upload or paste your resume. Add a target role or job description for tailored scoring." />
      <div className="grid gap-6 lg:grid-cols-5">
        <Card className="lg:col-span-3">
          <CardHeader title="Your resume" description="Only the extracted text is stored, never the original file." />
          <CardBody>
            <ResumeSource state={source} onChange={setSource} resumes={resumes} resumesLoading={isLoading} />
            {touched && sourceError && <p className="mt-3 text-sm text-bad-fg" role="alert">{sourceError}</p>}
          </CardBody>
        </Card>
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <CardHeader title="Target role" description="Used for skill-gap and keyword analysis." icon={<Target />} />
            <CardBody>
              <Field label="Role profile" htmlFor="role" hint="Leave on auto-detect to infer it from your skills.">
                <Select id="role" value={targetRole} onChange={(e) => setTargetRole(e.target.value)}>
                  <option value="">Auto-detect</option>
                  {meta?.roles.map((r) => <option key={r} value={r}>{r}</option>)}
                </Select>
              </Field>
            </CardBody>
          </Card>
          <Card>
            <CardHeader title="Job description" description="Optional. Unlocks job-match scoring." icon={<Briefcase />} />
            <CardBody className="space-y-4">
              <Field label="Job title" htmlFor="jt"><Input id="jt" placeholder="e.g. Senior Backend Engineer" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} /></Field>
              <Field label="Description" htmlFor="jd" error={touched ? jdError : null}>
                <Textarea id="jd" className="min-h-40" placeholder="Paste the full posting, including requirements…" value={jd} onChange={(e) => setJd(e.target.value)} />
              </Field>
            </CardBody>
          </Card>
          {error != null && <p className="rounded-lg bg-bad-soft px-3 py-2 text-sm text-bad-fg" role="alert">{error instanceof ApiError ? error.message : "Analysis failed. Please try again."}</p>}
          <Button size="lg" className="w-full" onClick={submit}>Run analysis <ArrowRight /></Button>
        </div>
      </div>
    </>
  );
}
