import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const badgeVariants = cva("inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium [&_svg]:size-3", {
  variants: {
    variant: {
      neutral: "bg-surface-2 text-fg-2 ring-1 ring-inset ring-border",
      accent: "bg-accent-soft text-accent-fg",
      good: "bg-good-soft text-good-fg",
      warn: "bg-warn-soft text-warn-fg",
      bad: "bg-bad-soft text-bad-fg",
      outline: "text-fg-2 ring-1 ring-inset ring-border-strong",
    },
  },
  defaultVariants: { variant: "neutral" },
});

export function Badge({ className, variant, ...props }: HTMLAttributes<HTMLSpanElement> & VariantProps<typeof badgeVariants>) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
