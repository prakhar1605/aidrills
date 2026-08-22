"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";

import { DifficultyBadge, TrackBadge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Editor } from "@/components/workspace/Editor";
import { HintsTab } from "@/components/workspace/HintsTab";
import { ResultsPanel } from "@/components/workspace/ResultsPanel";
import { RuntimeChip } from "@/components/workspace/RuntimeChip";
import { SolutionTab } from "@/components/workspace/SolutionTab";
import { Timer } from "@/components/workspace/Timer";
import { track as analytics } from "@/lib/analytics";
import { summarize, usePyRunner, type RunOutcome } from "@/lib/pyodide/client";
import type { Problem } from "@/lib/schema";
import { useHydrated, useProgress, useStore } from "@/lib/store";
import { cn, formatClock } from "@/lib/utils";

export type WorkspaceProblem = Pick<
  Problem,
  | "id"
  | "slug"
  | "title"
  | "track"
  | "difficulty"
  | "timeBudgetMin"
  | "packages"
  | "entryPoint"
  | "companies"
  | "starter"
  | "tests"
  | "solution"
>;

type Props = {
  problem: WorkspaceProblem;
  statement: React.ReactNode;
  hints: React.ReactNode[];
  next?: { slug: string; title: string };
};

type LeftTab = "description" | "hints" | "solution";

const DRAFT_DEBOUNCE_MS = 500;

export function Workspace({ problem, statement, hints, next }: Props) {
  const runner = usePyRunner();
  const hydrated = useHydrated();
  const progress = useProgress(problem.slug);

  const setDraft = useStore((state) => state.setDraft);
  const clearDraft = useStore((state) => state.clearDraft);
  const recordRun = useStore((state) => state.recordRun);
  const revealHint = useStore((state) => state.revealHint);
  const fontSize = useStore((state) => state.settings.fontSize);

  // null until the candidate types: the document then comes from the saved
  // draft, which is only readable once localStorage has been rehydrated.
  const savedDraft = useStore((state) => state.drafts[problem.slug]);
  const [edited, setEdited] = useState<string | null>(null);
  const code = edited ?? savedDraft ?? problem.starter;

  const [resetSignal, bumpReset] = useState(0);
  const [tab, setTab] = useState<LeftTab>("description");
  const [outcome, setOutcome] = useState<RunOutcome | null>(null);
  const [running, setRunning] = useState(false);
  const [interviewStartedAt, setInterviewStartedAt] = useState<number | null>(null);
  const [solvedInMs, setSolvedInMs] = useState<number | null>(null);
  const [shareLabel, setShareLabel] = useState("Share");
  const [split, setSplit] = useState(44);
  const [shortcuts, setShortcuts] = useState(false);

  const startedAt = useRef(0);

  const { warmup } = runner;
  useEffect(() => {
    startedAt.current = Date.now();
    warmup();
  }, [warmup]);

  // Autosave, debounced -- the store writes straight through to localStorage.
  useEffect(() => {
    if (edited === null || edited === problem.starter) return;
    const id = setTimeout(() => setDraft(problem.slug, edited), DRAFT_DEBOUNCE_MS);
    return () => clearTimeout(id);
  }, [edited, problem.slug, problem.starter, setDraft]);

  const run = useCallback(async () => {
    if (running) return;
    setRunning(true);
    analytics("run_tests", {
      slug: problem.slug,
      track: problem.track,
      difficulty: problem.difficulty,
    });

    const result = await runner.run({
      code,
      tests: problem.tests,
      packages: problem.packages,
    });

    setRunning(false);
    setOutcome(result);

    const stats = summarize(result.results);
    const began = interviewStartedAt ?? (startedAt.current || Date.now());
    const elapsed = Date.now() - began;
    recordRun(problem.slug, stats.allPassed, elapsed);

    if (stats.allPassed) {
      setSolvedInMs((previous) => previous ?? elapsed);
      analytics("all_passed", {
        slug: problem.slug,
        track: problem.track,
        difficulty: problem.difficulty,
      });
    }
  }, [code, interviewStartedAt, problem, recordRun, runner, running]);

  const resetToStarter = useCallback(() => {
    setEdited(problem.starter);
    clearDraft(problem.slug);
    bumpReset((value) => value + 1);
    setOutcome(null);
  }, [clearDraft, problem.slug, problem.starter]);

  const toggleInterview = useCallback(() => {
    setInterviewStartedAt((current) => {
      if (current) return null;
      analytics("interview_mode_start", { slug: problem.slug, track: problem.track });
      return Date.now();
    });
    setTab("description");
  }, [problem.slug, problem.track]);

  const share = useCallback(async () => {
    const time = solvedInMs ? ` in ${formatClock(solvedInMs / 1000)}` : "";
    const text = `${solvedInMs ? "Solved" : "Drilling"} ${problem.title}${time} — ${window.location.href}`;
    try {
      await navigator.clipboard.writeText(text);
      setShareLabel("Copied");
      setTimeout(() => setShareLabel("Share"), 1600);
    } catch {
      setShareLabel("Copy failed");
      setTimeout(() => setShareLabel("Share"), 1600);
    }
    analytics("share", { slug: problem.slug, track: problem.track });
  }, [problem.slug, problem.title, problem.track, solvedInMs]);

  // `?` opens the shortcut sheet; Escape closes it. Ignore keys typed into the
  // editor or any other field.
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      if (target?.closest("input, textarea, .cm-editor, [contenteditable]")) return;
      if (event.key === "?") setShortcuts(true);
      if (event.key === "Escape") setShortcuts(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const onDividerDrag = useCallback((event: React.PointerEvent<HTMLDivElement>) => {
    event.preventDefault();
    const container = event.currentTarget.parentElement;
    if (!container) return;
    const move = (pointer: PointerEvent) => {
      const bounds = container.getBoundingClientRect();
      const pct = ((pointer.clientX - bounds.left) / bounds.width) * 100;
      setSplit(Math.min(70, Math.max(25, pct)));
    };
    const up = () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
  }, []);

  const solved = progress.status === "solved";
  const interviewMode = interviewStartedAt !== null;

  return (
    <div className="flex flex-1 flex-col">
      {/* ---- toolbar ---- */}
      <div className="flex flex-wrap items-center gap-x-3 gap-y-2 border-b border-line px-5 py-2.5">
        <span className="font-mono text-xs text-muted">
          {String(problem.id).padStart(2, "0")}
        </span>
        <h1 className="text-sm font-medium">{problem.title}</h1>
        <TrackBadge track={problem.track} />
        <DifficultyBadge difficulty={problem.difficulty} />
        {hydrated && solved && (
          <span className="font-mono text-[11px] text-pass">solved</span>
        )}

        <div className="ml-auto flex items-center gap-2">
          <RuntimeChip status={runner.status} stage={runner.stage} className="mr-1" />

          {interviewMode ? (
            <>
              <Timer startedAt={interviewStartedAt} budgetMin={problem.timeBudgetMin} />
              <Button size="sm" variant="ghost" onClick={toggleInterview}>
                End
              </Button>
            </>
          ) : (
            <Button
              size="sm"
              variant="ghost"
              onClick={toggleInterview}
              title={`Countdown from ${problem.timeBudgetMin} minutes, hints disabled`}
              className="hidden lg:inline-flex"
            >
              Interview mode
            </Button>
          )}

          <Button size="sm" variant="ghost" onClick={share}>
            {shareLabel}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={resetToStarter}
            className="hidden lg:inline-flex"
          >
            Reset
          </Button>
          <Button
            size="sm"
            variant="primary"
            onClick={run}
            disabled={running || runner.status === "loading"}
            className="hidden lg:inline-flex"
          >
            {running ? "Running…" : "Run"}
            <kbd className="ml-1 font-mono text-[10px] opacity-70">⌘⏎</kbd>
          </Button>
        </div>
      </div>

      {solvedInMs !== null && (
        <div className="border-b border-line bg-pass/10 px-5 py-2 font-mono text-xs text-pass">
          All tests passed — {formatClock(solvedInMs / 1000)}
          {next && (
            <>
              {" · "}
              <Link href={`/problems/${next.slug}`} className="underline underline-offset-2">
                next: {next.title}
              </Link>
            </>
          )}
        </div>
      )}

      {/* ---- panes ---- */}
      <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
        <div
          className="min-h-0 overflow-y-auto px-5 py-6 lg:px-6"
          style={{ flexBasis: `${split}%` }}
        >
          <div className="mb-5 flex items-center gap-1 border-b border-line">
            {(["description", "hints", "solution"] as const).map((name) => (
              <button
                key={name}
                onClick={() => setTab(name)}
                className={cn(
                  "-mb-px border-b px-3 py-2 text-xs capitalize transition-colors",
                  tab === name
                    ? "border-ink text-ink"
                    : "border-transparent text-muted hover:text-ink",
                )}
              >
                {name}
                {name === "hints" && progress.hintsUsed > 0 && (
                  <span className="ml-1.5 font-mono text-[10px] text-muted">
                    {progress.hintsUsed}/{hints.length}
                  </span>
                )}
              </button>
            ))}
          </div>

          {tab === "description" && (
            <>
              {statement}
              {problem.companies.length > 0 && (
                <p className="mt-8 border-t border-line pt-4 font-mono text-[11px] text-muted">
                  Reported at {problem.companies.join(", ")} · budget{" "}
                  {problem.timeBudgetMin} min · entry point {problem.entryPoint}
                </p>
              )}
            </>
          )}

          {tab === "hints" && (
            <HintsTab
              hints={hints}
              revealed={progress.hintsUsed}
              locked={interviewMode}
              onReveal={(index) => {
                revealHint(problem.slug, index);
                analytics("hint_used", { slug: problem.slug, track: problem.track });
              }}
            />
          )}

          {tab === "solution" && (
            <SolutionTab
              solution={problem.solution}
              onReveal={() =>
                analytics("solution_revealed", { slug: problem.slug, track: problem.track })
              }
              onLoadIntoEditor={() => {
                setEdited(problem.solution);
                bumpReset((value) => value + 1);
                setTab("description");
              }}
            />
          )}

          <p className="mt-8 font-mono text-[11px] text-muted lg:hidden">
            Open this on a desktop to run the code — the editor needs a keyboard.
          </p>
        </div>

        <div
          role="separator"
          aria-orientation="vertical"
          onPointerDown={onDividerDrag}
          className="hidden w-px shrink-0 cursor-col-resize bg-line transition-colors hover:bg-accent lg:block"
        />

        <div className="hidden min-h-0 flex-1 flex-col lg:flex">
          <div className="min-h-0 flex-1 overflow-hidden">
            {hydrated ? (
              <Editor
                value={code}
                onChange={setEdited}
                onRun={run}
                fontSize={fontSize}
                resetSignal={resetSignal}
              />
            ) : (
              <div className="h-full animate-pulse bg-sunken" />
            )}
          </div>
          <div className="flex h-2/5 min-h-[9rem] flex-col">
            <ResultsPanel
              outcome={outcome}
              running={running}
              hint={
                runner.status === "loading"
                  ? "Loading the Python runtime…"
                  : `Write ${problem.entryPoint}, then run with ⌘⏎.`
              }
            />
          </div>
        </div>
      </div>

      {shortcuts && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-surface/80 p-4"
          onClick={() => setShortcuts(false)}
        >
          <div
            className="w-full max-w-sm rounded-lg border border-line bg-raised p-5"
            onClick={(event) => event.stopPropagation()}
          >
            <h2 className="text-sm font-medium">Keyboard shortcuts</h2>
            <dl className="mt-4 flex flex-col gap-2 font-mono text-xs">
              {[
                ["⌘ / Ctrl + ⏎", "Run the tests"],
                ["Tab", "Indent inside the editor"],
                ["?", "This sheet"],
                ["Esc", "Close"],
              ].map(([key, description]) => (
                <div key={key} className="flex justify-between gap-4">
                  <dt className="text-ink">{key}</dt>
                  <dd className="text-muted">{description}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      )}
    </div>
  );
}
