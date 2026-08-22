"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { NAV, site } from "@/lib/site";
import { useHydrated, useSolvedCount } from "@/lib/store";
import { cn } from "@/lib/utils";

export function Nav() {
  const pathname = usePathname();
  const solved = useSolvedCount();
  const hydrated = useHydrated();

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-surface/85 backdrop-blur-sm">
      <div className="mx-auto flex h-14 w-full max-w-6xl items-center gap-4 overflow-x-auto px-5 sm:gap-6">
        <Link
          href="/"
          className="flex shrink-0 items-center gap-2 font-mono text-sm tracking-tight"
        >
          <span className="inline-block h-2 w-2 rounded-full bg-accent" aria-hidden />
          <span className="font-medium">{site.name}</span>
        </Link>

        <nav className="flex shrink-0 items-center gap-1 text-sm" aria-label="Main">
          {NAV.map((item) => {
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "rounded px-2 py-1.5 whitespace-nowrap transition-colors sm:px-2.5",
                  active ? "text-ink" : "text-muted hover:text-ink",
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="ml-auto flex shrink-0 items-center gap-4 pl-2">
          {hydrated && solved > 0 && (
            <span className="hidden font-mono text-xs text-muted sm:inline">
              {solved} solved
            </span>
          )}
          <a
            href={site.repo}
            target="_blank"
            rel="noreferrer noopener"
            className="text-sm text-muted transition-colors hover:text-ink"
          >
            GitHub
          </a>
        </div>
      </div>
    </header>
  );
}
