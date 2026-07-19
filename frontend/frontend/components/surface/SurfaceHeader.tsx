"use client";

import type { ReactNode } from "react";
import type { DatasetDescriptor, ExplorerSurface } from "@/lib/datasets";
import { SURFACE_META, SURFACE_TONE_ICON } from "./meta";

interface SurfaceHeaderProps {
  surface: ExplorerSurface;
  dataset: DatasetDescriptor;
  /** One-line, dataset-specific description of what this surface shows. */
  description?: ReactNode;
  /** Right-aligned slot for context badges and cross-surface links. */
  right?: ReactNode;
}

/**
 * The shared title bar every surface wears, for both datasets.
 *
 * Renders a tinted surface icon, a `"<Dataset> · <Surface>"` title, and an
 * optional description, with a right-hand slot for badges/links. This is the
 * single biggest lever for making Gan and ExECTv2 feel like one product:
 * switching datasets changes the words and the right-hand context, never the
 * shape of the page.
 */
export default function SurfaceHeader({
  surface,
  dataset,
  description,
  right,
}: SurfaceHeaderProps) {
  const meta = SURFACE_META[surface];
  const Icon = meta.Icon;

  return (
    <header className="shrink-0 border-b border-border bg-surface px-3 py-3 sm:px-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-3">
          <div
            className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-md ${SURFACE_TONE_ICON[meta.tone]}`}
          >
            <Icon className="h-4 w-4" />
          </div>
          <div className="min-w-0">
            <h1 className="truncate text-sm font-semibold text-foreground">
              <span className="text-muted">{dataset.label}</span>
              <span className="mx-1.5 text-muted/50">·</span>
              {meta.label}
            </h1>
            {description && (
              <p className="mt-0.5 line-clamp-2 text-xs leading-snug text-muted">
                {description}
              </p>
            )}
          </div>
        </div>
        {right && <div className="flex flex-wrap items-center gap-2">{right}</div>}
      </div>
    </header>
  );
}
