"use client";

import type { ReactNode } from "react";
import type { DatasetDescriptor, ExplorerSurface } from "@/lib/datasets";
import { SURFACE_META, SURFACE_TONE_ICON } from "./meta";

interface SurfaceHeaderProps {
  surface: ExplorerSurface;
  dataset: DatasetDescriptor;
  /** Right-aligned slot for context badges and actions. */
  right?: ReactNode;
}

/**
 * Single-line title bar for report surfaces (runs, components, galleries).
 * Workspace/fill surfaces omit this header so the source document owns the height.
 */
export default function SurfaceHeader({
  surface,
  dataset,
  right,
}: SurfaceHeaderProps) {
  const meta = SURFACE_META[surface];
  const Icon = meta.Icon;

  return (
    <header className="shrink-0 border-b border-border bg-surface px-3 py-1.5 sm:px-5">
      <div className="flex min-h-7 flex-wrap items-center justify-between gap-2">
        <div className="flex min-w-0 items-center gap-2">
          <div
            className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-md ${SURFACE_TONE_ICON[meta.tone]}`}
          >
            <Icon className="h-3.5 w-3.5" />
          </div>
          <h1 className="truncate text-sm font-semibold text-foreground">
            <span className="text-muted">{dataset.label}</span>
            <span className="mx-1.5 text-muted/50">·</span>
            {meta.label}
          </h1>
        </div>
        {right && <div className="flex flex-wrap items-center gap-2">{right}</div>}
      </div>
    </header>
  );
}
