"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { StatusDot } from "@/components/problems/StatusDot";
import { DifficultyBadge, TrackBadge } from "@/components/ui/Badge";
import type { Problem, Track } from "@/lib/schema";
import { useHydrated, useStore } from "@/lib/store";
import { cn } from "@/lib/utils";

export type ProblemRow = Pick<
  Problem,
  "id" | "slug" | "title" | "track" | "difficulty" | "timeBudgetMin" | "tags" | "companies"
>;

type Props = { problems: ProblemRow[]; tracks: Track[] };

const ANY = "";

export function ProblemTable({ problems, tracks }: Props) {
  const [query, setQuery] = useState("");
  const [track, setTrack] = useState(ANY);
  const [difficulty, setDifficulty] = useState(ANY);
  const [tag, setTag] = useState(ANY);
  const [company, setCompany] = useState(ANY);
  const [status, setStatus] = useState(ANY);

  const progress = useStore((state) => state.progress);
  const hydrated = useHydrated();

  const tags = useMemo(
    () => [...new Set(problems.flatMap((problem) => problem.tags))].sort(),
    [problems],
  );
  const companies = useMemo(
    () => [...new Set(problems.flatMap((problem) => problem.companies))].sort(),
    [problems],
  );

  const visible = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return problems.filter((problem) => {
      if (track && problem.track !== track) return false;
      if (difficulty && problem.difficulty !== difficulty) return false;
      if (tag && !problem.tags.includes(tag)) return false;
      if (company && !problem.companies.includes(company)) return false;
      if (status) {
        const current = progress[problem.slug]?.status ?? "unsolved";
        if (current !== status) return false;
      }
      if (!needle) return true;
      return [problem.title, problem.slug, ...problem.tags, ...problem.companies]
        .join(" ")
        .toLowerCase()
        .includes(needle);
    });
  }, [problems, query, track, difficulty, tag, company, status, progress]);

  const filtered = Boolean(query || track || difficulty || tag || company || status);

  return (
    <div>
      <div className="flex flex-wrap items-center gap-2">
        <input
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search drills…"
          aria-label="Search drills"
          className="h-8 min-w-[12rem] flex-1 rounded-md border border-line bg-raised px-2.5 text-sm placeholder:text-muted"
        />
        <Select value={track} onChange={setTrack} label="Track">
          {tracks.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name}
            </option>
          ))}
        </Select>
        <Select value={difficulty} onChange={setDifficulty} label="Difficulty">
          {["easy", "medium", "hard"].map((value) => (
            <option key={value} value={value}>
              {value}
            </option>
          ))}
        </Select>
        <Select value={tag} onChange={setTag} label="Tag">
          {tags.map((value) => (
            <option key={value} value={value}>
              {value}
            </option>
          ))}
        </Select>
        <Select value={company} onChange={setCompany} label="Company">
          {companies.map((value) => (
            <option key={value} value={value}>
              {value}
            </option>
          ))}
        </Select>
        <Select value={status} onChange={setStatus} label="Status">
          {["unsolved", "attempted", "solved"].map((value) => (
            <option key={value} value={value}>
              {value}
            </option>
          ))}
        </Select>
        {filtered && (
          <button
            onClick={() => {
              setQuery("");
              setTrack(ANY);
              setDifficulty(ANY);
              setTag(ANY);
              setCompany(ANY);
              setStatus(ANY);
            }}
            className="h-8 rounded-md px-2 text-xs text-muted transition-colors hover:text-ink"
          >
            Clear
          </button>
        )}
      </div>

      <p className="mt-3 font-mono text-[11px] text-muted">
        {visible.length} of {problems.length} drills
        {hydrated && status ? "" : null}
      </p>

      {visible.length === 0 ? (
        <p className="mt-10 text-center text-sm text-muted">
          Nothing matches those filters.{" "}
          <Link href="/contribute" className="text-accent underline underline-offset-2">
            Add the drill you were looking for
          </Link>
          .
        </p>
      ) : (
        <ul className="mt-3 divide-y divide-line border-y border-line">
          {visible.map((problem) => (
            <li key={problem.slug}>
              <Link
                href={`/problems/${problem.slug}`}
                className="group flex items-center gap-3 py-2.5 transition-colors hover:bg-raised/50"
              >
                <span className="w-6 shrink-0 pl-1 font-mono text-[11px] text-muted">
                  {String(problem.id).padStart(2, "0")}
                </span>
                <StatusDot slug={problem.slug} />
                <span className="min-w-0 flex-1 truncate text-sm group-hover:text-white">
                  {problem.title}
                </span>
                <span className="hidden shrink-0 sm:block">
                  <TrackBadge track={problem.track} />
                </span>
                <span className="hidden shrink-0 sm:block">
                  <DifficultyBadge difficulty={problem.difficulty} />
                </span>
                <span className="w-14 shrink-0 pr-1 text-right font-mono text-[11px] text-muted">
                  {problem.timeBudgetMin} min
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function Select({
  value,
  onChange,
  label,
  children,
}: {
  value: string;
  onChange: (value: string) => void;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <select
      aria-label={label}
      value={value}
      onChange={(event) => onChange(event.target.value)}
      className={cn(
        "h-8 rounded-md border border-line bg-raised px-2 text-xs capitalize",
        value ? "text-ink" : "text-muted",
      )}
    >
      <option value="">{label}</option>
      {children}
    </select>
  );
}
