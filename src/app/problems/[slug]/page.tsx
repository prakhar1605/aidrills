import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { Markdown } from "@/components/ui/Markdown";
import { Workspace } from "@/components/workspace/Workspace";
import { getProblem, nextInTrack, problems, summary } from "@/lib/content";
import { site } from "@/lib/site";

export function generateStaticParams() {
  return problems.map((problem) => ({ slug: problem.slug }));
}

export async function generateMetadata({
  params,
}: PageProps<"/problems/[slug]">): Promise<Metadata> {
  const { slug } = await params;
  const problem = getProblem(slug);
  if (!problem) return {};

  const title = `${problem.title} — AI Engineer interview drill`;
  const description = summary(problem);
  const url = `${site.url}/problems/${problem.slug}`;

  return {
    title,
    description,
    alternates: { canonical: url },
    keywords: [...problem.tags, problem.track, "AI engineer interview", "LLM interview"],
    openGraph: { title, description, url, type: "article" },
    twitter: { card: "summary_large_image", title, description },
  };
}

export default async function ProblemPage({ params }: PageProps<"/problems/[slug]">) {
  const { slug } = await params;
  const problem = getProblem(slug);
  if (!problem) notFound();

  const next = nextInTrack(problem);

  return (
    <Workspace
      problem={{
        id: problem.id,
        slug: problem.slug,
        title: problem.title,
        track: problem.track,
        difficulty: problem.difficulty,
        timeBudgetMin: problem.timeBudgetMin,
        packages: problem.packages,
        entryPoint: problem.entryPoint,
        companies: problem.companies,
        starter: problem.starter,
        tests: problem.tests,
        solution: problem.solution,
      }}
      statement={<Markdown source={problem.statement} />}
      hints={problem.hints.map((hint, index) => (
        <Markdown key={index} source={hint} />
      ))}
      next={next && { slug: next.slug, title: next.title }}
    />
  );
}
