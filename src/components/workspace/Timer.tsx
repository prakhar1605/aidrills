"use client";

import { useEffect, useState } from "react";

import { cn, formatClock } from "@/lib/utils";

/** Counts down from the problem's time budget, then counts the overrun up. */
export function Timer({ startedAt, budgetMin }: { startedAt: number; budgetMin: number }) {
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 500);
    return () => clearInterval(id);
  }, []);

  const elapsed = Math.floor((now - startedAt) / 1000);
  const remaining = budgetMin * 60 - elapsed;
  const over = remaining < 0;

  return (
    <span
      className={cn(
        "font-mono text-xs tabular-nums",
        over ? "text-fail" : remaining < 120 ? "text-warn" : "text-ink",
      )}
      aria-live="off"
    >
      {over ? `+${formatClock(-remaining)}` : formatClock(remaining)}
    </span>
  );
}
