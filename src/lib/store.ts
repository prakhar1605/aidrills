"use client";

import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

/**
 * The only module in the app that touches localStorage.
 *
 * Phase 3 adds a sync layer on top of this; the UI must never block on it, so
 * every action here stays synchronous.
 */

export const STORAGE_KEY = "aidrills:v1";

export type ProblemStatus = "unsolved" | "attempted" | "solved";

export type ProgressEntry = {
  status: ProblemStatus;
  attempts: number;
  bestMs?: number;
  hintsUsed: number;
  solvedAt?: string;
};

export type Settings = {
  /** Editor font size in px. */
  fontSize: number;
};

type StoreState = {
  progress: Record<string, ProgressEntry>;
  drafts: Record<string, string>;
  settings: Settings;
  hydrated: boolean;

  recordRun: (slug: string, passed: boolean, durationMs: number) => void;
  revealHint: (slug: string, index: number) => void;
  markSolved: (slug: string, durationMs?: number) => void;
  setDraft: (slug: string, code: string) => void;
  clearDraft: (slug: string) => void;
  resetProblem: (slug: string) => void;
  setSettings: (patch: Partial<Settings>) => void;
  resetAll: () => void;
  /** Flipped once localStorage has been read. Never persisted. */
  setHydrated: () => void;
};

const EMPTY: ProgressEntry = { status: "unsolved", attempts: 0, hintsUsed: 0 };

export const DEFAULT_SETTINGS: Settings = { fontSize: 14 };

export const useStore = create<StoreState>()(
  persist(
    (set) => ({
      progress: {},
      drafts: {},
      settings: DEFAULT_SETTINGS,
      hydrated: false,

      recordRun: (slug, passed, durationMs) =>
        set((state) => {
          const entry = state.progress[slug] ?? EMPTY;
          const solved = passed || entry.status === "solved";
          const best =
            passed && durationMs > 0
              ? Math.min(entry.bestMs ?? Number.POSITIVE_INFINITY, durationMs)
              : entry.bestMs;
          return {
            progress: {
              ...state.progress,
              [slug]: {
                ...entry,
                attempts: entry.attempts + 1,
                status: solved ? "solved" : "attempted",
                bestMs: best,
                solvedAt: solved ? (entry.solvedAt ?? new Date().toISOString()) : entry.solvedAt,
              },
            },
          };
        }),

      // Index-based rather than a counter, so re-opening the Hints tab and
      // re-reading hint 1 does not inflate the count.
      revealHint: (slug, index) =>
        set((state) => {
          const entry = state.progress[slug] ?? EMPTY;
          return {
            progress: {
              ...state.progress,
              [slug]: { ...entry, hintsUsed: Math.max(entry.hintsUsed, index + 1) },
            },
          };
        }),

      markSolved: (slug, durationMs) =>
        set((state) => {
          const entry = state.progress[slug] ?? EMPTY;
          return {
            progress: {
              ...state.progress,
              [slug]: {
                ...entry,
                status: "solved",
                bestMs: durationMs
                  ? Math.min(entry.bestMs ?? Number.POSITIVE_INFINITY, durationMs)
                  : entry.bestMs,
                solvedAt: entry.solvedAt ?? new Date().toISOString(),
              },
            },
          };
        }),

      setDraft: (slug, code) => set((state) => ({ drafts: { ...state.drafts, [slug]: code } })),

      clearDraft: (slug) =>
        set((state) => {
          const drafts = { ...state.drafts };
          delete drafts[slug];
          return { drafts };
        }),

      resetProblem: (slug) =>
        set((state) => {
          const progress = { ...state.progress };
          const drafts = { ...state.drafts };
          delete progress[slug];
          delete drafts[slug];
          return { progress, drafts };
        }),

      setSettings: (patch) => set((state) => ({ settings: { ...state.settings, ...patch } })),

      resetAll: () => set({ progress: {}, drafts: {} }),

      setHydrated: () => set({ hydrated: true }),
    }),
    {
      name: STORAGE_KEY,
      version: 1,
      storage: createJSONStorage(() => localStorage),
      partialize: ({ progress, drafts, settings }) => ({ progress, drafts, settings }),
      // `hydrated` is deliberately outside partialize: server and first client
      // render both start false, so progress UI can wait instead of flashing.
      onRehydrateStorage: () => (state) => state?.setHydrated(),
    },
  ),
);

export function useProgress(slug: string): ProgressEntry {
  return useStore((state) => state.progress[slug] ?? EMPTY);
}

export function useHydrated(): boolean {
  return useStore((state) => state.hydrated);
}

export function useSolvedCount(): number {
  return useStore(
    (state) => Object.values(state.progress).filter((entry) => entry.status === "solved").length,
  );
}
