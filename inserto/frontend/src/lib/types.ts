// Mirrors backend/app/engine/result.py and app/schemas.py.

export type Status = "pass" | "warn" | "fail";
export type Impact = "high" | "medium" | "low";
export type Priority = "critical" | "high" | "medium" | "low";

export interface Preferences {
  ai_enhancement: boolean;
  default_target_role: string | null;
  email_digest: boolean;
  theme: "system" | "light" | "dark";
}

export interface User {
  id: number;
  email: string;
  name: string;
  headline: string | null;
  target_role: string | null;
  preferences: Preferences;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Resume {
  id: number;
  title: string;
  source: "pdf" | "docx" | "txt" | "paste";
  filename: string | null;
  page_count: number | null;
  created_at: string;
  word_count: number;
  latest_score: number | null;
  analysis_count: number;
}

export interface ResumeDetail extends Resume {
  text: string;
  parsed: Record<string, unknown>;
}

export interface AnalysisSummary {
  id: number;
  resume_id: number;
  resume_title: string;
  job_title: string | null;
  target_role: string | null;
  overall_score: number;
  ats_score: number;
  match_score: number | null;
  created_at: string;
}

export interface Subscore { key: string; label: string; score: number; weight: number; description: string }
export interface Check { id: string; label: string; status: Status; detail: string; impact: Impact }
export interface Term { term: string; count: number }
export interface SkillGap { name: string; category: string; importance: "core" | "nice"; reason: string }

export interface Role {
  title: string;
  company: string | null;
  start: string | null;
  end: string | null;
  is_current: boolean;
  duration_months: number | null;
  bullets: string[];
}

export interface AnalysisResult {
  engine_version: string;
  overall: { score: number; grade: string; label: string; summary: string };
  subscores: Subscore[];
  parsed: {
    contact: { name: string | null; email: string | null; phone: string | null; location: string | null; links: string[] };
    summary: string | null;
    sections: { key: string; label: string; title: string; line_count: number }[];
    roles: Role[];
    education: { institution: string | null; degree: string | null; degree_level: string | null; year: number | null; gpa: string | null }[];
    skills_listed: string[];
    certifications: string[];
    bullet_count: number;
    word_count: number;
    page_estimate: number;
  };
  ats: { score: number; checks: Check[]; parse_confidence: number; summary: string };
  structure: {
    score: number;
    sections: { key: string; label: string; present: boolean; required: boolean }[];
    order_ok: boolean;
    notes: string[];
    length_verdict: string;
  };
  skills: {
    score: number;
    found: { name: string; category: string; count: number; soft: boolean; in_skills_section: boolean; evidence: string }[];
    by_category: { category: string; count: number }[];
    hard_count: number;
    soft_count: number;
    missing: SkillGap[];
    unsupported: string[];
    target_role: string | null;
  };
  keywords: { score: number; top: Term[]; overused: Term[]; missing: string[]; density: number };
  experience: {
    score: number;
    total_years: number;
    role_count: number;
    avg_tenure_months: number | null;
    seniority: string;
    gaps: { start: string; end: string; months: number }[];
    bullets_per_role: number;
    notes: string[];
  };
  education: { score: number; highest: string | null; entries: number; notes: string[] };
  achievements: { score: number; count: number; examples: string[]; notes: string[] };
  quantification: { score: number; quantified: number; total: number; ratio: number; examples: string[]; unquantified: string[] };
  action_verbs: {
    score: number;
    strong: { verb: string; count: number }[];
    weak: { phrase: string; count: number; suggestion: string }[];
    repeated: { verb: string; count: number }[];
    starts_with_verb_ratio: number;
  };
  readability: {
    score: number;
    flesch: number;
    avg_bullet_words: number;
    long_bullets: string[];
    short_bullets: string[];
    first_person: number;
    passive: number;
    buzzwords: Term[];
    notes: string[];
  };
  match: null | {
    score: number;
    job_title: string | null;
    skill_score: number;
    keyword_score: number;
    matched_skills: string[];
    missing_skills: string[];
    extra_skills: string[];
    matched_keywords: string[];
    missing_keywords: string[];
    requirements: { text: string; met: "met" | "partial" | "missing"; evidence: string | null }[];
    years_required: number | null;
    years_found: number;
    verdict: string;
  };
  recruiter: { first_impression: string; strengths: string[]; concerns: string[]; skim: string[]; verdict: string };
  recommendations: {
    id: string;
    priority: Priority;
    category: string;
    title: string;
    detail: string;
    before: string | null;
    after: string | null;
  }[];
  rewrites: { original: string; improved: string; reasons: string[]; needs_input: boolean }[];
  insights: {
    career_level: string;
    role_fits: { role: string; fit: number; matched: string[]; missing: string[] }[];
    strengths: string[];
    growth_skills: SkillGap[];
    next_steps: string[];
  };
  provider: { name: string; ai_enhanced: boolean; note: string | null };
  ai?: {
    first_impression: string | null;
    strengths: string[];
    concerns: string[];
    rewrites: { original: string; improved: string; rationale: string }[];
    career_advice: string[];
  };
  disclaimer: string;
}

export interface Analysis extends AnalysisSummary {
  result: AnalysisResult;
  job_description: string | null;
}

export interface Dashboard {
  resume_count: number;
  analysis_count: number;
  best_score: number | null;
  latest: AnalysisSummary | null;
  trend: { id: number; date: string; overall: number; ats: number; match: number | null; label: string }[];
  recent: AnalysisSummary[];
  top_recommendations: AnalysisResult["recommendations"];
}

export interface Comparison {
  a: AnalysisSummary;
  b: AnalysisSummary;
  subscores: { key: string; label: string; a: number | null; b: number | null; delta: number | null }[];
  metrics: { label: string; a: number; b: number; delta: number }[];
  skills_only_a: string[];
  skills_only_b: string[];
  skills_shared: string[];
  winner: "a" | "b" | "tie";
}

export interface Meta {
  roles: string[];
  ai_provider: string;
  ai_available: boolean;
  engine_version: string;
}
