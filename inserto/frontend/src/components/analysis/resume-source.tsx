import { CheckCircle2, ClipboardPaste, FileText, Loader2, UploadCloud, X } from "lucide-react";
import { useCallback, useRef, useState, type DragEvent } from "react";
import { Segmented } from "@/components/ui/tabs";
import { Field, Input, Select, Textarea } from "@/components/ui/field";
import type { Resume } from "@/lib/types";
import { cn, formatDate } from "@/lib/utils";

export type SourceMode = "upload" | "paste" | "existing";
export interface SourceState {
  mode: SourceMode;
  file: File | null;
  title: string;
  text: string;
  resumeId: number | null;
}

const MAX = 5 * 1024 * 1024;
const OK_EXT = [".pdf", ".docx", ".txt"];

export function validateSource(s: SourceState): string | null {
  if (s.mode === "upload") {
    if (!s.file) return "Choose a file to upload.";
    if (!OK_EXT.some((e) => s.file!.name.toLowerCase().endsWith(e))) return "Upload a PDF, DOCX or TXT file.";
    if (s.file.size > MAX) return "Files are limited to 5 MB.";
  }
  if (s.mode === "paste") {
    if (!s.title.trim()) return "Give this resume a name.";
    if (s.text.trim().length < 80) return "Paste the full resume text (at least a few lines).";
  }
  if (s.mode === "existing" && !s.resumeId) return "Choose a saved resume.";
  return null;
}

function Dropzone({ file, onFile }: { file: File | null; onFile: (f: File | null) => void }) {
  const input = useRef<HTMLInputElement>(null);
  const [over, setOver] = useState(false);
  const onDrop = useCallback((e: DragEvent) => {
    e.preventDefault();
    setOver(false);
    const f = e.dataTransfer.files?.[0];
    if (f) onFile(f);
  }, [onFile]);

  if (file) {
    return (
      <div className="flex items-center gap-3 rounded-xl border border-border bg-surface-2 p-4">
        <div className="grid size-10 place-items-center rounded-lg bg-surface text-fg-2 shadow-card"><FileText className="size-5" aria-hidden /></div>
        <div className="min-w-0 flex-1">
          <div className="truncate text-sm font-medium">{file.name}</div>
          <div className="text-xs text-fg-3">{(file.size / 1024).toFixed(0)} KB · ready to analyze</div>
        </div>
        <CheckCircle2 className="size-5 text-good" aria-label="File selected" />
        <button onClick={() => onFile(null)} className="rounded-md p-1 text-fg-3 hover:bg-surface hover:text-fg" aria-label="Remove file"><X className="size-4" /></button>
      </div>
    );
  }
  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setOver(true); }}
      onDragLeave={() => setOver(false)}
      onDrop={onDrop}
      onClick={() => input.current?.click()}
      onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && input.current?.click()}
      role="button" tabIndex={0} aria-label="Upload resume file"
      className={cn(
        "group flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-12 text-center transition-colors",
        over ? "border-accent bg-accent-soft" : "border-border-strong hover:border-fg-3 hover:bg-surface-2/50",
      )}>
      <div className="grid size-12 place-items-center rounded-2xl border border-border bg-surface shadow-card transition-transform group-hover:-translate-y-0.5">
        <UploadCloud className="size-5 text-fg-2" aria-hidden />
      </div>
      <p className="mt-4 text-sm font-medium">Drop your resume here, or <span className="text-accent-fg underline underline-offset-4">browse</span></p>
      <p className="mt-1 text-xs text-fg-3">PDF, DOCX or TXT · up to 5 MB · text-based (not scanned)</p>
      <input ref={input} type="file" accept=".pdf,.docx,.txt" className="sr-only" onChange={(e) => onFile(e.target.files?.[0] ?? null)} />
    </div>
  );
}

export function ResumeSource({ state, onChange, resumes, resumesLoading, allowUpload = true }: {
  state: SourceState; onChange: (s: SourceState) => void; resumes: Resume[] | undefined; resumesLoading?: boolean; allowUpload?: boolean;
}) {
  const options = [
    ...(allowUpload ? [{ value: "upload" as const, label: "Upload" }, { value: "paste" as const, label: "Paste text" }] : []),
    { value: "existing" as const, label: `Saved${resumes?.length ? ` (${resumes.length})` : ""}` },
  ];
  return (
    <div className="space-y-4">
      {options.length > 1 && <Segmented label="Resume source" value={state.mode} onChange={(mode) => onChange({ ...state, mode })} options={options} />}
      {state.mode === "upload" && <Dropzone file={state.file} onFile={(file) => onChange({ ...state, file })} />}
      {state.mode === "paste" && (
        <div className="space-y-4">
          <Field label="Resume name" htmlFor="r-title"><Input id="r-title" placeholder="e.g. Backend — Oct 2026" value={state.title} onChange={(e) => onChange({ ...state, title: e.target.value })} /></Field>
          <Field label="Resume text" htmlFor="r-text" hint={`${state.text.trim().split(/\s+/).filter(Boolean).length} words`}>
            <Textarea id="r-text" className="min-h-72 font-mono text-[13px]" placeholder={"Jordan Lee\njordan@example.com · (415) 555-0142\n\nEXPERIENCE\nSenior Software Engineer, Stripe — Jan 2022 – Present\n• Led …"}
              value={state.text} onChange={(e) => onChange({ ...state, text: e.target.value })} />
          </Field>
        </div>
      )}
      {state.mode === "existing" && (
        resumesLoading ? <div className="flex items-center gap-2 text-sm text-fg-3"><Loader2 className="size-4 animate-spin" />Loading resumes…</div>
          : resumes?.length ? (
            <Field label="Saved resume" htmlFor="r-existing">
              <Select id="r-existing" value={state.resumeId ?? ""} onChange={(e) => onChange({ ...state, resumeId: Number(e.target.value) || null })}>
                <option value="">Choose a resume…</option>
                {resumes.map((r) => <option key={r.id} value={r.id}>{r.title} · {formatDate(r.created_at)}</option>)}
              </Select>
            </Field>
          ) : (
            <div className="flex items-center gap-3 rounded-xl border border-dashed border-border-strong p-4 text-sm text-fg-3">
              <ClipboardPaste className="size-4" aria-hidden />No saved resumes yet. Upload or paste one first.
            </div>
          )
      )}
    </div>
  );
}

const STAGES = ["Extracting text", "Parsing sections and roles", "Running ATS checks", "Extracting skills and keywords", "Scoring impact and readability", "Writing recommendations"];

export function AnalyzingState({ stage }: { stage: number }) {
  return (
    <div className="mx-auto max-w-md py-16 text-center" aria-live="polite">
      <div className="relative mx-auto grid size-16 place-items-center">
        <div className="absolute inset-0 animate-ping rounded-full bg-accent/15" aria-hidden />
        <div className="relative grid size-14 place-items-center rounded-2xl bg-primary text-primary-fg"><Loader2 className="size-6 animate-spin" aria-hidden /></div>
      </div>
      <h2 className="mt-6 text-lg font-semibold">Analyzing your resume</h2>
      <ol className="mt-6 space-y-2.5 text-left">
        {STAGES.map((s, i) => (
          <li key={s} className={cn("flex items-center gap-3 text-sm transition-colors", i < stage ? "text-fg-2" : i === stage ? "font-medium text-fg" : "text-fg-3")}>
            {i < stage ? <CheckCircle2 className="size-4 text-good" aria-hidden />
              : i === stage ? <Loader2 className="size-4 animate-spin text-accent" aria-hidden />
                : <span className="size-4 rounded-full border border-border-strong" aria-hidden />}
            {s}
          </li>
        ))}
      </ol>
    </div>
  );
}

export const STAGE_COUNT = STAGES.length;
