"use client";

import type { ReactNode } from "react";

/**
 * The two-pane body both example explorers share.
 *
 * Left is the source document (clinical note / letter) under a thin meta bar;
 * right is the inspector (Gan's stage detail / ExECTv2's family panels). The
 * split proportion, the meta bar, the borders, and the independent scroll
 * regions are owned here so the two datasets stop diverging on layout — only
 * the contents of each pane differ.
 */
export default function ExplorerBody({
  sourceLabel = "Source",
  sourceMeta,
  source,
  inspector,
  /** Width of the source pane; the inspector takes the rest. */
  sourceWidth = "55%",
}: {
  sourceLabel?: ReactNode;
  sourceMeta?: ReactNode;
  source: ReactNode;
  inspector: ReactNode;
  sourceWidth?: string;
}) {
  return (
    <div className="flex min-h-0 flex-1 overflow-hidden">
      {/* Left — source document */}
      <div className="flex min-w-0 flex-col border-r border-border" style={{ width: sourceWidth }}>
        <div className="flex items-center justify-between border-b border-border bg-surface-raised/50 px-4 py-1.5">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-muted">
            {sourceLabel}
          </span>
          {sourceMeta}
        </div>
        <div className="flex-1 overflow-y-auto p-6">{source}</div>
      </div>

      {/* Right — inspector */}
      <div className="flex min-h-0 min-w-0 flex-1 flex-col bg-surface">{inspector}</div>
    </div>
  );
}
