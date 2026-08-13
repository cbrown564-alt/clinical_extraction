"use client";

import type { ReactNode } from "react";

type SurfaceVariant = "fill" | "report";

interface SurfaceLayoutProps {
  /**
   * `report` – a centered, document-style scroll column (observatory, laboratory,
   * gallery). `fill` – children own the remaining height and their own scroll
   * (workbench split panes).
   */
  variant: SurfaceVariant;
  /** Optional report title bar. Fill/workspace surfaces omit this. */
  header?: ReactNode;
  /** Max content width for the `report` variant. */
  maxWidth?: number;
  /** Extra classes for the report content container. */
  contentClassName?: string;
  children: ReactNode;
}

/**
 * The outer chrome both datasets render every surface into.
 *
 * Owns the one decision that made Gan feel like an "app" and ExECTv2 feel like a
 * "report": each surface picks a variant *once*, and both datasets honour it.
 * Workbench is `fill`; observatory / laboratory / gallery are `report`.
 */
export default function SurfaceLayout({
  variant,
  header,
  maxWidth = 1200,
  contentClassName = "",
  children,
}: SurfaceLayoutProps) {
  return (
    <div className="flex h-full min-h-0 flex-col bg-background">
      {header}
      {variant === "report" ? (
        <div className="min-h-0 flex-1 overflow-y-auto">
          <div
            className={`mx-auto w-full p-3 sm:p-5 ${contentClassName}`}
            style={{ maxWidth }}
          >
            {children}
          </div>
        </div>
      ) : (
        <div className="flex min-h-0 flex-1 flex-col">{children}</div>
      )}
    </div>
  );
}
