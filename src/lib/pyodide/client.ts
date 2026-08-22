"use client";

import { useCallback, useSyncExternalStore } from "react";

import { PYODIDE_INDEX_URL, PY_RUNTIME_FILES, RUN_TIMEOUT_MS, WORKER_URL } from "./const";

/* -------------------------------------------------------------------------
 * The worker message contract. public/pyodide-worker.js implements the other
 * side of exactly these shapes -- change one, change both.
 * ---------------------------------------------------------------------- */

export type InitMessage = { type: "init"; indexURL: string; runtimeFiles: readonly string[] };
export type RunMessage = {
  type: "run";
  runId: number;
  code: string;
  tests: string;
  packages: readonly string[];
};
export type ToWorker = InitMessage | RunMessage;

export type TestStatus = "passed" | "failed" | "error";

export type TestResult = {
  name: string;
  status: TestStatus;
  message: string;
  durationMs: number;
};

export type ProgressMessage = { type: "progress"; stage: LoadStage };
export type ReadyMessage = { type: "ready" };
export type FatalMessage = { type: "fatal"; error: string };
export type ResultMessage = {
  type: "result";
  runId: number;
  results: TestResult[];
  stdout: string;
  error: string | null;
};
export type FromWorker = ProgressMessage | ReadyMessage | FatalMessage | ResultMessage;

/* ---------------------------------------------------------------------- */

export type LoadStage = "downloading" | "initializing" | "packages";
export type RunnerStatus = "idle" | "loading" | "ready" | "running" | "error" | "timeout";

export type RunnerState = {
  status: RunnerStatus;
  stage: LoadStage | null;
  error: string | null;
};

export type RunOutcome = {
  results: TestResult[];
  stdout: string;
  error: string | null;
  timedOut: boolean;
  durationMs: number;
};

const IDLE: RunnerState = { status: "idle", stage: null, error: null };

/**
 * Owns the single Pyodide worker for the tab.
 *
 * `warmup()` is fired on problem-page mount so the several megabytes of
 * WebAssembly are already there by the time anyone clicks Run.
 */
class PyRunner {
  private worker: Worker | null = null;
  private ready: Promise<void> | null = null;
  private state: RunnerState = IDLE;
  private subscribers = new Set<() => void>();
  private nextRunId = 1;
  private pending: {
    id: number;
    startedAt: number;
    timer: ReturnType<typeof setTimeout>;
    resolve: (outcome: RunOutcome) => void;
  } | null = null;

  subscribe = (callback: () => void) => {
    this.subscribers.add(callback);
    return () => this.subscribers.delete(callback);
  };

  getSnapshot = (): RunnerState => this.state;

  private setState(patch: Partial<RunnerState>) {
    this.state = { ...this.state, ...patch };
    this.subscribers.forEach((callback) => callback());
  }

  /** Start loading the runtime. Safe to call repeatedly. */
  warmup(): Promise<void> {
    if (!this.ready) {
      this.ready = this.boot().catch((error: unknown) => {
        this.ready = null;
        this.setState({ status: "error", stage: null, error: String(error) });
        throw error;
      });
    }
    return this.ready;
  }

  private boot(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.setState({ status: "loading", stage: "downloading", error: null });
      const worker = new Worker(WORKER_URL);
      this.worker = worker;

      worker.onmessage = (event: MessageEvent<FromWorker>) => {
        const message = event.data;
        switch (message.type) {
          case "progress":
            this.setState({ stage: message.stage });
            break;
          case "ready":
            this.setState({ status: "ready", stage: null, error: null });
            resolve();
            break;
          case "fatal":
            reject(new Error(message.error));
            break;
          case "result":
            this.settle(message);
            break;
        }
      };

      worker.onerror = (event) => {
        reject(new Error(event.message || "the Python worker failed to start"));
      };

      const init: InitMessage = {
        type: "init",
        indexURL: PYODIDE_INDEX_URL,
        runtimeFiles: PY_RUNTIME_FILES,
      };
      worker.postMessage(init);
    });
  }

  private settle(message: ResultMessage) {
    const pending = this.pending;
    if (!pending || pending.id !== message.runId) return; // a stale run; drop it
    clearTimeout(pending.timer);
    this.pending = null;
    this.setState({ status: "ready", stage: null, error: null });
    pending.resolve({
      results: message.results,
      stdout: message.stdout,
      error: message.error,
      timedOut: false,
      durationMs: Math.round(performance.now() - pending.startedAt),
    });
  }

  async run(input: { code: string; tests: string; packages?: readonly string[] }): Promise<RunOutcome> {
    try {
      await this.warmup();
    } catch (error) {
      return {
        results: [],
        stdout: "",
        error: `Python runtime failed to load: ${String(error)}`,
        timedOut: false,
        durationMs: 0,
      };
    }

    const id = this.nextRunId++;
    this.setState({ status: "running", stage: null, error: null });

    return new Promise<RunOutcome>((resolve) => {
      const timer = setTimeout(() => {
        if (this.pending?.id !== id) return;
        this.pending = null;
        // Nothing short of terminate() interrupts a spinning Python loop.
        this.terminate();
        this.setState({ status: "timeout", stage: null, error: null });
        resolve({
          results: [
            {
              name: "timeout",
              status: "error",
              message: `Took longer than ${RUN_TIMEOUT_MS / 1000}s — infinite loop?`,
              durationMs: RUN_TIMEOUT_MS,
            },
          ],
          stdout: "",
          error: null,
          timedOut: true,
          durationMs: RUN_TIMEOUT_MS,
        });
      }, RUN_TIMEOUT_MS);

      this.pending = { id, timer, resolve, startedAt: performance.now() };

      const message: RunMessage = {
        type: "run",
        runId: id,
        code: input.code,
        tests: input.tests,
        packages: input.packages ?? [],
      };
      this.worker?.postMessage(message);
    });
  }

  /** Kill the worker. The next run() boots a fresh one. */
  terminate() {
    this.worker?.terminate();
    this.worker = null;
    this.ready = null;
    if (this.pending) {
      clearTimeout(this.pending.timer);
      this.pending = null;
    }
  }
}

let singleton: PyRunner | null = null;

export function getPyRunner(): PyRunner {
  if (!singleton) singleton = new PyRunner();
  return singleton;
}

const NO_OP = () => () => {};
const serverSnapshot = () => IDLE;

export function usePyRunner() {
  const isBrowser = typeof window !== "undefined";
  const runner = isBrowser ? getPyRunner() : null;

  const state = useSyncExternalStore(
    runner?.subscribe ?? NO_OP,
    runner?.getSnapshot ?? serverSnapshot,
    serverSnapshot,
  );

  const warmup = useCallback(() => {
    runner?.warmup().catch(() => {
      /* surfaced through state.status === "error" */
    });
  }, [runner]);

  const run = useCallback(
    (input: { code: string; tests: string; packages?: readonly string[] }) =>
      runner
        ? runner.run(input)
        : Promise.resolve<RunOutcome>({
            results: [],
            stdout: "",
            error: "not running in a browser",
            timedOut: false,
            durationMs: 0,
          }),
    [runner],
  );

  return { ...state, warmup, run };
}

export function summarize(results: TestResult[]) {
  const passed = results.filter((result) => result.status === "passed").length;
  const failed = results.filter((result) => result.status === "failed").length;
  const errored = results.filter((result) => result.status === "error").length;
  return {
    passed,
    failed,
    errored,
    total: results.length,
    allPassed: results.length > 0 && passed === results.length,
  };
}
