import { z } from "zod";

/**
 * The single source of truth for what a problem is. `scripts/build-content.ts`
 * validates every `meta.json` against this, so a malformed problem fails the
 * build rather than the page.
 */

export const TRACK_IDS = ["foundations", "retrieval", "plumbing", "agents", "evals"] as const;
export const DIFFICULTIES = ["easy", "medium", "hard"] as const;
export const STATUSES = ["draft", "published"] as const;

export type TrackId = (typeof TRACK_IDS)[number];
export type Difficulty = (typeof DIFFICULTIES)[number];

const slug = z
  .string()
  .regex(/^[a-z0-9]+(-[a-z0-9]+)*$/, "must be lowercase kebab-case, e.g. rrf-fusion");

export const problemMetaSchema = z.object({
  id: z.number().int().positive(),
  slug,
  title: z.string().min(1),
  track: z.enum(TRACK_IDS),
  difficulty: z.enum(DIFFICULTIES),
  timeBudgetMin: z.number().int().positive().max(180),
  tags: z.array(z.string()).default([]),
  companies: z.array(z.string()).default([]),
  packages: z.array(z.string()).default([]),
  entryPoint: z.string().min(1),
  status: z.enum(STATUSES).default("draft"),
});

export type ProblemMeta = z.infer<typeof problemMetaSchema>;

/** A problem as it appears in `src/generated/problems.json`: meta plus the files. */
export const problemSchema = problemMetaSchema.extend({
  statement: z.string().min(1),
  starter: z.string().min(1),
  solution: z.string().min(1),
  tests: z.string().min(1),
  hints: z.array(z.string().min(1)).min(1),
});

export type Problem = z.infer<typeof problemSchema>;

export const trackSchema = z.object({
  id: z.enum(TRACK_IDS),
  name: z.string().min(1),
  blurb: z.string().min(1),
  accent: z.string().regex(/^#[0-9A-Fa-f]{6}$/, "must be a 6-digit hex colour"),
});

export type Track = z.infer<typeof trackSchema>;

export const roadmapSchema = z.object({
  title: z.string().min(1),
  intro: z.string().min(1),
  days: z
    .array(
      z.object({
        day: z.number().int().positive(),
        title: z.string().min(1),
        focus: z.string().min(1),
        slugs: z.array(slug),
      }),
    )
    .min(1),
});

export type Roadmap = z.infer<typeof roadmapSchema>;

export const contentSchema = z.object({
  problems: z.array(problemSchema),
  tracks: z.array(trackSchema),
  roadmap: roadmapSchema,
  resources: z.string().min(1),
});

export type Content = z.infer<typeof contentSchema>;
