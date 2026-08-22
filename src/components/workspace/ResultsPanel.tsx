"use client";

import { useState } from "react";

import { summarize, type RunOutcome, type TestResult } from "@/lib/pyodide/client";
import { cn, formatMs } from "@/lib/utils";

const GLYPH: Record<TestResult["status"], string> = {
  passed: "✓",
  failed: "✗",
  error: "!",
};

const TONE: Record<TestResult["status"], string> = {
  passed: "text-pass",
  failed: "text-fail",
  error: "text-warn",
};

type Props = {
  outcome: RunOutcome | null;
  running: boolean;
  /** Nothing has been run yet on this problem in this session. */
  hint?: string;
};

export function ResultsPanel({ outcome, running, hint }: Props) {
  const [tab, setTab] = useState<"results" | "console">("results");
  const [expanded, setExpanded] = useState<string | null>(null);

  const results = outcome?.results ?? [];
  const stats = summarize(results);
  const stdout = outcome?.stdout ?? "";

  return (
    <section className="flex min-h-0 flex-1 flex-col border-t border-line bg-sunken">
      <div className="flex h-9 shrink-0 items-center gap-1 border-b border-line px-2">
        {(["results", "console"] as const).map((name) => (
          <button
            key={name}
            onClick={() => setTab(name)}
            className={cn(
              "rounded px-2.5 py-1 font-mono text-xs capitalize transition-colors",
              tab === name ? "bg-raised text-ink" : "text-muted hover:text-ink",
            )}
          >
            {name}
            {name === "console" && stdout ? " ·" : ""}
          </button>
        ))}

        <div className="ml-auto pr-1 font-mono text-xs">
          {running ? (
            <span className="text-muted">running…</span>
          ) : outcome ? (
            <SummaryLine outcome={outcome} />
          ) : null}
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-auto">
        {tab === "console" ? (
          <pre className="p-3 font-mono text-xs leading-relaxed whitespace-pre-wrap text-ink/85">
            {stdout || <span className="text-muted">Nothing printed.</span>}
          </pre>
        ) : outcome?.error ? (
          <pre className="p-3 font-mono text-xs leading-relaxed whitespace-pre-wrap text-fail">
            {outcome.error}
          </pre>
        ) : results.length === 0 ? (
          <p className="p-3 font-mono text-xs text-muted">
            {running ? "Running the tests…" : (hint ?? "Run the tests to see results.")}
          </p>
        ) : (
          <ul>
            {results.map((result, index) => {
              const open = expanded === result.name;
              const clickable = Boolean(result.message);
              return (
                <li
                  key={result.name}
                  className="result-row border-b border-line/60 last:border-0"
                  style={{ animationDelay: `${Math.min(index, 12) * 22}ms` }}
                >
                  <button
                    onClick={() => clickable && setExpanded(open ? null : result.name)}
                    disabled={!clickable}
                    className={cn(
                      "flex w-full items-baseline gap-3 px-3 py-1.5 text-left font-mono text-xs",
                      clickable && "hover:bg-raised/60",
                      !clickable && "cursor-default",
                    )}
                  >
                    <span className={cn("w-3 shrink-0", TONE[result.status])} aria-hidden>
                      {GLYPH[result.status]}
                    </span>
                    <span className="sr-only">{result.status}: </span>
                    <span className="min-w-0 flex-1 truncate text-ink/90">{result.name}</span>
                    <span className="shrink-0 text-muted">{formatMs(result.durationMs)}</span>
                  </button>
                  {open && (
                    <pre className="border-t border-line/60 bg-surface/60 px-3 py-2 pl-9 font-mono text-[11px] leading-relaxed whitespace-pre-wrap text-muted">
                      {result.message}
                    </pre>
                  )}
                </li>
              );
            })}
            {stats.total > 0 && (
              <li className="px-3 py-2 font-mono text-xs text-muted">
                <SummaryLine outcome={outcome!} verbose />
              </li>
            )}
          </ul>
        )}
      </div>
    </section>
  );
}

function SummaryLine({ outcome, verbose = false }: { outcome: RunOutcome; verbose?: boolean }) {
  const stats = summarize(outcome.results);
  if (stats.total === 0) return <span className="text-fail">error</span>;

  const parts = [
    <span key="p" className={stats.passed ? "text-pass" : undefined}>
      {stats.passed} passed
    </span>,
  ];
  if (stats.failed) {
    parts.push(
      <span key="f" className="text-fail">
        {stats.failed} failed
      </span>,
    );
  }
  if (stats.errored) {
    parts.push(
      <span key="e" className="text-warn">
        {stats.errored} error{stats.errored === 1 ? "" : "s"}
      </span>,
    );
  }
  if (verbose) {
    const total = outcome.results.reduce((sum, result) => sum + result.durationMs, 0);
    parts.push(<span key="t">{formatMs(total)}</span>);
  }

  return (
    <span>
      {parts.map((part, index) => (
        <span key={index}>
          {index > 0 && <span className="text-line-strong"> · </span>}
          {part}
        </span>
      ))}
    </span>
  );
}
