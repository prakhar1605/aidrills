import Link from "next/link";

import type { Track } from "@/lib/schema";

export function TrackCard({ track, count }: { track: Track; count: number }) {
  return (
    <Link
      href={`/tracks/${track.id}`}
      className="group flex flex-col rounded-lg border border-line bg-raised p-4 transition-colors hover:border-line-strong"
    >
      <span className="flex items-center gap-2">
        <span
          className="inline-block h-2 w-2 rounded-full"
          style={{ background: track.accent }}
          aria-hidden
        />
        <span className="text-sm font-medium group-hover:text-white">{track.name}</span>
        <span className="ml-auto font-mono text-[11px] text-muted">{count}</span>
      </span>
      <span className="mt-2 text-xs leading-relaxed text-muted">{track.blurb}</span>
    </Link>
  );
}
