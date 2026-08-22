import Link from "next/link";

import { TrackCard } from "@/components/problems/TrackCard";
import { LandingDrill } from "@/components/workspace/LandingDrill";
import { countByTrack, getProblem, problems, tracks } from "@/lib/content";

const HERO_SLUG = "rrf-fusion";

export default function LandingPage() {
  const hero = getProblem(HERO_SLUG) ?? problems[0];
  const counts = countByTrack();

  return (
    <div className="mx-auto w-full max-w-5xl px-5 py-12 lg:py-16">
      <h1 className="max-w-2xl text-3xl leading-tight tracking-tight sm:text-4xl">
        You have used an embedding model for two years.{" "}
        <em className="font-display italic">Now write BM25 on the whiteboard.</em>
      </h1>
      <p className="mt-4 max-w-xl text-sm leading-relaxed text-muted">
        AI engineering interviews ask you to implement the pieces you normally import.
        These are those pieces, with real tests. The drill below is live — the editor is
        the editor, the runtime is CPython compiled to WebAssembly, and it is already
        running in this tab. No signup, no API key, nothing leaves your browser.
      </p>

      {hero && (
        <div className="mt-8">
          <LandingDrill
            slug={hero.slug}
            title={hero.title}
            timeBudgetMin={hero.timeBudgetMin}
            entryPoint={hero.entryPoint}
            starter={hero.starter}
            tests={hero.tests}
            packages={hero.packages}
          />
        </div>
      )}

      <div className="mt-14">
        <div className="flex items-baseline justify-between">
          <h2 className="text-xs font-medium tracking-[0.08em] text-muted uppercase">
            Tracks
          </h2>
          <Link
            href="/problems"
            className="font-mono text-xs text-muted transition-colors hover:text-ink"
          >
            all {problems.length} drills →
          </Link>
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {tracks.map((track) => (
            <TrackCard key={track.id} track={track} count={counts[track.id] ?? 0} />
          ))}
        </div>
      </div>

      <div className="mt-14 grid gap-6 border-t border-line pt-8 text-sm sm:grid-cols-3">
        <Feature title="The tests are the product">
          Every drill ships a reference solution that must pass and a starter that must
          fail. CI enforces both, so a drill can never quietly become vacuous.
        </Feature>
        <Feature title="Nothing runs on a server">
          Your Python executes in a Web Worker in this tab. There is no sandbox to
          escape, no queue to wait in, and no rate limit.
        </Feature>
        <Feature title="Git is the CMS">
          Problems are six files in a folder.{" "}
          <Link href="/contribute" className="text-accent underline underline-offset-2">
            Open a PR
          </Link>{" "}
          with the question you were actually asked.
        </Feature>
      </div>

      <p className="mt-12 font-mono text-xs text-muted">
        New here?{" "}
        <Link href="/roadmap" className="text-accent underline underline-offset-2">
          The 14-day plan
        </Link>{" "}
        orders these for you.
      </p>
    </div>
  );
}

function Feature({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h3 className="text-sm font-medium">{title}</h3>
      <p className="mt-1.5 text-xs leading-relaxed text-muted">{children}</p>
    </div>
  );
}
