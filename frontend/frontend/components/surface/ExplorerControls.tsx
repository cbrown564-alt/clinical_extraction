"use client";

import type { ReactNode, SelectHTMLAttributes } from "react";

/**
 * The control bar both example explorers wear directly under the header.
 *
 * Owns the one row where you pick *which specimen* and *which variant* you are
 * looking at: Gan picks a split + row and a pipeline family; ExECTv2 picks a
 * letter and an architecture. `left` carries the specimen/context pickers,
 * `right` carries the variant picker and actions, with a flexible spacer
 * between – so both datasets read as "the same bar with different selects".
 */
export function ControlBar({
  left,
  right,
}: {
  left?: ReactNode;
  right?: ReactNode;
}) {
  return (
    <div className="shrink-0 border-b border-border bg-surface">
      <div className="flex flex-wrap items-center gap-3 px-4 py-2">
        {left}
        <div className="flex-1" />
        {right}
      </div>
    </div>
  );
}

/** Inline uppercase label + control, the shared shape for every picker. */
export function ControlField({
  label,
  icon,
  htmlFor,
  children,
}: {
  label?: ReactNode;
  icon?: ReactNode;
  htmlFor?: string;
  children: ReactNode;
}) {
  return (
    <div className="flex w-full min-w-0 flex-wrap items-center gap-1.5 sm:w-auto sm:flex-nowrap">
      {icon}
      {label &&
        (htmlFor ? (
          <label htmlFor={htmlFor} className="text-[11px] font-semibold uppercase tracking-wide text-muted">
            {label}
          </label>
        ) : (
          <span className="text-[11px] font-semibold uppercase tracking-wide text-muted">{label}</span>
        ))}
      {children}
    </div>
  );
}

/** The single `<select>` styling both explorers use, so pickers never drift. */
export function ControlSelect({
  className = "",
  ...props
}: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      className={`max-w-full rounded-md border border-border bg-surface px-2 py-1 text-xs text-foreground outline-none focus:border-deterministic disabled:opacity-50 ${className}`}
      {...props}
    />
  );
}
