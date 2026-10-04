import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createContext, useCallback, useContext, useEffect, useMemo, type ReactNode } from "react";
import { api, setUnauthorizedHandler, tokenStore } from "./api";
import type { TokenResponse, User } from "./types";

interface AuthState {
  user: User | null;
  loading: boolean;
  signIn: (res: TokenResponse) => void;
  signOut: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const qc = useQueryClient();
  const hasToken = !!tokenStore.get();
  const { data, isLoading } = useQuery({ queryKey: ["me"], queryFn: api.me, enabled: hasToken, retry: false, staleTime: 60_000 });

  const signOut = useCallback(() => {
    tokenStore.set(null);
    qc.clear();
    qc.setQueryData(["me"], null);
  }, [qc]);

  const signIn = useCallback((res: TokenResponse) => {
    tokenStore.set(res.access_token);
    qc.setQueryData(["me"], res.user);
  }, [qc]);

  useEffect(() => setUnauthorizedHandler(signOut), [signOut]);

  const value = useMemo<AuthState>(
    () => ({ user: hasToken ? (data ?? null) : null, loading: hasToken && isLoading, signIn, signOut }),
    [data, hasToken, isLoading, signIn, signOut],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
