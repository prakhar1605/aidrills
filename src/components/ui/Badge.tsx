import { getTrack } from "@/lib/content";
import type { Difficulty } from "@/lib/schema";
import { cn } from "@/lib/utils";

const base =
  "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 font-mono text-[11px] leading-5 whitespace-nowrap";

const DIFFICULTY_CLASS: Record<Difficulty, string> = {
  easy: "border-line text-muted",
  medium: "border-line text-ink/80",
  hard: "border-line-strong text-ink",
};

export function DifficultyBadge({ difficulty }: { difficulty: Difficulty }) {
  return (
    <span className={cn(base, "bg-raised", DIFFICULTY_CLASS[difficulty])}>{difficulty}</span>
  );
}

/** The one place a track accent is allowed outside the track page and the OG card. */
export function TrackBadge({ track, className }: { track: string; className?: string }) {
  const meta = getTrack(track);
  const accent = meta?.accent ?? "#8C8A84";
  return (
    <span
      className={cn(base, className)}
      style={{
        color: accent,
        borderColor: `color-mix(in srgb, ${accent} 30%, transparent)`,
        background: `color-mix(in srgb, ${accent} 8%, transparent)`,
      }}
    >
      {meta?.name ?? track}
    </span>
  );
}

export function Tag({ children }: { children: React.ReactNode }) {
  return (
    <span className="rounded border border-line bg-raised px-1.5 py-0.5 font-mono text-[11px] text-muted">
      {children}
    </span>
  );
}
