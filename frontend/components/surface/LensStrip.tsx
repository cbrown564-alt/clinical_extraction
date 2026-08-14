"use client";

import type { ReactNode } from "react";
import type { DatasetTone } from "@/lib/datasets";

/** Lens tones: every dataset tone, plus the dark `foreground` "All" fill. */
export type LensTone = DatasetTone | "foreground";

export interface LensItem {
  /** Stable id used for selection. */
  id: string;
  label: string;
  /** Small second line under the label (counts, summary, "Awaiting trace"). */
  sublabel?: ReactNode;
  /** Pill content beside the label (e.g. a count or "3/4"). */
  count?: ReactNode;
  /** Active solid-fill tone for this lens. `foreground` is the dark "All" fill. */
  tone: LensTone;
  icon?: ReactNode;
  /** This individual lens cannot be selected (kept visible, dimmed). */
  disabled?: boolean;
  /** Fixed-width (no flex-grow) – e.g. the "All families" lead button. */
  fixed?: boolean;
  /** Full label shown on hover when the visible sublabel is truncated. */
  title?: string;
}

/** Solid active fill per tone. Fixed strings so Tailwind can extract them. */
const SOLID: Record<LensTone, string> = {
  foreground: "border-foreground bg-foreground text-surface shadow-sm",
  deterministic: "border-deterministic bg-deterministic text-surface shadow-sm",
  "deterministic-alt": "border-deterministic-alt bg-deterministic-alt text-surface shadow-sm",
  llm: "border-llm bg-llm text-surface shadow-sm",
  hybrid: "border-hybrid bg-hybrid text-surface shadow-sm",
  success: "border-success bg-success text-surface shadow-sm",
  error: "border-error bg-error text-surface shadow-sm",
  muted: "border-muted bg-muted text-surface shadow-sm",
};

/**
 * The lens row both datasets wear directly under the control bar.
 *
 * Gan fills it with the five pipeline stages (selecting one drives the
 * inspector); ExECTv2 fills it with the four key-finding families plus an
 * "All families" lead (selecting one filters the inspector panels). Same shape,
 * same active look, same interaction – only the cells differ. Replaces the
 * dataset-specific StageStrip and FamilyStrip.
 */
export default function LensStrip({
  items,
  activeId,
  onSelect,
  /** When false every lens is dimmed and inert (Gan's "awaiting trace" state). */
  enabled = true,
}: {
  items: LensItem[];
  activeId: string;
  onSelect: (id: string) => void;
  enabled?: boolean;
}) {
  return (
    <div className="min-w-0 shrink-0 overflow-x-auto border-b border-border bg-surface px-4 py-2">
      <div className="flex w-full min-w-0 items-stretch gap-1.5">
        {items.map((item) => {
          const isActive = item.id === activeId;
          const interactive = enabled && !item.disabled;
          const width = item.fixed ? "w-auto shrink-0" : "min-w-0 flex-1";
          return (
            <button
              key={item.id}
              title={item.title}
              onClick={() => interactive && onSelect(item.id)}
              disabled={!interactive}
              className={`flex min-w-0 flex-col justify-center gap-0.5 overflow-hidden rounded-md border px-3 py-1.5 text-left transition-colors ${width} ${
                isActive
                  ? SOLID[item.tone]
                  : interactive
                  ? "border-border bg-surface text-foreground hover:bg-surface-raised hover:shadow-sm"
                  : "border-border/60 bg-surface-raised/50 text-muted cursor-default"
              }`}
            >
              <div className="flex min-w-0 items-center gap-1.5">
                {item.icon}
                <span className="truncate text-xs font-semibold">{item.label}</span>
                {item.count !== undefined && (
                  <span
                    className={`ml-0.5 shrink-0 rounded-full px-1.5 py-0 text-[11px] font-semibold ${
                      isActive ? "bg-surface/25 text-surface" : "bg-surface-raised text-muted"
                    }`}
                  >
                    {item.count}
                  </span>
                )}
              </div>
              {item.sublabel !== undefined && (
                <div className={`min-w-0 truncate text-[11px] leading-tight ${isActive ? "text-surface/90" : "text-muted"}`}>
                  {item.sublabel}
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
