import { describe, expect, it } from "vitest";

import { problemMetaSchema, roadmapSchema, trackSchema } from "./schema";

const VALID = {
  id: 7,
  slug: "rrf-fusion",
  title: "Reciprocal Rank Fusion",
  track: "retrieval",
  difficulty: "medium",
  timeBudgetMin: 25,
  tags: ["ranking"],
  companies: ["Cohere"],
  packages: [],
  entryPoint: "rrf_fuse",
  status: "published",
};

describe("problemMetaSchema", () => {
  it("accepts a well-formed meta.json", () => {
    expect(problemMetaSchema.parse(VALID)).toMatchObject({ slug: "rrf-fusion", id: 7 });
  });

  it("defaults the optional list fields and status", () => {
    const parsed = problemMetaSchema.parse({
      id: 1,
      slug: "a-drill",
      title: "A Drill",
      track: "agents",
      difficulty: "easy",
      timeBudgetMin: 10,
      entryPoint: "solve",
    });
    expect(parsed).toMatchObject({ tags: [], companies: [], packages: [], status: "draft" });
  });

  it.each([
    ["a non-kebab slug", { slug: "RRF Fusion" }],
    ["an unknown track", { track: "prompting" }],
    ["an unknown difficulty", { difficulty: "expert" }],
    ["a zero id", { id: 0 }],
    ["a fractional id", { id: 1.5 }],
    ["a zero time budget", { timeBudgetMin: 0 }],
    ["an absurd time budget", { timeBudgetMin: 999 }],
    ["an empty title", { title: "" }],
    ["an empty entry point", { entryPoint: "" }],
    ["an unknown status", { status: "archived" }],
  ])("rejects %s", (_label, patch) => {
    const result = problemMetaSchema.safeParse({ ...VALID, ...patch });
    expect(result.success).toBe(false);
  });

  it("names the offending field in the error", () => {
    const result = problemMetaSchema.safeParse({ ...VALID, slug: "Not A Slug" });
    expect(result.success).toBe(false);
    if (result.success) return;
    expect(result.error.issues[0].path).toEqual(["slug"]);
    expect(result.error.issues[0].message).toContain("kebab-case");
  });
});

describe("trackSchema", () => {
  const track = { id: "evals", name: "Evals", blurb: "Scoring.", accent: "#E0687A" };

  it("accepts a six-digit hex accent", () => {
    expect(trackSchema.parse(track).accent).toBe("#E0687A");
  });

  it.each(["red", "#fff", "E0687A", "#E0687AA"])("rejects the accent %s", (accent) => {
    expect(trackSchema.safeParse({ ...track, accent }).success).toBe(false);
  });
});

describe("roadmapSchema", () => {
  it("rejects a day list with a malformed slug", () => {
    const result = roadmapSchema.safeParse({
      title: "Plan",
      intro: "Do the drills.",
      days: [{ day: 1, title: "Decoding", focus: "Sampling.", slugs: ["Top K"] }],
    });
    expect(result.success).toBe(false);
  });

  it("rejects an empty plan", () => {
    const result = roadmapSchema.safeParse({ title: "Plan", intro: "x", days: [] });
    expect(result.success).toBe(false);
  });
});
