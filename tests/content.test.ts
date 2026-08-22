import { readdirSync, readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { problems, roadmap, tracks } from "@/lib/content";
import { problemSchema } from "@/lib/schema";

/**
 * The rules build-content.ts enforces, asserted against the real content so a
 * regression shows up as a failing test and not only as a red build.
 */

const PROBLEMS_DIR = join(process.cwd(), "content", "problems");
const REQUIRED = ["meta.json", "statement.md", "starter.py", "tests.py", "solution.py", "hints.md"];

const onDisk = readdirSync(PROBLEMS_DIR, { withFileTypes: true })
  .filter((entry) => entry.isDirectory() && !entry.name.startsWith("_"))
  .map((entry) => entry.name);

describe("generated content", () => {
  it("has problems", () => {
    expect(problems.length).toBeGreaterThan(0);
  });

  it("matches the problem schema", () => {
    for (const problem of problems) {
      const result = problemSchema.safeParse(problem);
      expect(result.success, `${problem.slug}: ${JSON.stringify(result.error?.issues)}`).toBe(
        true,
      );
    }
  });

  it("only contains published problems", () => {
    expect(problems.every((problem) => problem.status === "published")).toBe(true);
  });

  it("has unique ids and slugs", () => {
    expect(new Set(problems.map((p) => p.id)).size).toBe(problems.length);
    expect(new Set(problems.map((p) => p.slug)).size).toBe(problems.length);
  });

  it("is ordered by id", () => {
    const ids = problems.map((problem) => problem.id);
    expect(ids).toEqual([...ids].sort((a, b) => a - b));
  });

  it("gives every problem exactly three hints", () => {
    for (const problem of problems) {
      expect(problem.hints, problem.slug).toHaveLength(3);
    }
  });

  it("puts every problem in a declared track", () => {
    const ids = new Set(tracks.map((track) => track.id));
    for (const problem of problems) {
      expect(ids.has(problem.track), `${problem.slug} -> ${problem.track}`).toBe(true);
    }
  });
});

describe("test contract", () => {
  it("imports the submission in every tests.py", () => {
    for (const problem of problems) {
      expect(problem.tests, problem.slug).toMatch(/^\s*from submission import \*/m);
    }
  });

  it("declares at least three cases per problem", () => {
    for (const problem of problems) {
      const cases = problem.tests.match(/\bdef test_\w+\s*\(/g) ?? [];
      expect(cases.length, problem.slug).toBeGreaterThanOrEqual(3);
    }
  });

  it("gives every assertion a message", () => {
    for (const problem of problems) {
      const bare = problem.tests
        .split("\n")
        .filter((line) => /^\s*assert /.test(line) && !line.includes(","));
      expect(bare, `${problem.slug}: bare asserts`).toEqual([]);
    }
  });

  it("only imports the standard library, numpy or mock_llm", () => {
    const allowed = /^(?:from|import)\s+(submission|mock_llm|numpy|math|json|re|string|collections|itertools|typing|random|time|dataclasses|functools|heapq)\b/;
    for (const problem of problems) {
      const imports = problem.tests
        .split("\n")
        .filter((line) => /^(?:from|import)\s/.test(line));
      for (const line of imports) {
        expect(allowed.test(line), `${problem.slug}: ${line}`).toBe(true);
      }
    }
  });

  it("only lists numpy as a Pyodide package", () => {
    for (const problem of problems) {
      for (const name of problem.packages) {
        expect(["numpy"], problem.slug).toContain(name);
      }
    }
  });

  it("names an entry point the starter actually defines", () => {
    for (const problem of problems) {
      // The entry point is a function for most drills and a class for the
      // stateful ones (TokenBucket, InvertedIndex, ...).
      const defined = new RegExp(`^(?:def|class)\\s+${problem.entryPoint}\\b`, "m");
      expect(defined.test(problem.starter), `${problem.slug}: ${problem.entryPoint}`).toBe(
        true,
      );
    }
  });
});

describe("problem folders", () => {
  it("all six files exist for every folder on disk", () => {
    for (const slug of onDisk) {
      for (const file of REQUIRED) {
        expect(existsSync(join(PROBLEMS_DIR, slug, file)), `${slug}/${file}`).toBe(true);
      }
    }
  });

  it("every folder name matches the slug in its meta.json", () => {
    for (const slug of onDisk) {
      const meta = JSON.parse(readFileSync(join(PROBLEMS_DIR, slug, "meta.json"), "utf8"));
      expect(meta.slug, slug).toBe(slug);
    }
  });
});

describe("roadmap", () => {
  it("only references published problems", () => {
    const published = new Set(problems.map((problem) => problem.slug));
    for (const day of roadmap.days) {
      for (const slug of day.slugs) {
        expect(published.has(slug), `day ${day.day} -> ${slug}`).toBe(true);
      }
    }
  });

  it("numbers the days consecutively from one", () => {
    expect(roadmap.days.map((day) => day.day)).toEqual(
      roadmap.days.map((_, index) => index + 1),
    );
  });
});
