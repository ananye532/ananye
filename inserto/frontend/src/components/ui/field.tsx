import { forwardRef, type InputHTMLAttributes, type ReactNode, type SelectHTMLAttributes, type TextareaHTMLAttributes } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

const control =
  "w-full rounded-lg border border-border bg-surface px-3 text-sm text-fg shadow-card outline-none transition placeholder:text-fg-3 hover:border-border-strong focus:border-accent focus:ring-4 focus:ring-accent/15 disabled:opacity-60 aria-[invalid=true]:border-bad";

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(({ className, ...p }, ref) => (
  <input ref={ref} className={cn(control, "h-10", className)} {...p} />
));
Input.displayName = "Input";

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaHTMLAttributes<HTMLTextAreaElement>>(({ className, ...p }, ref) => (
  <textarea ref={ref} className={cn(control, "min-h-32 resize-y py-2.5 leading-relaxed", className)} {...p} />
));
Textarea.displayName = "Textarea";

export const Select = forwardRef<HTMLSelectElement, SelectHTMLAttributes<HTMLSelectElement>>(({ className, children, ...p }, ref) => (
  <div className="relative">
    <select ref={ref} className={cn(control, "h-10 appearance-none pr-9", className)} {...p}>{children}</select>
    <ChevronDown className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-fg-3" aria-hidden />
  </div>
));
Select.displayName = "Select";

export function Field({ label, htmlFor, hint, error, children, className }: {
  label: ReactNode; htmlFor: string; hint?: ReactNode; error?: string | null; children: ReactNode; className?: string;
}) {
  return (
    <div className={cn("space-y-1.5", className)}>
      <label htmlFor={htmlFor} className="block text-[13px] font-medium text-fg">{label}</label>
      {children}
      {error ? <p className="text-xs text-bad-fg" role="alert">{error}</p> : hint ? <p className="text-xs text-fg-3">{hint}</p> : null}
    </div>
  );
}
