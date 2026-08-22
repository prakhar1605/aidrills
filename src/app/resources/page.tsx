import type { Metadata } from "next";

import { Markdown } from "@/components/ui/Markdown";
import { resources } from "@/lib/content";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "Resources",
  description:
    "A short, curated reading list for AI engineering interviews: attention, BPE, BM25, reciprocal rank fusion, backoff, SSE, agents, evals.",
  alternates: { canonical: `${site.url}/resources` },
};

export default function ResourcesPage() {
  return (
    <div className="mx-auto w-full max-w-2xl px-5 py-12">
      <h1 className="text-2xl">Resources</h1>
      <div className="mt-6">
        <Markdown source={resources} />
      </div>
    </div>
  );
}
