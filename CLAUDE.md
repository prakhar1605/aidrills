# aidrills

LeetCode for AI Engineering interviews. Next.js App Router + TS + Tailwind.
Problems are files in `content/problems/<slug>/` — git is the CMS.
User Python runs in-browser via Pyodide in a Web Worker. No server-side code execution.
No auth until M6.

## Commands

```
pnpm dev                          build-content, then next dev
pnpm build                        build-content, then next build
pnpm test                         vitest
pnpm lint                         eslint
pnpm build-content [--check]      compile content -> src/generated/problems.json
pnpm new-problem <slug>           scaffold from content/_template

python python/test_problem.py <slug> [--solution|--starter]
python python/test_problem.py --all
pytest python/selftest -q         runner.py + mock_llm.py unit tests
```

Python tooling lives in a local `.venv` (`pip install -r python/requirements-dev.txt`).

## Conventions

- Read `docs/SPEC.md` before changing architecture. Follow the milestone order in §11.
  State which milestone you're on.
- Problem schema lives in `src/lib/schema.ts`. Any content change must pass content CI.
- `tests.py`: plain `def test_*` with `assert` **and a message**; imports only stdlib,
  numpy (if in `meta.packages`), `mock_llm`.
- Worker/client message types live in `src/lib/pyodide/client.ts`. The worker is a static
  classic script at `public/pyodide-worker.js` and cannot import them — if you change one
  side, change the other by hand.
- Pyodide version/CDN URL only in `src/lib/pyodide/const.ts`. The client passes the index
  URL to the worker in the `init` message; the worker hardcodes nothing.
- `localStorage` is touched only in `src/lib/store.ts`.
- Client components only where needed (workspace, editor, store hooks). Pages stay
  server/static. Statements and hints are rendered on the server and passed to the
  workspace as `ReactNode` props.
- No new dependency without a one-line reason. No second component library.
- Design tokens in §9 of the spec, defined as a Tailwind v4 `@theme` block in
  `src/app/globals.css`. Dark theme first.
- MDX evaluates `{` as an expression and `<` as a tag outside code fences. Statements must
  keep both inside backticks or a fenced block.

## Don'ts

- No database for content. No server execution of user code. No auth before M6. No paywalls.
- Don't "just add an API key" for anything LLM-related before M8; use `mock_llm`.
- Don't bind a CodeMirror shortcut without `Prec.highest` if `defaultKeymap` already uses it
  — `Mod-Enter` is `insertBlankLine` by default and will silently swallow Run.

## Deviations from docs/SPEC.md

Recorded so nobody "fixes" them back:

- **shadcn/ui was not installed.** Its init rewrites `globals.css` with its own token set,
  which fights §9's palette. The handful of primitives needed live in `src/components/ui/`
  and follow shadcn conventions (`cn()`, variant maps) so `shadcn add` still works later.
- **Tailwind v4** has no `tailwind.config.ts`; tokens are the `@theme` block in
  `globals.css`.
- **The worker is `public/pyodide-worker.js`,** not a bundled `src/lib/pyodide/worker.ts`.
  `importScripts` needs a classic worker, and a static file has zero bundler surface.
- **OG images use the `opengraph-image.tsx` convention** rather than a `/og/[slug]` route,
  so Next wires the metadata and prerenders them automatically.
- **`settings.vim` and `settings.theme` are not in the store.** Vim mode needs another
  dependency and light theme is post-launch (§9); the setting would be dead config.
- **PostHog is not installed.** `src/lib/analytics.ts` owns the event vocabulary and
  forwards to `window.posthog` when it exists — adding `posthog-js` is a one-line change.
- **`/dev/runner`** (M2's throwaway debug page) was not kept; the landing drill serves the
  same purpose and ships.
