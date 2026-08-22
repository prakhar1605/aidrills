import Link from "next/link";

export default function NotFound() {
  return (
    <div className="mx-auto flex w-full max-w-2xl flex-1 flex-col justify-center px-5 py-24">
      <p className="font-mono text-xs text-muted">404</p>
      <h1 className="mt-2 text-2xl">No drill here.</h1>
      <p className="mt-3 max-w-prose text-sm text-muted">
        The page you asked for does not exist. If it is a problem you think should,
        that is a contribution waiting to happen.
      </p>
      <div className="mt-6 flex gap-4 text-sm">
        <Link href="/problems" className="text-accent underline underline-offset-2">
          All drills
        </Link>
        <Link href="/roadmap" className="text-accent underline underline-offset-2">
          The 14-day plan
        </Link>
        <Link href="/contribute" className="text-accent underline underline-offset-2">
          Add a drill
        </Link>
      </div>
    </div>
  );
}
