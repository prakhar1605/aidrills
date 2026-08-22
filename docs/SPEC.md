# aidrills — Build Spec v1

**One line:** LeetCode for AI Engineering interviews. A user opens a problem, writes Python in the browser, runs tests instantly (no server, no API key), and tracks progress. Deployed on Vercel. Problems live in the repo as files; the site renders them.

Working name `aidrills` — rename freely, nothing below depends on it.

---

## 0. Locked decisions (don't relitigate mid-build)

- Next.js (latest stable, App Router) + TypeScript + Tailwind + shadcn/ui. pnpm. Vercel, project root = repo root.
- Problems are files in `content/problems/<slug>/`. Git is the CMS. No database for content, ever.
- User code runs client-side in Pyodide (CPython compiled to WebAssembly) inside a Web Worker. No server-side execution, ever.
- Tests are plain `def test_*():` functions with `assert`. A tiny custom runner executes them in the browser (pytest is not used in the browser). The same files run under pytest locally and in CI.
- `mock_llm` is a pure-Python fake LLM shipped into the Pyodide filesystem, so RAG / agent / eval problems are testable offline.
- Phase 1–2: zero auth, progress in localStorage. Phase 3: Supabase (GitHub OAuth) with a local→cloud migration on first login.
- Editor: CodeMirror 6. Markdown: next-mdx-remote. State: zustand + persist. Validation: zod. Tests: vitest (TS) + pytest (content).

---

## 1. Architecture

```
Browser
 ├─ Next.js pages (static, generated from content JSON at build)
 ├─ Workspace UI:  Description | Editor | Results
 ├─ zustand store ──► localStorage      (Phase 3: ──► Supabase)
 └─ Web Worker ──► Pyodide (numpy loaded on demand)
                    ├─ /py/runner.py      (test runner)
                    ├─ /py/mock_llm.py    (fake LLM)
                    ├─ submission.py      (user code, written per run)
                    └─ tests.py           (problem tests, written per run)

Build time (Vercel)
 content/problems/**  ─► scripts/build-content.ts ─► src/generated/problems.json
 python/**            ─► copied to public/py/
```

---

## 2. Repo layout

```
aidrills/
  CLAUDE.md                     # §13
  docs/SPEC.md                  # this file
  content/
    _template/                  # scaffold source for new problems
    problems/<slug>/            # §3
    tracks.json                 # track order, names, one-line descriptions, accent color
    roadmap.json                # 14-day plan → ordered problem slugs per day
    resources.md                # curated external links (the "awesome" list)
  python/
    mock_llm.py                 # fake LLM, pure python, no deps
    runner.py                   # runner used inside Pyodide
    test_problem.py             # local/CI harness: runs a problem's tests against solution or starter
    requirements-dev.txt        # pytest, numpy (CI/local only)
  scripts/
    build-content.ts            # validate + compile content → JSON; --check for CI
    new-problem.ts              # scaffold content/problems/<slug> from _template
  src/
    app/                        # routes, §5
    components/
      workspace/                # Editor, ResultsPanel, Console, Toolbar, HintsTab, SolutionTab, Timer
      problems/                 # ProblemTable, Filters, StatusBadge, TrackCard
      layout/                   # Shell, Nav, Footer
      ui/                       # shadcn
    lib/
      content.ts                # typed access to generated JSON
      schema.ts                 # zod schemas for meta.json + generated shape
      store.ts                  # zustand store (the ONLY place localStorage is touched)
      pyodide/const.ts          # PYODIDE_VERSION, CDN URL (single source of truth)
      pyodide/worker.ts         # the Web Worker
      pyodide/client.ts         # PyRunner class: warmup(), run(), terminate(); shared message types
      analytics.ts              # thin wrapper over PostHog events
    generated/problems.json     # build output, gitignored
  public/py/                    # runner.py + mock_llm.py copied at build (gitignored)
  .github/workflows/
    content-ci.yml              # pytest every problem on PR/push
    web-ci.yml                  # pnpm build + vitest
```

---

## 3. Problem format

```
content/problems/rrf-fusion/
  meta.json
  statement.md        # MDX-compatible markdown
  starter.py          # what the candidate sees first
  tests.py            # the cases
  solution.py         # reference answer + a short "what the interviewer is checking" comment block
  hints.md            # hints separated by a line containing only ---
```

`meta.json`

```json
{
  "id": 7,
  "slug": "rrf-fusion",
  "title": "Reciprocal Rank Fusion",
  "track": "retrieval",
  "difficulty": "medium",
  "timeBudgetMin": 25,
  "tags": ["ranking", "hybrid-search"],
  "companies": ["Cohere", "Glean"],
  "packages": [],
  "entryPoint": "rrf_fuse",
  "status": "published"
}
```

- `track` ∈ `foundations | retrieval | plumbing | agents | evals`
- `difficulty` ∈ `easy | medium | hard`
- `packages`: Pyodide packages to load before running, e.g. `["numpy"]`. Keep empty when possible (faster first run).
- `status`: `draft` problems are excluded from the build but still run in CI.

**Test contract**

- `tests.py` begins with `from submission import *`. In the browser the user's code is written to `submission.py`; locally `python/test_problem.py <slug> --solution|--starter` copies the chosen file to a temp dir as `submission.py` next to `tests.py` and runs pytest there.
- One `def test_*()` per case, plain `assert` with a message: `assert out == exp, f"expected {exp!r}, got {out!r}"`.
- Allowed imports: stdlib, `numpy` (only if listed in `packages`), `mock_llm`. Nothing else. No network, no file I/O.
- CI rules: `solution.py` must pass every test; `starter.py` must fail at least one (proves the tests aren't vacuous).

**Hints**: 3 per problem, progressive — nudge → approach → near-solution.

---

## 4. In-browser execution

**Worker** (`src/lib/pyodide/worker.ts`)

- `init`: load Pyodide from the CDN URL in `const.ts`, fetch `/py/runner.py` and `/py/mock_llm.py`, write both to the Pyodide FS, post `{type:"ready"}`. Post `{type:"progress", stage}` with `downloading | initializing | packages` during init.
- `run {runId, code, tests, packages}`: `loadPackage(packages)` if not already loaded; write `submission.py` and `tests.py`; call `runner.run()`; post `{type:"result", runId, results, stdout, error}`.

**Runner** (`python/runner.py`)

- Fresh import each run: `sys.modules.pop("submission", None)`, same for `tests`, so edits take effect.
- Redirect `sys.stdout` to a StringIO for the duration; return captured text as `stdout`.
- Iterate `test_*` callables in definition order. For each: time it; `AssertionError` → `failed` with the message; any other exception → `error` with a short traceback (last 3 frames); otherwise `passed`.
- If `tests.py` or `submission.py` fails to import (syntax error etc.), return `error` at top level with the traceback.
- Return JSON: `{ "results": [{ "name", "status", "message", "durationMs" }], "stdout": "..." }`.

**Client** (`src/lib/pyodide/client.ts`, class `PyRunner`)

- Singleton. `warmup()` is called on problem page mount so the runtime is ready before the first click.
- Status: `idle | loading | ready | running | error | timeout`, exposed through a hook `usePyRunner()`.
- Global run timeout 15 s → `worker.terminate()`, surface a `timeout` result ("Took longer than 15s — infinite loop?"), re-init lazily on the next run.
- Every run gets a `runId`; results for stale ids are dropped.
- Message types for worker and client live in one file and are imported by both.

First load is several MB from the CDN (cached afterwards). Show a small status chip in the toolbar: `Python runtime · loading` / `ready`.

**mock_llm v0** (`python/mock_llm.py`)

```python
llm = MockLLM(
    responses={"summarize": "Short summary.", "*": "ok"},   # match by substring in prompt, "*" = default
    fail_on_call=[2],                                       # raise RateLimitError on the 2nd call
    latency_ms=0,
)
llm.complete(prompt) -> str
llm.stream(prompt) -> Iterator[str]            # yields tokens (whitespace split)
llm.tool_call(prompt, tools) -> dict           # scripted {"name", "arguments"}
llm.calls -> list[dict]                        # every call, for assertions
count_tokens(text) -> int                      # deterministic approximation
```

Problems that need it import it directly: `from mock_llm import MockLLM, RateLimitError`.

---

## 5. Routes & UI

| Route | Job |
|---|---|
| `/` | Landing: thesis + a live runnable drill (see §9), 5 track cards, problem count |
| `/problems` | Table: title, track, difficulty, time budget, companies, status. Client-side filters (track, difficulty, tag, company, status) + search |
| `/problems/[slug]` | Workspace |
| `/tracks/[track]` | Ordered path through the track with a progress bar |
| `/roadmap` | 14-day plan rendered from `roadmap.json` |
| `/resources` | Rendered `resources.md` |
| `/contribute` | How to add a problem, link to repo + template |
| `/og/[slug]` | OG image via `next/og` |
| `sitemap.xml`, `robots.txt` | Generated from content |

**Workspace (desktop)**: resizable two-pane split.

- Left, tabs: **Description** (MDX) · **Hints** (reveal one at a time; each reveal increments `hintsUsed`) · **Solution** (confirm dialog before reveal).
- Right: CodeMirror (Python, dark theme, `Cmd/Ctrl+Enter` = Run) on top; **Results** panel below with per-test rows (✓/✗, name, ms; click to expand message) and a **Console** tab (stdout).
- Toolbar: Run · Reset to starter · Interview mode (countdown from `timeBudgetMin`, hints disabled, shows time taken on first full pass) · Mark solved (auto when all tests pass) · Share (copies URL + "Solved RRF Fusion in 14:20") · runtime status chip.
- Mobile: description + read-only solution; editor hidden with a one-line "Open on desktop to run code" note.
- Empty states and loading skeletons on every page; `?` opens the keyboard shortcuts sheet.

---

## 6. State

zustand store with `persist`, storage key `aidrills:v1`:

```ts
progress: Record<slug, {
  status: "unsolved" | "attempted" | "solved";
  attempts: number;
  bestMs?: number;
  hintsUsed: number;
  solvedAt?: string;
}>;
drafts: Record<slug, string>;        // autosaved editor content, debounced 500 ms
settings: { fontSize: number; vim: boolean; theme: "dark" | "light" };
```

Phase 3 adds `user` and a sync layer (§10). The UI never blocks on sync.

---

## 7. Content pipeline & CI

- `pnpm build` = `pnpm build-content && next build`.
- `build-content.ts`: walk `content/problems`, validate `meta.json` with zod, require all five files, split `hints.md` on `---`, compile `statement.md`, emit `problems.json` (published only) with code files inlined as strings. Any invalid problem fails the build with the path and the reason. `--check` runs validation only.
- `content-ci.yml` (PR + push): set up Python, install `python/requirements-dev.txt`, for each problem run `test_problem.py <slug> --solution` (must pass) and `--starter` (must fail), then `pnpm build-content --check`.
- `web-ci.yml`: `pnpm install`, `pnpm build`, `pnpm test`.
- `pnpm new-problem <slug>` copies `content/_template`, fills `meta.json` with the next `id`.

---

## 8. SEO, sharing, analytics

- Every problem page is static. Title: `{title} — AI Engineer interview drill`. Description: first paragraph of the statement. Canonical URL. OG image from `/og/[slug]`.
- OG card: dark, title, track accent, difficulty, "Run in your browser · no API key".
- Vercel Analytics + PostHog. Events: `run_tests`, `all_passed`, `hint_used`, `solution_revealed`, `interview_mode_start`, `share`. Properties: `slug`, `track`, `difficulty`.

---

## 9. Design direction

Subject is a test runner and a clock — build the identity from that, not from a generic dark SaaS template.

- **Hero = the product.** The landing page opens with a real drill (e.g. `rrf-fusion`) already loaded in the real editor with the timer armed at 25:00. The visitor can run it before reading anything. No hero stat blocks, no gradient blobs.
- **Palette** (tokens in `tailwind.config`): surface `#121417`, raised `#1A1D21`, text `#E6E1D6` (warm, not pure white), muted `#8C8A84`, accent `#4F7CFF`. Pass/fail use their own semantic greens/reds only inside the results panel. Each track gets one accent in `tracks.json` and it is used only in badges, the track page header, and the OG card.
- **Type**: IBM Plex Sans for UI and statements, IBM Plex Mono for code, results, timers and problem ids. One display moment — the landing headline — in Instrument Serif italic. Nowhere else.
- **Signature**: the results panel reads like a terminal test run — monospace rows appearing one by one, a final summary line `4 passed · 1 failed · 212 ms`. Keep animation to that panel and the timer; nothing else moves.
- Light theme is polish, not a launch blocker. Visible focus rings, reduced-motion respected.

---

## 10. Phase 3 — accounts & data (Supabase)

Auth: GitHub OAuth through Supabase, `@supabase/ssr`. Tables:

```
profiles(id uuid pk → auth.users, handle text unique, avatar_url, github_url, created_at)
progress(user_id, slug, status, attempts, best_ms, hints_used, solved_at, updated_at, pk(user_id, slug))
submissions(id, user_id, slug, code, passed int, total int, duration_ms, created_at)
asked_reports(id, user_id, slug, company, role, round, asked_on date, note, approved bool default false, created_at)
report_votes(report_id, user_id, pk(report_id, user_id))
```

- RLS: users read/write their own `progress` and `submissions`; `asked_reports` public-read where `approved`.
- RPC `weekly_leaderboard()` → top solvers in the last 7 days.
- `/u/[handle]` public profile. `/api/badge/[handle]` returns an SVG badge ("aidrills · 23/60 solved") with cache headers — people paste it in their README, it links back.
- Migration: on first login push local `progress`; on conflict the server wins if it already has `solved`, otherwise local wins. Drafts stay local.
- Also in Phase 3: submissions history tab, streaks, and a BYO-key interviewer for system-design prompts (OpenRouter key stored in localStorage, calls made from the client, rubric-scored feedback). No server ever touches user keys.

---

## 11. Milestones (build order)

One Claude Code session per milestone. Meet the DoD before moving on.

**M1 — Skeleton.** Next app, Tailwind, shadcn, layout shell, `schema.ts`, `build-content.ts`, two sample problems under `content/problems`, `/problems` list, `/problems/[slug]` rendering statement + starter read-only.
DoD: `pnpm build` green; both pages render; invalid `meta.json` fails the build with a clear message.

**M2 — Runner.** `python/runner.py`, `python/mock_llm.py` (v0 above), `test_problem.py`, Pyodide worker + `PyRunner` + `usePyRunner`, and a throwaway `/dev/runner` page with a textarea and a Run button.
DoD: sample solution → all green; starter → red; `while True: pass` → timeout surfaced and the next run works; a `print()` shows up in stdout.

**M3 — Workspace.** CodeMirror, results + console panel, toolbar (Run, Reset), autosaved drafts, progress store, auto mark-solved, status badges on the list page.
DoD: solve a problem end-to-end; refresh keeps the code and the solved status.

**M4 — Content v1.** The 12 starred problems in §12, Hints + Solution tabs, `/tracks/[track]`, `new-problem` script, `_template`, `content-ci.yml`.
DoD: CI green on a PR that adds a problem; a PR with a broken solution goes red.

**M5 — Launch polish.** Landing with live drill, roadmap, resources, contribute page, interview mode, share + OG, SEO, analytics, 404/empty states, mobile read-only, 30+ problems, custom domain on Vercel.
DoD: Lighthouse ≥ 90 on `/` and a problem page; production deploy on the domain. → **Launch.**

**M6 — Accounts.** Supabase auth, progress sync + migration, profile page, leaderboard, badge endpoint.

**M7 — Community.** Asked-at reports + votes, submissions history, streaks.

**M8 — Interviewer.** BYO-key design-round interviewer.

---

## 12. Initial problem bank (★ = M4 set; aim 30+ by M5)

- **Foundations**: ★ BPE tokenizer (train + encode) · ★ scaled dot-product attention (numpy) · KV-cache step decode · ★ top-k / top-p sampling · RoPE apply · softmax with temperature · cosine-similarity top-k · mean-pooled embeddings
- **Retrieval**: ★ fixed-size chunker with overlap · ★ BM25 · ★ reciprocal rank fusion · MMR re-ranking · recursive character splitter · inverted index · near-duplicate chunk dedupe
- **LLM plumbing**: ★ retry with exponential backoff + jitter (mock 429s) · token-bucket rate limiter · ★ SSE stream parser · ★ JSON output validate-and-repair · semantic cache with similarity threshold · cost estimator · prompt template renderer with escaping
- **Agents**: ★ tool-calling loop with a step budget · ReAct output parser · sliding-window memory with summarization · plan → execute with retry · tool-schema validator · parallel tool calls with dependency order
- **Evals & safety**: ★ exact-match / F1 scorer · LLM-as-judge harness (mock) · ★ prompt-injection detector (heuristics) · PII redactor · pairwise preference aggregator (Elo) · eval dataset dedupe + split

---

## 13. CLAUDE.md (paste at repo root)

```md
# aidrills
LeetCode for AI Engineering interviews. Next.js App Router + TS + Tailwind + shadcn.
Problems are files in content/problems/<slug>/ — git is the CMS.
User Python runs in-browser via Pyodide in a Web Worker. No server-side code execution. No auth until M6.

## Commands
pnpm dev · pnpm build (runs build-content first) · pnpm test (vitest)
python python/test_problem.py <slug> --solution|--starter · pnpm new-problem <slug>

## Conventions
- Read docs/SPEC.md before changing architecture. Follow the milestone order in §11. State which milestone you're on.
- Problem schema lives in src/lib/schema.ts. Any content change must pass content-ci.
- tests.py: plain `def test_*` with assert; imports only stdlib, numpy (if in meta.packages), mock_llm.
- Worker/client message types live in src/lib/pyodide/client.ts and are imported by both sides.
- Pyodide version/CDN URL only in src/lib/pyodide/const.ts.
- localStorage is touched only in src/lib/store.ts.
- Client components only where needed (workspace, editor, store hooks). Pages stay server/static.
- No new dependency without a one-line reason. shadcn for UI; no second component library.
- Design tokens in §9 of the spec. Dark theme first.

## Don'ts
- No database for content. No server execution of user code. No auth before M6. No paywalls.
- Don't "just add an API key" for anything LLM-related before M8; use mock_llm.
```

---

## 14. Working with Claude Code

- Commit `CLAUDE.md` and `docs/SPEC.md` before writing any app code. Open each session with: "We're on M<n>. Read CLAUDE.md and docs/SPEC.md §<relevant sections>, then propose a plan."
- Use plan mode for M2 and M6 — the two places where a wrong structure is expensive. Approve the plan, then let it implement.
- Build `/dev/runner` before the real workspace. Debug Pyodide in isolation; it is the only hard part of this project.
- After every milestone: `pnpm build`, `pnpm test`, the Python harness on all problems, commit, push → Vercel preview.
- Ask for vitest coverage on `build-content` validation and the runner result parsing; pytest on `mock_llm`.
- If it proposes a server route for running code, or an API key for tests, say no and point to §0.
- Scaffold problems with it, then verify every test and solution yourself. Tests are the product.

---

## 15. Non-goals for v1

Hidden tests, a second language (TypeScript track comes after M6), server sandboxes, anything LLM-powered before M8, DSA or classical-ML problems, an editor on mobile.
