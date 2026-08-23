# aidrills

**LeetCode for AI engineering interviews.** Open a problem, write Python in the browser,
run real tests instantly. No signup, no API key, no server — your code executes in a Web
Worker in your own tab on [Pyodide](https://pyodide.org/) (CPython compiled to
WebAssembly).

Thirty-four drills across five tracks: attention, RoPE, KV caching and BPE; BM25,
reciprocal rank fusion and MMR; backoff, token buckets and SSE parsing; agent loops,
schedulers and memory; eval scorers, LLM judges and injection detection.

```bash
pnpm install
pnpm dev
```

## How it works

```
Browser
 ├─ Next.js pages (static, generated from content JSON at build time)
 ├─ Workspace UI:  Description | Editor | Results
 ├─ zustand store ──► localStorage
 └─ Web Worker ──► Pyodide (numpy on demand)
                    ├─ /py/runner.py      the test runner
                    ├─ /py/mock_llm.py    a pure-Python fake LLM
                    ├─ submission.py      your code, written per run
                    └─ tests.py           the problem's tests

Build
 content/problems/**  ─► scripts/build-content.ts ─► src/generated/problems.json
 python/**            ─► public/py/
```

There is no database and no CMS. A problem is six files in a folder, and git is the
source of truth. `docs/SPEC.md` is the full design document.

## A problem

```
content/problems/rrf-fusion/
  meta.json      track, difficulty, time budget, tags, companies, entry point
  statement.md   the question, the contract, and what the interviewer is checking
  starter.py     what the candidate sees first
  tests.py       the cases
  solution.py    the reference answer
  hints.md       three hints, nudge -> approach -> near-solution
```

CI enforces two rules on every problem, on every push:

1. `solution.py` passes every test.
2. `starter.py` fails at least one — proof the tests are not vacuous.

The same `tests.py` runs under real pytest locally and under a ~100-line runner in the
browser, so nothing ships that pytest has not already verified.

## Commands

| | |
|---|---|
| `pnpm dev` | build content, then Next dev server |
| `pnpm build` | build content, then a production build |
| `pnpm test` | vitest — schema, content rules, utils |
| `pnpm lint` | eslint |
| `pnpm build-content --check` | validate content without emitting |
| `pnpm new-problem <slug>` | scaffold a new drill from the template |
| `python python/test_problem.py --all` | every solution passes, every starter fails |
| `pytest python/selftest -q` | unit tests for `runner.py` and `mock_llm.py` |

Python tooling needs a virtualenv:

```bash
python3 -m venv .venv && ./.venv/bin/pip install -r python/requirements-dev.txt
```

## Contributing

The best drills come from questions people were actually asked. `pnpm new-problem <slug>`,
write the tests first, check it both ways, flip `status` to `published`, open a PR. The
`/contribute` page has the full walkthrough.

## Deploying

Vercel, project root = repo root. `pnpm build` runs the content build first. Set
`NEXT_PUBLIC_SITE_URL` to the production origin so canonical URLs, the sitemap and OG
tags point at the right place.

## Stack

Next.js 16 (App Router) · TypeScript · Tailwind v4 · CodeMirror 6 · zustand · zod ·
next-mdx-remote · Pyodide 0.28 · vitest · pytest
