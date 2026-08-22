"use client";

import { useHydrated, useStore } from "@/lib/store";

export function TrackProgress({ slugs, accent }: { slugs: string[]; accent: string }) {
  const progress = useStore((state) => state.progress);
  const hydrated = useHydrated();

  const solved = hydrated
    ? slugs.filter((slug) => progress[slug]?.status === "solved").length
    : 0;
  const pct = slugs.length ? (solved / slugs.length) * 100 : 0;

  return (
    <div className="mt-6">
      <div className="flex items-baseline justify-between font-mono text-[11px] text-muted">
        <span>
          {hydrated ? `${solved} of ${slugs.length} solved` : `${slugs.length} drills`}
        </span>
        <span>{hydrated ? `${Math.round(pct)}%` : ""}</span>
      </div>
      <div className="mt-1.5 h-1 overflow-hidden rounded-full bg-line">
        <div
          className="h-full rounded-full transition-[width] duration-300"
          style={{ width: `${pct}%`, background: accent }}
        />
      </div>
    </div>
  );
}
