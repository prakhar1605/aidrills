"use client";

import { useHydrated, useProgress } from "@/lib/store";
import { cn } from "@/lib/utils";

const LABEL = {
  solved: "Solved",
  attempted: "Attempted",
  unsolved: "Not started",
} as const;

/** Progress lives in localStorage, so this renders neutral until hydration. */
export function StatusDot({ slug }: { slug: string }) {
  const progress = useProgress(slug);
  const hydrated = useHydrated();
  const status = hydrated ? progress.status : "unsolved";

  return (
    <span
      title={LABEL[status]}
      className={cn(
        "inline-block h-1.5 w-1.5 shrink-0 rounded-full",
        status === "solved"
          ? "bg-pass"
          : status === "attempted"
            ? "bg-warn"
            : "bg-line-strong",
      )}
    >
      <span className="sr-only">{LABEL[status]}</span>
    </span>
  );
}
