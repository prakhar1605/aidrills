"use client";

import { Button } from "@/components/ui/Button";

type Props = {
  hints: React.ReactNode[];
  revealed: number;
  onReveal: (index: number) => void;
  locked: boolean;
};

const LABELS = ["Nudge", "Approach", "Near-solution"];

export function HintsTab({ hints, revealed, onReveal, locked }: Props) {
  if (locked) {
    return (
      <p className="font-mono text-xs text-muted">
        Hints are disabled in interview mode. Leave interview mode to read them — the
        run stops counting when you do.
      </p>
    );
  }

  return (
    <ol className="flex flex-col gap-3">
      {hints.map((hint, index) => {
        const open = index < revealed;
        const available = index <= revealed;
        return (
          <li key={index} className="rounded-lg border border-line bg-raised">
            <div className="flex items-center gap-3 px-3 py-2">
              <span className="font-mono text-[11px] text-muted">
                {index + 1} · {LABELS[index] ?? "Hint"}
              </span>
              {!open && (
                <Button
                  size="sm"
                  variant="ghost"
                  className="ml-auto"
                  disabled={!available}
                  onClick={() => onReveal(index)}
                >
                  {available ? "Reveal" : "Locked"}
                </Button>
              )}
            </div>
            {open && <div className="border-t border-line px-3 py-3">{hint}</div>}
          </li>
        );
      })}
    </ol>
  );
}
