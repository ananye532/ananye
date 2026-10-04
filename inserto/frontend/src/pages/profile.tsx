import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { Field, Input, Select } from "@/components/ui/field";
import { PageHeader } from "@/components/ui/misc";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useMeta } from "@/lib/queries";
import { useToast } from "@/lib/toast";
import { formatDate, initials } from "@/lib/utils";

export default function ProfilePage() {
  const { user } = useAuth();
  const { data: meta } = useMeta();
  const qc = useQueryClient();
  const toast = useToast();
  const [form, setForm] = useState({ name: "", headline: "", target_role: "" });
  useEffect(() => { if (user) setForm({ name: user.name, headline: user.headline ?? "", target_role: user.target_role ?? "" }); }, [user]);

  const save = useMutation({
    mutationFn: () => api.updateProfile({ name: form.name.trim(), headline: form.headline, target_role: form.target_role }),
    onSuccess: (u) => { qc.setQueryData(["me"], u); toast({ kind: "success", title: "Profile saved" }); },
    onError: (e) => toast({ kind: "error", title: "Couldn’t save profile", body: e instanceof ApiError ? e.message : undefined }),
  });
  if (!user) return null;
  const dirty = form.name !== user.name || form.headline !== (user.headline ?? "") || form.target_role !== (user.target_role ?? "");

  return (
    <>
      <PageHeader title="Profile" description="Your details and career target. The target role personalizes skill-gap analysis." />
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="p-6 text-center">
          <div className="mx-auto grid size-20 place-items-center rounded-full bg-accent-soft text-2xl font-semibold text-accent-fg">{initials(user.name)}</div>
          <div className="mt-4 text-lg font-semibold">{user.name}</div>
          <div className="text-sm text-fg-3">{user.headline || user.email}</div>
          <div className="mt-4 text-xs text-fg-3">Member since {formatDate(user.created_at)}</div>
        </Card>
        <Card className="lg:col-span-2">
          <CardHeader title="Details" />
          <CardBody>
            <form className="space-y-4" onSubmit={(e: FormEvent) => { e.preventDefault(); if (form.name.trim()) save.mutate(); }}>
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="Full name" htmlFor="p-name" error={!form.name.trim() ? "Name is required." : null}><Input id="p-name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></Field>
                <Field label="Email" htmlFor="p-email" hint="Email changes aren’t supported yet."><Input id="p-email" value={user.email} disabled /></Field>
              </div>
              <Field label="Headline" htmlFor="p-head" hint="e.g. Backend engineer focused on payments infrastructure"><Input id="p-head" maxLength={200} value={form.headline} onChange={(e) => setForm({ ...form, headline: e.target.value })} /></Field>
              <Field label="Target role" htmlFor="p-role" hint="Used by default when an analysis doesn’t specify one.">
                <Select id="p-role" value={form.target_role} onChange={(e) => setForm({ ...form, target_role: e.target.value })}>
                  <option value="">Auto-detect from resume</option>
                  {meta?.roles.map((r) => <option key={r} value={r}>{r}</option>)}
                </Select>
              </Field>
              <div className="flex justify-end"><Button type="submit" loading={save.isPending} disabled={!dirty || !form.name.trim()}>Save changes</Button></div>
            </form>
          </CardBody>
        </Card>
      </div>
    </>
  );
}
