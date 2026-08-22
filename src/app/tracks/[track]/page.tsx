import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { StatusDot } from "@/components/problems/StatusDot";
import { TrackProgress } from "@/components/problems/TrackProgress";
import { DifficultyBadge } from "@/components/ui/Badge";
import { getTrack, problemsInTrack, tracks } from "@/lib/content";
import type { TrackId } from "@/lib/schema";
import { site } from "@/lib/site";

export function generateStaticParams() {
  return tracks.map((track) => ({ track: track.id }));
}

export async function generateMetadata({
  params,
}: PageProps<"/tracks/[track]">): Promise<Metadata> {
  const { track: id } = await params;
  const track = getTrack(id);
  if (!track) return {};
  return {
    title: `${track.name} drills`,
    description: track.blurb,
    alternates: { canonical: `${site.url}/tracks/${track.id}` },
  };
}

export default async function TrackPage({ params }: PageProps<"/tracks/[track]">) {
  const { track: id } = await params;
  const track = getTrack(id);
  if (!track) notFound();

  const list = problemsInTrack(track.id as TrackId);

  return (
    <div className="mx-auto w-full max-w-3xl px-5 py-12">
      <div className="flex items-center gap-2">
        <span
          className="inline-block h-2.5 w-2.5 rounded-full"
          style={{ background: track.accent }}
          aria-hidden
        />
        <h1 className="text-2xl">{track.name}</h1>
      </div>
      <p className="mt-2 max-w-prose text-sm text-muted">{track.blurb}</p>

      <TrackProgress slugs={list.map((problem) => problem.slug)} accent={track.accent} />

      <ol className="mt-8 divide-y divide-line border-y border-line">
        {list.map((problem, index) => (
          <li key={problem.slug}>
            <Link
              href={`/problems/${problem.slug}`}
              className="group flex items-center gap-3 py-3 transition-colors hover:bg-raised/50"
            >
              <span className="w-5 shrink-0 pl-1 font-mono text-[11px] text-muted">
                {index + 1}
              </span>
              <StatusDot slug={problem.slug} />
              <span className="min-w-0 flex-1">
                <span className="block truncate text-sm group-hover:text-white">
                  {problem.title}
                </span>
                {problem.companies.length > 0 && (
                  <span className="mt-0.5 block font-mono text-[11px] text-muted">
                    {problem.companies.join(" · ")}
                  </span>
                )}
              </span>
              <DifficultyBadge difficulty={problem.difficulty} />
              <span className="w-14 shrink-0 pr-1 text-right font-mono text-[11px] text-muted">
                {problem.timeBudgetMin} min
              </span>
            </Link>
          </li>
        ))}
      </ol>

      {list.length === 0 && (
        <p className="mt-10 text-sm text-muted">
          No drills in this track yet.{" "}
          <Link href="/contribute" className="text-accent underline underline-offset-2">
            Write the first one
          </Link>
          .
        </p>
      )}

      <nav className="mt-10 flex flex-wrap gap-2 border-t border-line pt-6">
        {tracks
          .filter((other) => other.id !== track.id)
          .map((other) => (
            <Link
              key={other.id}
              href={`/tracks/${other.id}`}
              className="rounded-full border border-line px-3 py-1 font-mono text-[11px] text-muted transition-colors hover:text-ink"
            >
              {other.name}
            </Link>
          ))}
      </nav>
    </div>
  );
}
