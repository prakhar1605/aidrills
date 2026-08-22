import { describe, expect, it } from "vitest";

import { summarize, type TestResult } from "./client";

const result = (name: string, status: TestResult["status"]): TestResult => ({
  name,
  status,
  message: status === "passed" ? "" : "boom",
  durationMs: 1,
});

describe("summarize", () => {
  it("counts an all-green run", () => {
    const stats = summarize([result("a", "passed"), result("b", "passed")]);
    expect(stats).toEqual({ passed: 2, failed: 0, errored: 0, total: 2, allPassed: true });
  });

  it("separates failures from errors", () => {
    const stats = summarize([
      result("a", "passed"),
      result("b", "failed"),
      result("c", "error"),
    ]);
    expect(stats).toMatchObject({ passed: 1, failed: 1, errored: 1, total: 3 });
    expect(stats.allPassed).toBe(false);
  });

  it("does not call an empty run a pass", () => {
    // A collection error returns no rows; treating that as solved would let a
    // syntax error mark the problem complete.
    expect(summarize([]).allPassed).toBe(false);
  });
});
