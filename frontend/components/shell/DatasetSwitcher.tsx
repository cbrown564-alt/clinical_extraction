"use client";

import { useEffect, useId, useRef, useState } from "react";
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
  const triggerRef = useRef<HTMLButtonElement>(null);
  const optionRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const listboxId = useId();

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

  function focusOption(index: number) {
    optionRefs.current[index]?.focus();
  }

  function openAndFocusSelected() {
    setOpen(true);
    window.requestAnimationFrame(() => {
      const selectedIndex = Math.max(0, DATASETS.findIndex((dataset) => dataset.id === datasetId));
      focusOption(selectedIndex);
    });
  }

  function onTriggerKeyDown(event: React.KeyboardEvent<HTMLButtonElement>) {
    if (event.key === "ArrowDown" || event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openAndFocusSelected();
    }
    if (event.key === "Escape" && open) {
      event.preventDefault();
      setOpen(false);
    }
  }

  function onOptionKeyDown(event: React.KeyboardEvent<HTMLButtonElement>, index: number) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      focusOption((index + 1) % DATASETS.length);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      focusOption((index - 1 + DATASETS.length) % DATASETS.length);
    } else if (event.key === "Home") {
      event.preventDefault();
      focusOption(0);
    } else if (event.key === "End") {
      event.preventDefault();
      focusOption(DATASETS.length - 1);
    } else if (event.key === "Escape") {
      event.preventDefault();
      setOpen(false);
      triggerRef.current?.focus();
    }
  }

  return (
    <div ref={ref} className="relative">
      <button
        ref={triggerRef}
        type="button"
        onClick={() => setOpen((v) => !v)}
        onKeyDown={onTriggerKeyDown}
        className="flex min-h-7 items-center gap-1.5 rounded-md px-2 py-1 text-left transition-colors hover:bg-surface-raised"
        aria-label={`Dataset: ${descriptor.label}. Switch dataset`}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={open ? listboxId : undefined}
      >
        <Database className="h-3.5 w-3.5 text-muted" />
        <span className="hidden text-xs font-semibold text-foreground sm:inline">{descriptor.label}</span>
        <ChevronDown className={`hidden h-3.5 w-3.5 text-muted transition-transform sm:block ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <div
          id={listboxId}
          role="listbox"
          aria-label="Dataset"
          className="absolute right-0 top-full z-50 mt-1 w-60 overflow-hidden rounded-md border border-border bg-surface shadow-lg"
        >
          {DATASETS.map((d, index) => {
            const active = d.id === datasetId;
            return (
              <button
                ref={(node) => {
                  optionRefs.current[index] = node;
                }}
                key={d.id}
                type="button"
                role="option"
                aria-selected={active}
                onClick={() => choose(d.id)}
                onKeyDown={(event) => onOptionKeyDown(event, index)}
                className={`flex w-full flex-col gap-0.5 border-b border-border/60 px-3 py-2 text-left transition-colors last:border-b-0 ${
                  active ? "bg-deterministic/8" : "hover:bg-surface-raised"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-foreground">{d.label}</span>
                  {active && (
                    <span className="rounded bg-deterministic/15 px-1.5 py-0.5 text-[11px] font-medium text-deterministic">
                      active
                    </span>
                  )}
                </div>
                <span className="text-[11px] leading-snug text-muted">{d.tagline}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
