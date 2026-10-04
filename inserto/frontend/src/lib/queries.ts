import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./api";

export const keys = {
  dashboard: ["dashboard"] as const,
  resumes: ["resumes"] as const,
  resume: (id: number) => ["resume", id] as const,
  analyses: (p: object = {}) => ["analyses", p] as const,
  analysis: (id: number) => ["analysis", id] as const,
  meta: ["meta"] as const,
};

export const useMeta = () => useQuery({ queryKey: keys.meta, queryFn: api.meta, staleTime: Infinity });
export const useDashboard = () => useQuery({ queryKey: keys.dashboard, queryFn: api.dashboard });
export const useResumes = () => useQuery({ queryKey: keys.resumes, queryFn: api.resumes });
export const useResume = (id: number) => useQuery({ queryKey: keys.resume(id), queryFn: () => api.resume(id), enabled: id > 0 });
export const useAnalyses = (p: { resume_id?: number; q?: string; limit?: number } = {}) =>
  useQuery({ queryKey: keys.analyses(p), queryFn: () => api.analyses(p) });
export const useAnalysis = (id: number) =>
  useQuery({ queryKey: keys.analysis(id), queryFn: () => api.analysis(id), enabled: id > 0, staleTime: Infinity });

export function useInvalidateWorkspace() {
  const qc = useQueryClient();
  return () => Promise.all([
    qc.invalidateQueries({ queryKey: keys.dashboard }),
    qc.invalidateQueries({ queryKey: keys.resumes }),
    qc.invalidateQueries({ queryKey: ["analyses"] }),
  ]);
}

export function useAnalyze() {
  const qc = useQueryClient();
  const invalidate = useInvalidateWorkspace();
  return useMutation({
    mutationFn: api.analyze,
    onSuccess: (a) => {
      qc.setQueryData(keys.analysis(a.id), a);
      void invalidate();
    },
  });
}
