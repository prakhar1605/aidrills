"use client";

import type { LoadStage, RunnerStatus } from "@/lib/pyodide/client";
import { cn } from "@/lib/utils";

const STAGE_LABEL: Record<LoadStage, string> = {
  downloading: "downloading",
  initializing: "starting",
  packages: "loading numpy",
};

export function RuntimeChip({
  status,
  stage,
  className,
}: {
  status: RunnerStatus;
  stage: LoadStage | null;
  className?: string;
}) {
  const label =
    status === "loading"
      ? (stage ? STAGE_LABEL[stage] : "loading")
      : status === "running"
        ? "running"
        : status === "timeout"
          ? "timed out"
          : status === "error"
            ? "failed"
            : status === "ready"
              ? "ready"
              : "idle";

  const dot =
    status === "ready"
      ? "bg-pass"
      : status === "error" || status === "timeout"
        ? "bg-fail"
        : status === "idle"
          ? "bg-line-strong"
          : "bg-warn";

  return (
    <span
      className={cn("flex items-center gap-1.5 font-mono text-[11px] text-muted", className)}
      title="Your code runs on Pyodide in this tab. Nothing is sent anywhere."
    >
      <span
        className={cn(
          "inline-block h-1.5 w-1.5 rounded-full",
          dot,
          (status === "loading" || status === "running") && "animate-pulse",
        )}
        aria-hidden
      />
      <span className="hidden sm:inline">Python runtime · </span>
      {label}
    </span>
  );
}
