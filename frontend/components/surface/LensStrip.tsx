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
  /** Fixed-width (no flex-grow) — e.g. the "All families" lead button. */
  fixed?: boolean;
}

/** Solid active fill per tone. Fixed strings so Tailwind can extract them. */
const SOLID: Record<LensTone, string> = {
  foreground: "border-foreground bg-foreground text-white shadow-sm",
  deterministic: "border-deterministic bg-deterministic text-white shadow-sm",
  "deterministic-alt": "border-deterministic-alt bg-deterministic-alt text-white shadow-sm",
  llm: "border-llm bg-llm text-white shadow-sm",
  hybrid: "border-hybrid bg-hybrid text-white shadow-sm",
  success: "border-success bg-success text-white shadow-sm",
  error: "border-error bg-error text-white shadow-sm",
  muted: "border-muted bg-muted text-white shadow-sm",
};

/**
 * The lens row both datasets wear directly under the control bar.
 *
 * Gan fills it with the five pipeline stages (selecting one drives the
 * inspector); ExECTv2 fills it with the four key-finding families plus an
 * "All families" lead (selecting one filters the inspector panels). Same shape,
 * same active look, same interaction — only the cells differ. Replaces the
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
    <div className="shrink-0 border-b border-border bg-surface px-4 py-2">
      <div className="flex items-stretch gap-1.5">
        {items.map((item) => {
          const isActive = item.id === activeId;
          const interactive = enabled && !item.disabled;
          const width = item.fixed ? "min-w-[96px]" : "min-w-[120px] flex-1";
          return (
            <button
              key={item.id}
              onClick={() => interactive && onSelect(item.id)}
              disabled={!interactive}
              className={`flex flex-col justify-center gap-0.5 rounded-md border px-3 py-1.5 text-left transition-all ${width} ${
                isActive
                  ? SOLID[item.tone]
                  : interactive
                  ? "border-border bg-surface text-foreground hover:bg-surface-raised hover:shadow-sm"
                  : "border-border/60 bg-surface-raised/50 text-muted cursor-default"
              }`}
            >
              <div className="flex items-center gap-1.5">
                {item.icon}
                <span className="text-[11px] font-semibold">{item.label}</span>
                {item.count !== undefined && (
                  <span
                    className={`ml-0.5 rounded-full px-1.5 py-0 text-[10px] font-semibold ${
                      isActive ? "bg-white/25 text-white" : "bg-surface-raised text-muted"
                    }`}
                  >
                    {item.count}
                  </span>
                )}
              </div>
              {item.sublabel !== undefined && (
                <div className={`text-[10px] leading-tight ${isActive ? "text-white/90" : "text-muted"}`}>
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
