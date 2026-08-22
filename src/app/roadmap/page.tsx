import type { Metadata } from "next";
import Link from "next/link";

import { StatusDot } from "@/components/problems/StatusDot";
import { getProblem, roadmap } from "@/lib/content";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: roadmap.title,
  description:
    "A 14-day plan through the AI engineering interview drills: decoding, attention, tokenizers, retrieval, plumbing, agents, evals.",
  alternates: { canonical: `${site.url}/roadmap` },
};

export default function RoadmapPage() {
  return (
    <div className="mx-auto w-full max-w-3xl px-5 py-12">
      <h1 className="text-2xl">{roadmap.title}</h1>
      <p className="mt-3 max-w-prose text-sm leading-relaxed text-muted">{roadmap.intro}</p>

      <ol className="mt-10 flex flex-col">
        {roadmap.days.map((day) => (
          <li key={day.day} className="flex gap-5 border-t border-line py-5 last:border-b">
            <span className="w-10 shrink-0 pt-0.5 font-mono text-xs text-muted">
              Day {day.day}
            </span>
            <div className="min-w-0 flex-1">
              <h2 className="text-sm font-medium">{day.title}</h2>
              <p className="mt-1 text-xs leading-relaxed text-muted">{day.focus}</p>
              <ul className="mt-3 flex flex-col gap-1.5">
                {day.slugs.map((slug) => {
                  const problem = getProblem(slug);
                  if (!problem) return null;
                  return (
                    <li key={slug}>
                      <Link
                        href={`/problems/${slug}`}
                        className="group inline-flex items-center gap-2 text-sm transition-colors hover:text-white"
                      >
                        <StatusDot slug={slug} />
                        <span>{problem.title}</span>
                        <span className="font-mono text-[11px] text-muted">
                          {problem.timeBudgetMin} min
                        </span>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
