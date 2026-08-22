#!/usr/bin/env python3
"""Run a problem's tests under real pytest, locally and in CI.

    python python/test_problem.py rrf-fusion --solution   # must pass
    python python/test_problem.py rrf-fusion --starter    # must fail
    python python/test_problem.py --all                   # both, every problem

The browser uses python/runner.py instead; this harness exists so the same
tests.py is verified by the real thing before it ever ships.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS = ROOT / "content" / "problems"
MOCK_LLM = ROOT / "python" / "mock_llm.py"

GREEN, RED, DIM, RESET = "\033[32m", "\033[31m", "\033[2m", "\033[0m"


def run_once(slug: str, which: str, verbose: bool = False) -> tuple[bool, str]:
    """Run `slug`'s tests against solution.py or starter.py. Returns (passed, output)."""
    problem = PROBLEMS / slug
    source = problem / f"{which}.py"
    tests = problem / "tests.py"
    for path in (source, tests):
        if not path.exists():
            return False, f"missing {path.relative_to(ROOT)}"

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        shutil.copy(source, work / "submission.py")
        shutil.copy(tests, work / "tests.py")
        shutil.copy(MOCK_LLM, work / "mock_llm.py")
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "tests.py", "-q", "--no-header", "-p", "no:cacheprovider"],
            cwd=work,
            capture_output=True,
            text=True,
        )
    output = (proc.stdout + proc.stderr).strip()
    if verbose:
        print(output)
    return proc.returncode == 0, output


def check(slug: str, verbose: bool = False) -> bool:
    """solution.py must pass every test; starter.py must fail at least one."""
    ok = True

    passed, output = run_once(slug, "solution", verbose)
    if passed:
        print(f"  {GREEN}pass{RESET} solution")
    else:
        ok = False
        print(f"  {RED}FAIL{RESET} solution -- must pass every test")
        print(indent(output))

    failed_as_expected, output = run_once(slug, "starter", verbose)
    if not failed_as_expected:
        print(f"  {GREEN}pass{RESET} starter fails")
    else:
        ok = False
        print(f"  {RED}FAIL{RESET} starter passed -- the tests are vacuous")

    return ok


def indent(text: str) -> str:
    return "\n".join(f"    {DIM}{line}{RESET}" for line in text.splitlines()[-25:])


def all_slugs() -> list[str]:
    return sorted(
        p.name
        for p in PROBLEMS.iterdir()
        if p.is_dir() and (p / "meta.json").exists()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", nargs="?", help="problem slug, e.g. rrf-fusion")
    parser.add_argument("--solution", action="store_true", help="run against solution.py")
    parser.add_argument("--starter", action="store_true", help="run against starter.py")
    parser.add_argument("--all", action="store_true", help="check every problem")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if args.all or not args.slug:
        slugs = all_slugs()
        if not slugs:
            print("no problems found in content/problems")
            return 1
        failures = []
        for slug in slugs:
            meta = json.loads((PROBLEMS / slug / "meta.json").read_text())
            print(f"{slug} {DIM}({meta.get('track', '?')} / {meta.get('difficulty', '?')}){RESET}")
            if not check(slug, args.verbose):
                failures.append(slug)
        print()
        if failures:
            print(f"{RED}{len(failures)} of {len(slugs)} problems failed:{RESET} {', '.join(failures)}")
            return 1
        print(f"{GREEN}all {len(slugs)} problems ok{RESET}")
        return 0

    if args.solution or args.starter:
        which = "solution" if args.solution else "starter"
        passed, output = run_once(args.slug, which, verbose=True)
        if which == "solution":
            return 0 if passed else 1
        return 1 if passed else 0  # starter is expected to fail

    return 0 if check(args.slug, args.verbose) else 1


if __name__ == "__main__":
    sys.exit(main())
