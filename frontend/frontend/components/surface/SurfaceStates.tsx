"use client";

import type { ReactNode } from "react";
import { Eye, RotateCcw, ShieldAlert } from "lucide-react";

/** Full-height centered loading state, shared by every surface. */
export function SurfaceLoading({ message = "Loading…" }: { message?: string }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="flex h-full items-center justify-center bg-background px-6 text-muted"
    >
      <div className="w-full max-w-sm">
        <p className="text-sm font-medium text-foreground">{message}</p>
        <div className="mt-3 space-y-2" aria-hidden>
          <div className="h-2 w-full animate-pulse rounded bg-border/80" />
          <div className="h-2 w-3/4 animate-pulse rounded bg-border/60" />
        </div>
      </div>
    </div>
  );
}

/** Full-height centered error card, shared by every surface. */
export function SurfaceError({
  title = "Data failed to load",
  detail,
  onRetry,
}: {
  title?: string;
  detail?: ReactNode;
  onRetry?: () => void;
}) {
  return (
    <div
      role="alert"
      className="flex h-full items-center justify-center bg-background p-8"
    >
      <div className="max-w-md rounded-md border border-error/25 bg-error/8 p-5">
        <div className="flex items-center gap-2 text-error">
          <ShieldAlert className="h-4 w-4" />
          <p className="text-sm font-semibold">{title}</p>
        </div>
        {detail && <p className="mt-2 text-xs text-muted">{detail}</p>}
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="mt-4 inline-flex min-h-9 items-center gap-2 rounded-md border border-error/30 bg-surface px-3 py-2 text-xs font-semibold text-error transition-colors hover:bg-error/8"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            Try again
          </button>
        )}
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
      {hint && <p className="mt-1 text-xs text-muted">{hint}</p>}
    </div>
  );
}
