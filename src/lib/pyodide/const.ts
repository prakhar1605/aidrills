/**
 * The only place the Pyodide version and CDN URL appear.
 *
 * The worker is a static classic script in public/, so it cannot import this
 * module -- the client passes `PYODIDE_INDEX_URL` in the init message instead.
 * That keeps the version pinned in exactly one file.
 */

export const PYODIDE_VERSION = "0.28.3";

export const PYODIDE_INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

/** Written into the Pyodide filesystem at init; copied to public/py by the build. */
export const PY_RUNTIME_FILES = ["runner.py", "mock_llm.py"] as const;

export const WORKER_URL = "/pyodide-worker.js";

/** A run that outlives this is treated as an infinite loop and the worker is killed. */
export const RUN_TIMEOUT_MS = 15_000;
