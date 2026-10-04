import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Monitor, Moon, Sun } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { ConfirmDialog } from "@/components/ui/dialog";
import { Field, Input } from "@/components/ui/field";
import { PageHeader, Switch } from "@/components/ui/misc";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useMeta } from "@/lib/queries";
import { useTheme, type ThemeChoice } from "@/lib/theme";
import { useToast } from "@/lib/toast";
import type { Preferences } from "@/lib/types";
import { cn } from "@/lib/utils";

function Row({ title, description, children }: { title: string; description: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-6 py-4 first:pt-0 last:pb-0">
      <div><div className="text-sm font-medium">{title}</div><p className="mt-0.5 text-sm text-fg-3">{description}</p></div>
      {children}
    </div>
  );
}

export default function SettingsPage() {
  const { user, signOut } = useAuth();
  const { theme, setTheme } = useTheme();
  const { data: meta } = useMeta();
  const qc = useQueryClient();
  const toast = useToast();
  const [pw, setPw] = useState({ current_password: "", new_password: "" });
  const [confirmDelete, setConfirmDelete] = useState(false);

  const prefs = useMutation({
    mutationFn: (p: Preferences) => api.updatePreferences(p),
    onSuccess: (u) => qc.setQueryData(["me"], u),
    onError: () => toast({ kind: "error", title: "Couldn’t save preference" }),
  });
  const password = useMutation({
    mutationFn: () => api.changePassword(pw),
    onSuccess: () => { setPw({ current_password: "", new_password: "" }); toast({ kind: "success", title: "Password updated" }); },
    onError: (e) => toast({ kind: "error", title: "Password not changed", body: e instanceof ApiError ? e.message : undefined }),
  });
  const del = useMutation({ mutationFn: api.deleteAccount, onSuccess: signOut, onError: () => toast({ kind: "error", title: "Couldn’t delete account" }) });
  if (!user) return null;
  const p = user.preferences;
  const update = (patch: Partial<Preferences>) => prefs.mutate({ ...p, ...patch });

  const themes: { value: ThemeChoice; label: string; icon: typeof Sun }[] = [
    { value: "system", label: "System", icon: Monitor }, { value: "light", label: "Light", icon: Sun }, { value: "dark", label: "Dark", icon: Moon },
  ];

  return (
    <>
      <PageHeader title="Settings" description="Appearance, analysis behavior and account security." />
      <div className="space-y-6">
        <Card>
          <CardHeader title="Appearance" />
          <CardBody>
            <div className="grid max-w-md grid-cols-3 gap-3" role="radiogroup" aria-label="Theme">
              {themes.map((t) => (
                <button key={t.value} role="radio" aria-checked={theme === t.value} onClick={() => { setTheme(t.value); update({ theme: t.value }); }}
                  className={cn("flex flex-col items-center gap-2 rounded-xl border p-4 text-sm transition", theme === t.value ? "border-accent bg-accent-soft text-fg" : "border-border text-fg-2 hover:bg-surface-2")}>
                  <t.icon className="size-5" aria-hidden />{t.label}
                </button>
              ))}
            </div>
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="Analysis" />
          <CardBody className="divide-y divide-border">
            <Row title="AI enhancement" description={meta?.ai_available
              ? `Add narrative feedback and rewrites from the configured AI provider (${meta.ai_provider}). Scores are never affected.`
              : "No AI provider is configured on this server. Analyses use the deterministic engine only."}>
              <Switch id="ai" label="AI enhancement" checked={p.ai_enhancement} onChange={(v) => update({ ai_enhancement: v })} />
            </Row>
            <Row title="Email digest" description="Saved for when email delivery is configured; no emails are sent today.">
              <Switch id="digest" label="Email digest" checked={p.email_digest} onChange={(v) => update({ email_digest: v })} />
            </Row>
          </CardBody>
        </Card>
        <Card>
          <CardHeader title="Password" />
          <CardBody>
            <form className="grid max-w-xl gap-4 sm:grid-cols-2" onSubmit={(e: FormEvent) => { e.preventDefault(); password.mutate(); }}>
              <Field label="Current password" htmlFor="pw-c"><Input id="pw-c" type="password" autoComplete="current-password" value={pw.current_password} onChange={(e) => setPw({ ...pw, current_password: e.target.value })} /></Field>
              <Field label="New password" htmlFor="pw-n" hint="At least 8 characters."><Input id="pw-n" type="password" autoComplete="new-password" value={pw.new_password} onChange={(e) => setPw({ ...pw, new_password: e.target.value })} /></Field>
              <div><Button type="submit" variant="secondary" loading={password.isPending} disabled={!pw.current_password || pw.new_password.length < 8}>Update password</Button></div>
            </form>
          </CardBody>
        </Card>
        <Card className="border-bad/30">
          <CardHeader title="Delete account" description="Permanently delete your account, resumes and analyses. This cannot be undone." />
          <CardBody><Button variant="danger" onClick={() => setConfirmDelete(true)}>Delete account</Button></CardBody>
        </Card>
      </div>
      <ConfirmDialog open={confirmDelete} title="Delete your account?" confirmLabel="Delete everything" loading={del.isPending}
        description="All resumes, analyses and settings will be permanently deleted." onConfirm={() => del.mutate()} onCancel={() => setConfirmDelete(false)} />
    </>
  );
}
