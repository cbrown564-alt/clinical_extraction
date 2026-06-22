"use client";

import type { ReactNode } from "react";
import { Eye, Loader2, ShieldAlert } from "lucide-react";

/** Full-height centered loading state, shared by every surface. */
export function SurfaceLoading({ message = "Loading…" }: { message?: string }) {
  return (
    <div className="flex h-full items-center justify-center bg-background text-muted">
      <div className="flex items-center gap-2">
        <Loader2 className="h-4 w-4 animate-spin" />
        <p className="text-sm font-medium">{message}</p>
      </div>
    </div>
  );
}

/** Full-height centered error card, shared by every surface. */
export function SurfaceError({
  title = "Data failed to load",
  detail,
}: {
  title?: string;
  detail?: ReactNode;
}) {
  return (
    <div className="flex h-full items-center justify-center bg-background p-8">
      <div className="max-w-md rounded-md border border-error/25 bg-error/8 p-5">
        <div className="flex items-center gap-2 text-error">
          <ShieldAlert className="h-4 w-4" />
          <p className="text-sm font-semibold">{title}</p>
        </div>
        {detail && <p className="mt-2 text-xs text-muted">{detail}</p>}
      </div>
    </div>
  );
}

/**
 * Inline empty state for "nothing matches" / "nothing selected" regions.
 * Use inside a surface body rather than as a full-height takeover.
 */
export function SurfaceEmpty({
  message,
  hint,
  icon,
}: {
  message: string;
  hint?: ReactNode;
  icon?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-surface py-12 text-center">
      <div className="mb-3 text-muted/40">{icon ?? <Eye className="h-8 w-8" />}</div>
      <p className="text-sm font-medium text-muted">{message}</p>
      {hint && <p className="mt-1 text-[11px] text-muted">{hint}</p>}
    </div>
  );
}
