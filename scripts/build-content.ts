/**
 * Compile content/ into src/generated/problems.json, and copy the Python
 * runtime into public/py/.
 *
 *   tsx scripts/build-content.ts            build
 *   tsx scripts/build-content.ts --check    validate only, emit nothing
 *
 * Any invalid problem is a hard failure with the path and the reason. Drafts
 * are validated but excluded from the output -- CI still runs their tests.
 */
import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

import {
  contentSchema,
  problemMetaSchema,
  roadmapSchema,
  trackSchema,
  type Problem,
} from "../src/lib/schema";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const CONTENT = join(ROOT, "content");
const PROBLEMS = join(CONTENT, "problems");
const OUT_DIR = join(ROOT, "src", "generated");
const OUT_FILE = join(OUT_DIR, "problems.json");
const PY_SRC = join(ROOT, "python");
const PY_OUT = join(ROOT, "public", "py");

const REQUIRED = ["meta.json", "statement.md", "starter.py", "tests.py", "solution.py", "hints.md"];
const RUNTIME_FILES = ["runner.py", "mock_llm.py"];

const errors: string[] = [];
const fail = (where: string, message: string) =>
  errors.push(`  ${relative(ROOT, where)}\n    ${message}`);

function read(path: string): string {
  return readFileSync(path, "utf8");
}

function readJson(path: string): unknown {
  try {
    return JSON.parse(read(path));
  } catch (error) {
    fail(path, `not valid JSON: ${(error as Error).message}`);
    return null;
  }
}

/** zod issues, flattened into one line each. */
function issues(error: { issues: readonly { path: PropertyKey[]; message: string }[] }): string {
  return error.issues
    .map((issue) => `${issue.path.join(".") || "(root)"}: ${issue.message}`)
    .join("\n    ");
}

function splitHints(source: string): string[] {
  return source
    .split(/^---$/m)
    .map((hint) => hint.trim())
    .filter(Boolean);
}

function loadProblem(slug: string): Problem | null {
  const dir = join(PROBLEMS, slug);

  const missing = REQUIRED.filter((file) => !existsSync(join(dir, file)));
  if (missing.length) {
    fail(dir, `missing ${missing.join(", ")}`);
    return null;
  }

  const raw = readJson(join(dir, "meta.json"));
  if (raw === null) return null;

  const parsed = problemMetaSchema.safeParse(raw);
  if (!parsed.success) {
    fail(join(dir, "meta.json"), issues(parsed.error));
    return null;
  }
  const meta = parsed.data;

  if (meta.slug !== slug) {
    fail(join(dir, "meta.json"), `slug "${meta.slug}" does not match the directory name "${slug}"`);
    return null;
  }

  const tests = read(join(dir, "tests.py"));
  if (!/^\s*from submission import \*/m.test(tests)) {
    fail(join(dir, "tests.py"), "must contain `from submission import *` (see docs/SPEC.md section 3)");
  }
  if (!/\bdef test_\w+\s*\(/.test(tests)) {
    fail(join(dir, "tests.py"), "contains no `def test_*` functions");
  }

  const hints = splitHints(read(join(dir, "hints.md")));
  if (hints.length !== 3) {
    fail(join(dir, "hints.md"), `expected 3 hints separated by --- lines, found ${hints.length}`);
  }

  return {
    ...meta,
    statement: read(join(dir, "statement.md")).trim(),
    starter: read(join(dir, "starter.py")),
    solution: read(join(dir, "solution.py")),
    tests,
    hints,
  };
}

function main() {
  const check = process.argv.includes("--check");

  if (!existsSync(PROBLEMS)) {
    console.error(`content: ${relative(ROOT, PROBLEMS)} does not exist`);
    process.exit(1);
  }

  const slugs = readdirSync(PROBLEMS, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && !entry.name.startsWith("_"))
    .map((entry) => entry.name)
    .sort();

  const all = slugs.map(loadProblem).filter((problem): problem is Problem => problem !== null);

  // Ids and slugs both have to be unique: ids order the list, slugs are the URLs.
  const seenIds = new Map<number, string>();
  for (const problem of all) {
    const clash = seenIds.get(problem.id);
    if (clash) {
      fail(
        join(PROBLEMS, problem.slug, "meta.json"),
        `id ${problem.id} is already used by "${clash}"`,
      );
    }
    seenIds.set(problem.id, problem.slug);
  }

  const tracksRaw = readJson(join(CONTENT, "tracks.json"));
  const tracks = trackSchema.array().min(1).safeParse(tracksRaw);
  if (!tracks.success) fail(join(CONTENT, "tracks.json"), issues(tracks.error));

  const roadmapRaw = readJson(join(CONTENT, "roadmap.json"));
  const roadmap = roadmapSchema.safeParse(roadmapRaw);
  if (!roadmap.success) fail(join(CONTENT, "roadmap.json"), issues(roadmap.error));

  const published = all.filter((problem) => problem.status === "published");
  const publishedSlugs = new Set(published.map((problem) => problem.slug));

  if (roadmap.success) {
    for (const day of roadmap.data.days) {
      for (const slug of day.slugs) {
        if (!publishedSlugs.has(slug)) {
          fail(
            join(CONTENT, "roadmap.json"),
            `day ${day.day} references "${slug}", which is not a published problem`,
          );
        }
      }
    }
  }

  const trackIds = new Set((tracks.success ? tracks.data : []).map((track) => track.id));
  for (const problem of published) {
    if (!trackIds.has(problem.track)) {
      fail(
        join(PROBLEMS, problem.slug, "meta.json"),
        `track "${problem.track}" is not defined in content/tracks.json`,
      );
    }
  }

  for (const file of RUNTIME_FILES) {
    if (!existsSync(join(PY_SRC, file))) fail(join(PY_SRC, file), "missing Python runtime file");
  }

  if (errors.length) {
    console.error(`\ncontent: ${errors.length} problem${errors.length === 1 ? "" : "s"}\n`);
    console.error(errors.join("\n\n"));
    console.error("");
    process.exit(1);
  }

  const content = contentSchema.parse({
    problems: [...published].sort((a, b) => a.id - b.id),
    tracks: tracks.success ? tracks.data : [],
    roadmap: roadmap.success ? roadmap.data : undefined,
    resources: read(join(CONTENT, "resources.md")).trim(),
  });

  const drafts = all.length - published.length;
  const summary = `${published.length} published${drafts ? `, ${drafts} draft` : ""}`;

  if (check) {
    console.log(`content: ok — ${summary}`);
    return;
  }

  mkdirSync(OUT_DIR, { recursive: true });
  writeFileSync(OUT_FILE, JSON.stringify(content, null, 2));

  rmSync(PY_OUT, { recursive: true, force: true });
  mkdirSync(PY_OUT, { recursive: true });
  for (const file of RUNTIME_FILES) {
    writeFileSync(join(PY_OUT, file), read(join(PY_SRC, file)));
  }

  console.log(`content: ${summary} -> ${relative(ROOT, OUT_FILE)}`);
  console.log(`content: ${RUNTIME_FILES.join(", ")} -> ${relative(ROOT, PY_OUT)}`);
}

main();
