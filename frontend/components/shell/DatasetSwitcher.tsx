"use client";

import { useEffect, useRef, useState } from "react";
import { ChevronDown, Database } from "lucide-react";
import { DATASETS, useDatasetNavigation } from "@/lib/datasets";
import type { DatasetId } from "@/lib/datasets";

/**
 * Sticky app-shell dataset switcher.
 *
 * A dense context selector (not a promotional badge, not a nav tab) that lives
 * in the top-right of the shell. Switching writes `?dataset=` and persists the
 * choice, preserving the current surface while resetting incompatible item
 * selectors.
 */
export default function DatasetSwitcher() {
  const { datasetId, descriptor, setDataset } = useDatasetNavigation();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function onClick(event: MouseEvent) {
      if (ref.current && !ref.current.contains(event.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  function choose(id: DatasetId) {
    setOpen(false);
    if (id !== datasetId) setDataset(id);
  }

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 rounded-md border border-border bg-surface-raised px-2.5 py-1 text-left transition-colors hover:bg-surface"
        title="Switch dataset"
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        <Database className="h-3.5 w-3.5 text-muted" />
        <div className="leading-tight">
          <span className="block text-[9px] font-medium uppercase tracking-wider text-muted">Dataset</span>
          <span className="block text-[11px] font-semibold text-foreground">{descriptor.label}</span>
        </div>
        <ChevronDown className={`h-3.5 w-3.5 text-muted transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <div
          role="listbox"
          className="absolute right-0 top-full z-50 mt-1 w-60 overflow-hidden rounded-md border border-border bg-surface shadow-lg"
        >
          {DATASETS.map((d) => {
            const active = d.id === datasetId;
            return (
              <button
                key={d.id}
                role="option"
                aria-selected={active}
                onClick={() => choose(d.id)}
                className={`flex w-full flex-col gap-0.5 border-b border-border/60 px-3 py-2 text-left transition-colors last:border-b-0 ${
                  active ? "bg-deterministic/8" : "hover:bg-surface-raised"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-semibold text-foreground">{d.label}</span>
                  {active && (
                    <span className="rounded bg-deterministic/15 px-1.5 py-0.5 text-[9px] font-medium text-deterministic">
                      active
                    </span>
                  )}
                </div>
                <span className="text-[10px] leading-snug text-muted">{d.tagline}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
