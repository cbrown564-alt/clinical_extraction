"use client";

import Link from "next/link";
import { ArrowLeft, RotateCcw, ShieldAlert } from "lucide-react";

export default function AppError({
  error,
  unstable_retry,
}: {
  error: Error & { digest?: string };
  unstable_retry: () => void;
}) {
  return (
    <section
      role="alert"
      aria-labelledby="app-error-title"
      className="flex h-full items-center justify-center bg-background px-6 py-10"
    >
      <div className="w-full max-w-lg rounded-lg border border-error/25 bg-surface p-6">
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-error/10 text-error">
            <ShieldAlert className="h-4.5 w-4.5" />
          </div>
          <div>
            <h1 id="app-error-title" className="text-lg font-semibold text-foreground">
              This surface could not load
            </h1>
            <p className="mt-1 max-w-[65ch] text-sm leading-relaxed text-muted">
              Your current route and dataset are unchanged. Retry the surface, or return to the
              Example Explorer without losing saved review decisions.
            </p>
          </div>
        </div>

        <div className="mt-5 flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => unstable_retry()}
            className="inline-flex min-h-10 items-center gap-2 rounded-md bg-deterministic px-3.5 py-2 text-sm font-semibold text-surface transition-colors hover:bg-deterministic/90"
          >
            <RotateCcw className="h-4 w-4" />
            Try again
          </button>
          <Link
            href="/workbench"
            className="inline-flex min-h-10 items-center gap-2 rounded-md border border-border bg-surface px-3.5 py-2 text-sm font-semibold text-foreground transition-colors hover:bg-surface-raised"
          >
            <ArrowLeft className="h-4 w-4" />
            Example Explorer
          </Link>
        </div>

        {error.digest && (
          <p className="mt-5 font-mono text-[11px] text-muted">Reference {error.digest}</p>
        )}
      </div>
    </section>
  );
}
