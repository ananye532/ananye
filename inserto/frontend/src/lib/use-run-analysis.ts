import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { SourceState } from "@/components/analysis/resume-source";
import { STAGE_COUNT } from "@/components/analysis/resume-source";
import { api } from "./api";
import { useAnalyze, useInvalidateWorkspace } from "./queries";

/** Resolves the resume (upload/paste/existing), runs the analysis and navigates to it. */
export function useRunAnalysis() {
  const analyze = useAnalyze();
  const invalidate = useInvalidateWorkspace();
  const nav = useNavigate();
  const [stage, setStage] = useState(-1);
  const [error, setError] = useState<unknown>(null);
  const timer = useRef<number | null>(null);

  useEffect(() => () => { if (timer.current) window.clearInterval(timer.current); }, []);

  async function run(source: SourceState, opts: { job_title?: string; job_description?: string; target_role?: string }, tab = "") {
    setError(null);
    setStage(0);
    // Stages are a progress narrative; the request itself is one round-trip.
    timer.current = window.setInterval(() => setStage((s) => Math.min(s + 1, STAGE_COUNT - 1)), 550);
    try {
      let resumeId = source.resumeId;
      if (source.mode === "upload" && source.file) resumeId = (await api.uploadResume(source.file)).id;
      if (source.mode === "paste") resumeId = (await api.pasteResume({ title: source.title.trim(), text: source.text })).id;
      if (!resumeId) throw new Error("No resume selected");
      void invalidate();
      const a = await analyze.mutateAsync({ resume_id: resumeId, ...opts });
      nav(`/app/analyses/${a.id}${tab}`);
    } catch (e) {
      setError(e);
      setStage(-1);
    } finally {
      if (timer.current) window.clearInterval(timer.current);
    }
  }

  return { run, stage, running: stage >= 0, error };
}
