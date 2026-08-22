"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";

type Props = {
  solution: string;
  onLoadIntoEditor?: () => void;
  onReveal: () => void;
  /** Skip the confirmation — the mobile page shows the solution as reference. */
  alwaysVisible?: boolean;
};

export function SolutionTab({ solution, onLoadIntoEditor, onReveal, alwaysVisible }: Props) {
  const [revealed, setRevealed] = useState(Boolean(alwaysVisible));

  if (!revealed) {
    return (
      <div className="rounded-lg border border-line bg-raised p-5">
        <h3 className="text-sm font-medium">Show the reference solution?</h3>
        <p className="mt-1.5 max-w-prose text-sm text-muted">
          You cannot unsee it. If you are stuck, the third hint is nearly the answer and
          costs you less. Revealing is recorded against this problem.
        </p>
        <Button
          variant="outline"
          className="mt-4"
          onClick={() => {
            setRevealed(true);
            onReveal();
          }}
        >
          Show solution
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {onLoadIntoEditor && (
        <div className="flex justify-end">
          <Button size="sm" variant="ghost" onClick={onLoadIntoEditor}>
            Load into editor
          </Button>
        </div>
      )}
      <pre className="overflow-x-auto rounded-lg border border-line bg-sunken p-4 font-mono text-xs leading-relaxed">
        <code>{solution}</code>
      </pre>
    </div>
  );
}
