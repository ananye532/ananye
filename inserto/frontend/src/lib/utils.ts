import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export type Tone = "good" | "warn" | "bad";

export function scoreTone(score: number): Tone {
  if (score >= 75) return "good";
  if (score >= 55) return "warn";
  return "bad";
}

export function toneLabel(score: number): string {
  if (score >= 85) return "Excellent";
  if (score >= 75) return "Strong";
  if (score >= 55) return "Fair";
  return "Needs work";
}

export const toneText: Record<Tone, string> = { good: "text-good-fg", warn: "text-warn-fg", bad: "text-bad-fg" };
export const toneBg: Record<Tone, string> = { good: "bg-good-soft", warn: "bg-warn-soft", bad: "bg-bad-soft" };
export const toneVar: Record<Tone, string> = { good: "var(--good)", warn: "var(--warn)", bad: "var(--bad)" };

const dateFmt = new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" });
const timeFmt = new Intl.DateTimeFormat(undefined, { hour: "numeric", minute: "2-digit" });

export function formatDate(iso: string) {
  return dateFmt.format(new Date(iso));
}

export function formatDateTime(iso: string) {
  const d = new Date(iso);
  return `${dateFmt.format(d)} · ${timeFmt.format(d)}`;
}

export function relativeTime(iso: string) {
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 86400 * 7) return `${Math.floor(diff / 86400)}d ago`;
  return formatDate(iso);
}

export function pct(ratio: number) {
  return `${Math.round(ratio * 100)}%`;
}

export function initials(name: string) {
  return name.split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0]!.toUpperCase()).join("");
}
