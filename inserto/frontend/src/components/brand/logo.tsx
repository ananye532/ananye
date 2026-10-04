import { cn } from "@/lib/utils";

export function LogoMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={cn("size-7", className)} aria-hidden>
      <rect width="32" height="32" rx="8" fill="var(--primary)" />
      <path d="M11 9h10M16 9v14M11 23h10" stroke="var(--primary-fg)" strokeWidth="2.6" strokeLinecap="round" />
      <circle cx="24" cy="9" r="2.4" fill="var(--accent)" />
    </svg>
  );
}

export function Logo({ className }: { className?: string }) {
  return (
    <span className={cn("inline-flex items-center gap-2 font-semibold tracking-tight", className)}>
      <LogoMark />
      <span className="text-[17px]">Inserto</span>
    </span>
  );
}
