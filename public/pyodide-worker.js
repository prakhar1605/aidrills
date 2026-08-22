/**
 * The Pyodide worker. Deliberately a plain classic worker served from public/
 * rather than a bundled module: `importScripts` is the supported way to load
 * Pyodide from a CDN, and this file then has zero bundler surface area.
 *
 * It has no hardcoded Pyodide version -- the client sends the index URL, which
 * lives in src/lib/pyodide/const.ts. The message contract is documented in
 * src/lib/pyodide/client.ts and both sides must agree.
 *
 *   in   { type: "init", indexURL, runtimeFiles }
 *        { type: "run", runId, code, tests, packages }
 *   out  { type: "progress", stage }
 *        { type: "ready" }
 *        { type: "fatal", error }
 *        { type: "result", runId, results, stdout, error }
 */

let pyodide = null;
const loadedPackages = new Set();

function progress(stage) {
  self.postMessage({ type: "progress", stage });
}

async function init(indexURL, runtimeFiles) {
  progress("downloading");
  self.importScripts(indexURL + "pyodide.js");

  progress("initializing");
  pyodide = await self.loadPyodide({ indexURL });

  // MEMFS mtimes have one-second resolution, so a cached .pyc can shadow a
  // freshly written submission.py. Never write bytecode.
  pyodide.runPython("import sys, os\nsys.dont_write_bytecode = True\nif os.getcwd() not in sys.path:\n    sys.path.insert(0, os.getcwd())");

  const sources = await Promise.all(
    runtimeFiles.map(async (name) => {
      const response = await fetch(`/py/${name}`, { cache: "force-cache" });
      if (!response.ok) throw new Error(`could not load /py/${name} (${response.status})`);
      return [name, await response.text()];
    }),
  );
  for (const [name, source] of sources) {
    pyodide.FS.writeFile(name, source, { encoding: "utf8" });
  }

  // Import once; runner.run() re-imports submission and tests on every call.
  pyodide.runPython("import runner");

  self.postMessage({ type: "ready" });
}

async function run({ runId, code, tests, packages }) {
  const missing = (packages || []).filter((name) => !loadedPackages.has(name));
  if (missing.length) {
    progress("packages");
    await pyodide.loadPackage(missing);
    missing.forEach((name) => loadedPackages.add(name));
  }

  pyodide.FS.writeFile("submission.py", code, { encoding: "utf8" });
  pyodide.FS.writeFile("tests.py", tests, { encoding: "utf8" });

  const payload = pyodide.runPython("import runner\nrunner.run()");
  const parsed = JSON.parse(payload);
  self.postMessage({
    type: "result",
    runId,
    results: parsed.results,
    stdout: parsed.stdout,
    error: null,
  });
}

self.onmessage = async (event) => {
  const message = event.data;
  try {
    if (message.type === "init") {
      await init(message.indexURL, message.runtimeFiles);
      return;
    }
    if (message.type === "run") {
      if (!pyodide) throw new Error("the Python runtime is not ready yet");
      await run(message);
    }
  } catch (error) {
    const text = error && error.message ? error.message : String(error);
    if (message.type === "run") {
      self.postMessage({
        type: "result",
        runId: message.runId,
        results: [],
        stdout: "",
        error: text,
      });
    } else {
      self.postMessage({ type: "fatal", error: text });
    }
  }
};
