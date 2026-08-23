import { MDXRemote } from "next-mdx-remote/rsc";
import remarkGfm from "remark-gfm";

import { cn } from "@/lib/utils";

/**
 * Statements, hints and resources are MDX compiled at build time, so a broken
 * statement fails `next build` rather than a page view.
 *
 * remark-gfm: statements use tables to specify signal weights, PII types and
 * the like. Without it those render as a paragraph full of pipe characters.
 *
 * Author's note for content: outside code fences, MDX evaluates `{` as an
 * expression and `<` as a tag. Keep braces and angle brackets inside backticks.
 */
export function Markdown({ source, className }: { source: string; className?: string }) {
  return (
    <div className={cn("prose-drill", className)}>
      <MDXRemote
        source={source}
        options={{ mdxOptions: { remarkPlugins: [remarkGfm] } }}
      />
    </div>
  );
}
