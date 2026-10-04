import { ArrowRight, CheckCircle2 } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";
import { Logo } from "@/components/brand/logo";
import { Button } from "@/components/ui/button";
import { Field, Input } from "@/components/ui/field";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

function AuthFrame({ title, subtitle, children, footer }: { title: string; subtitle: string; children: React.ReactNode; footer: React.ReactNode }) {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="flex flex-col px-4 py-8 sm:px-10">
        <Link to="/" aria-label="Inserto home"><Logo /></Link>
        <div className="mx-auto flex w-full max-w-sm flex-1 flex-col justify-center py-12">
          <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
          <p className="mt-1.5 text-fg-2">{subtitle}</p>
          <div className="mt-8">{children}</div>
          <p className="mt-6 text-sm text-fg-3">{footer}</p>
        </div>
      </div>
      <div className="relative hidden overflow-hidden border-l border-border bg-surface lg:block">
        <div className="bg-grid absolute inset-0 opacity-70" aria-hidden />
        <div className="relative flex h-full flex-col justify-center px-14">
          <blockquote className="max-w-md text-2xl font-medium leading-snug tracking-tight">
            “Recruiters skim a resume in seconds. Inserto shows you what survives that skim — and what doesn’t.”
          </blockquote>
          <ul className="mt-10 space-y-3 text-fg-2">
            {["ATS compatibility and parse confidence", "Skills, keywords and job match", "Prioritized, explainable fixes"].map((t) => (
              <li key={t} className="flex items-center gap-2.5"><CheckCircle2 className="size-4 text-good" aria-hidden />{t}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export function Login() {
  const { user, signIn } = useAuth();
  const location = useLocation();
  const from = (location.state as { from?: string } | null)?.from ?? "/app";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  if (user) return <Navigate to={from} replace />;

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      signIn(await api.login({ email, password }));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthFrame title="Welcome back" subtitle="Sign in to your Inserto workspace."
      footer={<>New to Inserto? <Link to="/register" className="font-medium text-fg hover:underline">Create an account</Link></>}>
      <form onSubmit={submit} className="space-y-4" noValidate>
        <Field label="Email" htmlFor="email"><Input id="email" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></Field>
        <Field label="Password" htmlFor="password"><Input id="password" type="password" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} /></Field>
        {error && <p className="rounded-lg bg-bad-soft px-3 py-2 text-sm text-bad-fg" role="alert">{error}</p>}
        <Button type="submit" className="w-full" size="lg" loading={busy}>Sign in <ArrowRight /></Button>
      </form>
    </AuthFrame>
  );
}

export function Register() {
  const { user, signIn } = useAuth();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  // New accounts land on the upload flow; this also covers the redirect right after sign-up.
  if (user) return <Navigate to="/app/new" replace />;
  const weak = form.password.length > 0 && form.password.length < 8;

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (form.password.length < 8) return setError("Use at least 8 characters for your password.");
    setError(null);
    setBusy(true);
    try {
      signIn(await api.register(form));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthFrame title="Create your account" subtitle="Your first analysis takes under a minute."
      footer={<>Already have an account? <Link to="/login" className="font-medium text-fg hover:underline">Sign in</Link></>}>
      <form onSubmit={submit} className="space-y-4" noValidate>
        <Field label="Full name" htmlFor="name"><Input id="name" autoComplete="name" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></Field>
        <Field label="Email" htmlFor="email"><Input id="email" type="email" autoComplete="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></Field>
        <Field label="Password" htmlFor="password" hint="At least 8 characters." error={weak ? "Too short — use at least 8 characters." : null}>
          <Input id="password" type="password" autoComplete="new-password" required aria-invalid={weak} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        </Field>
        {error && <p className="rounded-lg bg-bad-soft px-3 py-2 text-sm text-bad-fg" role="alert">{error}</p>}
        <Button type="submit" className="w-full" size="lg" loading={busy}>Create account <ArrowRight /></Button>
      </form>
    </AuthFrame>
  );
}
