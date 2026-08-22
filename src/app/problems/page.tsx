import type { Metadata } from "next";

import { ProblemTable, type ProblemRow } from "@/components/problems/ProblemTable";
import { problems, tracks } from "@/lib/content";

export const metadata: Metadata = {
  title: "All drills",
  description:
    "Every AI engineering interview drill: attention, tokenizers, BM25, reciprocal rank fusion, retries, SSE parsing, agent loops, evals. Runs in your browser.",
  alternates: { canonical: "/problems" },
};

export default function ProblemsPage() {
  const rows: ProblemRow[] = problems.map(
    ({ id, slug, title, track, difficulty, timeBudgetMin, tags, companies }) => ({
      id,
      slug,
      title,
      track,
      difficulty,
      timeBudgetMin,
      tags,
      companies,
    }),
  );

  return (
    <div className="mx-auto w-full max-w-4xl px-5 py-12">
      <h1 className="text-2xl">Drills</h1>
      <p className="mt-2 max-w-prose text-sm text-muted">
        {problems.length} problems across five tracks. Every one has real tests, a
        reference solution, and a time budget taken from how long the question actually
        gets in a screen.
      </p>

      <div className="mt-8">
        <ProblemTable problems={rows} tracks={tracks} />
      </div>
    </div>
  );
}
