import type {
  Analysis, AnalysisSummary, Comparison, Dashboard, Meta, Preferences, Resume, ResumeDetail, TokenResponse, User,
} from "./types";

const TOKEN_KEY = "inserto-token";

export const tokenStore = {
  get: (): string | null => {
    try { return localStorage.getItem(TOKEN_KEY); } catch { return null; }
  },
  set: (t: string | null) => {
    try { t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY); } catch { /* storage unavailable */ }
  },
};

export class ApiError extends Error {
  constructor(public status: number, message: string, public code?: string) {
    super(message);
  }
}

let onUnauthorized: (() => void) | null = null;
export const setUnauthorizedHandler = (fn: () => void) => { onUnauthorized = fn; };

function messageFrom(body: unknown, fallback: string): { message: string; code?: string } {
  if (body && typeof body === "object" && "detail" in body) {
    const d = (body as { detail: unknown }).detail;
    if (typeof d === "string") return { message: d };
    if (d && typeof d === "object" && "message" in d) return { message: String((d as { message: string }).message), code: (d as { code?: string }).code };
    if (Array.isArray(d) && d[0]?.msg) return { message: String(d[0].msg).replace(/^Value error, /, "") };
  }
  return { message: fallback };
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const token = tokenStore.get();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
  let res: Response;
  try {
    res = await fetch(`/api${path}`, { ...init, headers });
  } catch {
    throw new ApiError(0, "Can’t reach the Inserto server. Check your connection and try again.");
  }
  if (res.status === 204) return undefined as T;
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    if (res.status === 401 && token) onUnauthorized?.();
    const { message, code } = messageFrom(body, `Request failed (${res.status})`);
    throw new ApiError(res.status, message, code);
  }
  return body as T;
}

const json = (data: unknown) => JSON.stringify(data);

export const api = {
  register: (d: { email: string; name: string; password: string }) => request<TokenResponse>("/auth/register", { method: "POST", body: json(d) }),
  login: (d: { email: string; password: string }) => request<TokenResponse>("/auth/login", { method: "POST", body: json(d) }),
  me: () => request<User>("/auth/me"),
  updateProfile: (d: Partial<Pick<User, "name" | "headline" | "target_role">>) => request<User>("/me", { method: "PATCH", body: json(d) }),
  updatePreferences: (d: Preferences) => request<User>("/me/preferences", { method: "PUT", body: json(d) }),
  changePassword: (d: { current_password: string; new_password: string }) => request<void>("/me/password", { method: "POST", body: json(d) }),
  deleteAccount: () => request<void>("/me", { method: "DELETE" }),

  meta: () => request<Meta>("/meta"),
  dashboard: () => request<Dashboard>("/dashboard"),

  resumes: () => request<Resume[]>("/resumes"),
  resume: (id: number) => request<ResumeDetail>(`/resumes/${id}`),
  uploadResume: (file: File, title?: string) => {
    const fd = new FormData();
    fd.append("file", file);
    if (title) fd.append("title", title);
    return request<ResumeDetail>("/resumes/upload", { method: "POST", body: fd });
  },
  pasteResume: (d: { title: string; text: string }) => request<ResumeDetail>("/resumes/paste", { method: "POST", body: json(d) }),
  renameResume: (id: number, title: string) => request<Resume>(`/resumes/${id}`, { method: "PATCH", body: json({ title }) }),
  deleteResume: (id: number) => request<void>(`/resumes/${id}`, { method: "DELETE" }),

  analyze: (d: { resume_id: number; job_title?: string; job_description?: string; target_role?: string; use_ai?: boolean }) =>
    request<Analysis>("/analyses", { method: "POST", body: json(d) }),
  analyses: (params: { resume_id?: number; q?: string; limit?: number } = {}) => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => v !== undefined && v !== "" && qs.set(k, String(v)));
    return request<AnalysisSummary[]>(`/analyses${qs.size ? `?${qs}` : ""}`);
  },
  analysis: (id: number) => request<Analysis>(`/analyses/${id}`),
  deleteAnalysis: (id: number) => request<void>(`/analyses/${id}`, { method: "DELETE" }),
  compare: (a: number, b: number) => request<Comparison>("/compare", { method: "POST", body: json({ a, b }) }),
  rewrite: (bullet: string, context?: string) => request<{ provider: string; options: string[] }>("/studio/rewrite", { method: "POST", body: json({ bullet, context }) }),
};
