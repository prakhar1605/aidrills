"use client";

/**
 * One named event vocabulary for the whole app.
 *
 * Vercel Analytics handles page views. Product events go to PostHog when it is
 * present on `window` -- adding posthog-js is then a one-line change in the
 * layout and nothing here has to move. Until then this is a no-op in
 * production and a console line in development.
 */

export type AnalyticsEvent =
  | "run_tests"
  | "all_passed"
  | "hint_used"
  | "solution_revealed"
  | "interview_mode_start"
  | "share";

type Props = {
  slug?: string;
  track?: string;
  difficulty?: string;
  [key: string]: string | number | boolean | undefined;
};

type PostHogLike = { capture: (event: string, props?: Props) => void };

export function track(event: AnalyticsEvent, props: Props = {}): void {
  if (typeof window === "undefined") return;

  const posthog = (window as unknown as { posthog?: PostHogLike }).posthog;
  if (posthog?.capture) {
    posthog.capture(event, props);
    return;
  }

  if (process.env.NODE_ENV === "development") {
    console.debug(`[analytics] ${event}`, props);
  }
}
