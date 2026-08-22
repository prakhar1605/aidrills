import generated from "@/generated/problems.json";

import type { Content, Difficulty, Problem, Roadmap, Track, TrackId } from "./schema";

/**
 * Typed access to the build output. Nothing else in the app reads
 * src/generated/problems.json directly.
 */
const content = generated as unknown as Content;

export const problems: Problem[] = content.problems;
export const tracks: Track[] = content.tracks;
export const roadmap: Roadmap = content.roadmap;
export const resources: string = content.resources;

export const DIFFICULTY_ORDER: Record<Difficulty, number> = { easy: 0, medium: 1, hard: 2 };

export function getProblem(slug: string): Problem | undefined {
  return problems.find((problem) => problem.slug === slug);
}

export function getTrack(id: string): Track | undefined {
  return tracks.find((track) => track.id === id);
}

export function problemsInTrack(id: TrackId): Problem[] {
  return problems.filter((problem) => problem.track === id);
}

export function countByTrack(): Record<string, number> {
  return problems.reduce<Record<string, number>>((counts, problem) => {
    counts[problem.track] = (counts[problem.track] ?? 0) + 1;
    return counts;
  }, {});
}

export function allTags(): string[] {
  return [...new Set(problems.flatMap((problem) => problem.tags))].sort();
}

export function allCompanies(): string[] {
  return [...new Set(problems.flatMap((problem) => problem.companies))].sort();
}

/** The first paragraph of a statement, flattened -- used for meta descriptions. */
export function summary(problem: Problem, maxLength = 160): string {
  const paragraph = problem.statement.split(/\n\s*\n/)[0] ?? "";
  const flat = paragraph.replace(/[`*_]/g, "").replace(/\s+/g, " ").trim();
  if (flat.length <= maxLength) return flat;
  return `${flat.slice(0, flat.lastIndexOf(" ", maxLength - 1))}…`;
}

/** The next problem in the same track, for the workspace footer. */
export function nextInTrack(problem: Problem): Problem | undefined {
  const siblings = problemsInTrack(problem.track);
  const index = siblings.findIndex((candidate) => candidate.slug === problem.slug);
  return index >= 0 ? siblings[index + 1] : undefined;
}
