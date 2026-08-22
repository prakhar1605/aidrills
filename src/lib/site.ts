export const site = {
  name: "aidrills",
  tagline: "AI engineering interview drills that run in your browser",
  description:
    "Timed AI engineering interview drills — attention, BM25, RRF, retries, agent loops, evals. Write Python in the browser, run the tests instantly. No signup, no API key, no server.",
  url: process.env.NEXT_PUBLIC_SITE_URL ?? "https://aidrills.vercel.app",
  repo: "https://github.com/prakhar1605/aidrills",
} as const;

export const NAV = [
  { href: "/problems", label: "Problems" },
  { href: "/roadmap", label: "Roadmap" },
  { href: "/resources", label: "Resources" },
  { href: "/contribute", label: "Contribute" },
] as const;
