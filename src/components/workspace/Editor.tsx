"use client";

import { indentWithTab } from "@codemirror/commands";
import { python } from "@codemirror/lang-python";
import { Compartment, EditorState, Prec } from "@codemirror/state";
import { oneDark } from "@codemirror/theme-one-dark";
import { EditorView, keymap } from "@codemirror/view";
import { basicSetup } from "codemirror";
import { useEffect, useRef } from "react";

type EditorProps = {
  /** Initial document. Pushed into the view again whenever `resetSignal` changes. */
  value: string;
  onChange: (value: string) => void;
  onRun: () => void;
  fontSize: number;
  /** Bump to force the document back to `value` (Reset to starter, Load solution). */
  resetSignal: number;
  /** Read at mount only; the workspace never toggles this on a live editor. */
  readOnly?: boolean;
};

/**
 * CodeMirror 6 is imperative and owns its own document. React only ever
 * pushes: the initial value at mount, and a replacement when `resetSignal`
 * changes. Every keystroke flows the other way through `onChange`.
 */
export function Editor({
  value,
  onChange,
  onRun,
  fontSize,
  resetSignal,
  readOnly = false,
}: EditorProps) {
  const host = useRef<HTMLDivElement>(null);
  const view = useRef<EditorView | null>(null);
  const font = useRef<Compartment | null>(null);

  // Props read from inside CodeMirror callbacks. Kept in a ref so the view is
  // built exactly once and handlers never go stale.
  const latest = useRef({ value, onChange, onRun, fontSize, readOnly });
  useEffect(() => {
    latest.current = { value, onChange, onRun, fontSize, readOnly };
  });

  useEffect(() => {
    const parent = host.current;
    if (!parent) return;

    const { value: doc, fontSize: size, readOnly: locked } = latest.current;
    const compartment = new Compartment();
    font.current = compartment;

    const instance = new EditorView({
      state: EditorState.create({
        doc,
        extensions: [
          basicSetup,
          python(),
          oneDark,
          // Prec.highest, or defaultKeymap's own Mod-Enter (insertBlankLine)
          // wins the lookup and Run silently never fires.
          Prec.highest(
            keymap.of(
              ["Mod-Enter", "Ctrl-Enter", "Shift-Enter"].map((key) => ({
                key,
                preventDefault: true,
                run: () => {
                  latest.current.onRun();
                  return true;
                },
              })),
            ),
          ),
          keymap.of([indentWithTab]),
          EditorView.updateListener.of((update) => {
            if (update.docChanged) latest.current.onChange(update.state.doc.toString());
          }),
          EditorView.editable.of(!locked),
          EditorState.readOnly.of(locked),
          compartment.of(EditorView.theme({ "&": { fontSize: `${size}px` } })),
        ],
      }),
      parent,
    });
    view.current = instance;

    return () => {
      instance.destroy();
      view.current = null;
      font.current = null;
    };
  }, []);

  useEffect(() => {
    const instance = view.current;
    if (!instance) return;
    const next = latest.current.value;
    if (instance.state.doc.toString() === next) return;
    instance.dispatch({
      changes: { from: 0, to: instance.state.doc.length, insert: next },
    });
  }, [resetSignal]);

  useEffect(() => {
    const compartment = font.current;
    if (!compartment) return;
    view.current?.dispatch({
      effects: compartment.reconfigure(
        EditorView.theme({ "&": { fontSize: `${fontSize}px` } }),
      ),
    });
  }, [fontSize]);

  return <div ref={host} className="h-full overflow-hidden" />;
}
