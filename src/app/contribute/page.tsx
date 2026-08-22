import type { Metadata } from "next";

import { Markdown } from "@/components/ui/Markdown";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "Add a drill",
  description:
    "How to contribute an AI engineering interview drill: six files in a folder, tests that CI verifies both ways.",
  alternates: { canonical: `${site.url}/contribute` },
};

const GUIDE = `
The best drills come from questions people were actually asked. If you got one in a
screen and it is not here, it belongs here.

A problem is six files in one folder. Git is the CMS — there is no database and no
admin panel.

\`\`\`text
content/problems/<slug>/
  meta.json      track, difficulty, time budget, tags, companies, entry point
  statement.md   the question, the contract, and what the interviewer is checking
  starter.py     what the candidate sees first
  tests.py       the cases
  solution.py    the reference answer
  hints.md       three hints, separated by a line containing only ---
\`\`\`

## Scaffold it

\`\`\`bash
pnpm new-problem near-duplicate-dedupe
\`\`\`

That copies the template and assigns the next free id, with \`status\` set to
\`draft\` — drafts stay off the site but CI still runs their tests, so a
half-finished problem cannot rot.

## Write the tests first

The tests are the product. A drill with weak tests is worse than no drill, because it
teaches the wrong thing and looks authoritative doing it.

- \`tests.py\` starts with \`from submission import *\`.
- One \`def test_*()\` per case, plain \`assert\` with a message:
  \`assert out == exp, f"expected {exp!r}, got {out!r}"\`.
- Imports are limited to the standard library, \`numpy\` (only if you list it in
  \`packages\`), and \`mock_llm\`. No network, no file I/O.
- Cover the degenerate cases explicitly: empty input, a single element, the tie.

## Check it both ways

\`\`\`bash
python python/test_problem.py <slug>
\`\`\`

CI enforces two rules on every problem, on every push:

1. \`solution.py\` passes every test.
2. \`starter.py\` fails at least one — proof the tests are not vacuous.

Then flip \`status\` to \`"published"\` and open a PR.

## Style notes

- The statement ends with a short "What the interviewer is checking" section. That
  paragraph is why someone comes back.
- Three hints, progressive: a nudge, then the approach, then near-solution.
- Anything LLM-shaped uses \`mock_llm\`. Never an API key — see the non-goals in the
  spec.
- Outside code fences, MDX evaluates \`{\` as an expression and \`<\` as a tag. Keep
  both inside backticks.
`;

export default function ContributePage() {
  return (
    <div className="mx-auto w-full max-w-2xl px-5 py-12">
      <h1 className="text-2xl">Add a drill</h1>
      <div className="mt-6">
        <Markdown source={GUIDE} />
      </div>
      <div className="mt-10 flex flex-wrap gap-3 border-t border-line pt-6 text-sm">
        <a
          href={site.repo}
          target="_blank"
          rel="noreferrer noopener"
          className="rounded-md border border-line-strong px-3 py-2 transition-colors hover:bg-raised"
        >
          Open the repo
        </a>
        <a
          href={`${site.repo}/tree/main/content/_template`}
          target="_blank"
          rel="noreferrer noopener"
          className="rounded-md border border-line px-3 py-2 text-muted transition-colors hover:text-ink"
        >
          The template
        </a>
        <a
          href={`${site.repo}/tree/main/docs/SPEC.md`}
          target="_blank"
          rel="noreferrer noopener"
          className="rounded-md border border-line px-3 py-2 text-muted transition-colors hover:text-ink"
        >
          The spec
        </a>
      </div>
    </div>
  );
}
