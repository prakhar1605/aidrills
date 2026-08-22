import Link from "next/link";

import { PYODIDE_VERSION } from "@/lib/pyodide/const";
import { site } from "@/lib/site";

export function Footer() {
  return (
    <footer className="border-t border-line">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-3 px-5 py-8 text-xs text-muted sm:flex-row sm:items-center sm:justify-between">
        <p className="font-mono">
          Your code runs in this tab, on Pyodide {PYODIDE_VERSION}. Nothing is uploaded.
        </p>
        <nav className="flex items-center gap-4" aria-label="Footer">
          <Link href="/problems" className="transition-colors hover:text-ink">
            Problems
          </Link>
          <Link href="/contribute" className="transition-colors hover:text-ink">
            Add a problem
          </Link>
          <a
            href={site.repo}
            target="_blank"
            rel="noreferrer noopener"
            className="transition-colors hover:text-ink"
          >
            Source
          </a>
        </nav>
      </div>
    </footer>
  );
}
