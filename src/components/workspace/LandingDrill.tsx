"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Editor } from "@/components/workspace/Editor";
import { ResultsPanel } from "@/components/workspace/ResultsPanel";
import { RuntimeChip } from "@/components/workspace/RuntimeChip";
import { Timer } from "@/components/workspace/Timer";
import { track as analytics } from "@/lib/analytics";
import { summarize, usePyRunner, type RunOutcome } from "@/lib/pyodide/client";
import { formatClock } from "@/lib/utils";

type Props = {
  slug: string;
  title: string;
  timeBudgetMin: number;
  entryPoint: string;
  starter: string;
  tests: string;
  packages: readonly string[];
};

/**
 * The landing hero is the product: a real drill, in the real editor, on the
 * real runtime. The clock is armed at the time budget and starts on the first
 * keystroke.
 */
export function LandingDrill({
  slug,
  title,
  timeBudgetMin,
  entryPoint,
  starter,
  tests,
  packages,
}: Props) {
  const runner = usePyRunner();
  const [code, setCode] = useState(starter);
  const [outcome, setOutcome] = useState<RunOutcome | null>(null);
  const [running, setRunning] = useState(false);
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [solvedInMs, setSolvedInMs] = useState<number | null>(null);
  const armed = useRef(false);

  const { warmup } = runner;
  useEffect(() => {
    warmup();
  }, [warmup]);

  const arm = useCallback(() => {
    if (armed.current) return;
    armed.current = true;
    setStartedAt(Date.now());
  }, []);

  const run = useCallback(async () => {
    if (running) return;
    arm();
    setRunning(true);
    analytics("run_tests", { slug, track: "landing" });

    const result = await runner.run({ code, tests, packages });
    setRunning(false);
    setOutcome(result);

    if (summarize(result.results).allPassed) {
      setSolvedInMs(Date.now() - (startedAt ?? Date.now()));
      analytics("all_passed", { slug, track: "landing" });
    }
  }, [arm, code, packages, running, runner, slug, startedAt, tests]);

  return (
    <div className="overflow-hidden rounded-xl border border-line bg-raised">
      <div className="flex items-center gap-3 border-b border-line px-3 py-2">
        <Link
          href={`/problems/${slug}`}
          className="font-mono text-xs text-ink transition-colors hover:text-white"
        >
          {title}
        </Link>
        <span className="hidden font-mono text-[11px] text-muted sm:inline">
          {entryPoint}
        </span>

        <div className="ml-auto flex items-center gap-3">
          <RuntimeChip status={runner.status} stage={runner.stage} />
          {startedAt ? (
            <Timer startedAt={startedAt} budgetMin={timeBudgetMin} />
          ) : (
            <span className="font-mono text-xs tabular-nums text-muted">
              {formatClock(timeBudgetMin * 60)}
            </span>
          )}
          <Button
            size="sm"
            variant="primary"
            onClick={run}
            disabled={running || runner.status === "loading"}
          >
            {running ? "Running…" : "Run tests"}
          </Button>
        </div>
      </div>

      <div className="flex h-[26rem] flex-col">
        <div className="min-h-0 flex-1 overflow-hidden">
          <Editor
            value={code}
            onChange={(value) => {
              arm();
              setCode(value);
            }}
            onRun={run}
            fontSize={13}
            resetSignal={0}
          />
        </div>
        <div className="flex h-44 flex-col">
          <ResultsPanel
            outcome={outcome}
            running={running}
            hint={
              runner.status === "loading"
                ? "Loading CPython into this tab. No server involved."
                : `Implement ${entryPoint}, then hit Run. ⌘⏎ works too.`
            }
          />
        </div>
      </div>

      {solvedInMs !== null && (
        <div className="border-t border-line bg-pass/10 px-3 py-2 font-mono text-xs text-pass">
          All tests passed in {formatClock(solvedInMs / 1000)} —{" "}
          <Link href="/problems" className="underline underline-offset-2">
            the rest of the drills are this way
          </Link>
        </div>
      )}
    </div>
  );
}
