"use client";

import Link from "next/link";
import type { MouseEvent } from "react";
import {
  surfaceHref,
  TONE_CLASSES,
  type DatasetId,
  type DatasetTone,
  type ExplorerSurface,
  type MetricDescriptor,
} from "@/lib/datasets";
import { Blend, Bot, Braces } from "lucide-react";
import { activeMethodLabel } from "@/lib/plainLanguageLabels";
import type { ActiveMethod } from "@/lib/types";
import { SURFACE_META, SURFACE_TONE_ACTIVE } from "./meta";

// ── Method badge ─────────────────────────────────────────────────────

const METHOD_CLASSES: Record<ActiveMethod, string> = {
  llm_with_rules: "border-hybrid/25 bg-hybrid/8 text-hybrid",
  llm: "border-llm/25 bg-llm/8 text-llm",
  rules: "border-deterministic/25 bg-deterministic/8 text-deterministic",
};

export function MethodBadge({
  method,
  label,
  className = "",
}: {
  method: ActiveMethod;
  label?: string;
  className?: string;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1 shrink-0 rounded border px-1.5 py-0.5 text-[11px] font-medium ${METHOD_CLASSES[method]} ${className}`}
    >
      {method === "llm_with_rules" ? (
        <Blend className="h-3 w-3" aria-hidden="true" />
      ) : method === "llm" ? (
        <Bot className="h-3 w-3" aria-hidden="true" />
      ) : (
        <Braces className="h-3 w-3" aria-hidden="true" />
      )}
      {label ?? activeMethodLabel(method)}
    </span>
  );
}

// ── Metric formatting ────────────────────────────────────────────────

export type MetricFormat = MetricDescriptor["format"];

/** Canonical metric rendering, shared by tables, strips, and cards. */
export function formatMetricValue(
  value: number | null | undefined,
  format: MetricFormat,
  opts: { asPercent?: boolean; digits?: number } = {}
): string {
  if (typeof value !== "number" || Number.isNaN(value)) return "–";
  switch (format) {
    case "f1":
      return value.toFixed(opts.digits ?? 2);
    case "rate":
      return opts.asPercent
        ? `${(value * 100).toFixed(opts.digits ?? 1)}%`
        : value.toFixed(opts.digits ?? 2);
    case "count":
      return Math.round(value).toLocaleString();
  }
}

/** Magnitude shading for an F1/rate value so weak cells read at a glance. */
export function metricTone(value: number | null | undefined): string {
  if (typeof value !== "number") return "text-muted";
  if (value >= 0.9) return "text-success";
  if (value >= 0.8) return "text-foreground";
  return "text-error";
}

/** Right-aligned F1 table cell with magnitude shading. */
export function F1Cell({
  value,
  lead = false,
  digits = 2,
}: {
  value: number | null | undefined;
  lead?: boolean;
  digits?: number;
}) {
  return (
    <td
      className={`px-2 py-2 text-right font-mono text-xs ${metricTone(value)} ${
        lead ? "font-semibold" : ""
      }`}
    >
      {formatMetricValue(value, "f1", { digits })}
    </td>
  );
}

// ── Decision badge ───────────────────────────────────────────────────

/**
 * Maps every decision vocabulary in the app onto a tone. ExECTv2 uses
 * control/simplification/diagnostic/pending/superseded; the Gan registry uses
 * accept/reject/revise/historical. One badge speaks both.
 */
const DECISION_TONE: Record<string, DatasetTone> = {
  // ExECTv2 RunDecision
  control: "deterministic",
  method: "deterministic-alt",
  simplification: "success",
  diagnostic: "llm",
  pending: "muted",
  superseded: "error",
  // Gan registry decision
  accept: "success",
  reject: "error",
  revise: "llm",
  historical: "deterministic-alt",
};

export function DecisionBadge({
  decision,
  className = "",
}: {
  decision?: string | null;
  className?: string;
}) {
  const tone = DECISION_TONE[decision ?? ""] ?? "muted";
  return (
    <span
      className={`shrink-0 rounded border px-1.5 py-0.5 text-[11px] font-medium ${TONE_CLASSES[tone]} ${className}`}
    >
      {decision || "–"}
    </span>
  );
}

// ── Cross-surface link pill ──────────────────────────────────────────

/**
 * A standardized deep-link pill to another surface, tinted by that surface's
 * tone and carrying its icon. Replaces the ad-hoc "Aggregate / Errors / Explore"
 * links each dataset rolled by hand, so cross-surface navigation looks and reads
 * the same everywhere. Preserves the active dataset via {@link surfaceHref}.
 */
export function SurfaceLink({
  surface,
  datasetId,
  params = {},
  label,
  onClick,
}: {
  surface: ExplorerSurface;
  datasetId: DatasetId;
  params?: Record<string, string | number | undefined>;
  /** Defaults to the surface's canonical label. */
  label?: string;
  onClick?: (e: MouseEvent<HTMLAnchorElement>) => void;
}) {
  const meta = SURFACE_META[surface];
  const Icon = meta.Icon;
  return (
    <Link
      href={surfaceHref(surface, datasetId, params)}
      onClick={onClick}
      className={`inline-flex items-center gap-1 rounded border px-2 py-1 text-[11px] font-medium transition-colors ${SURFACE_TONE_ACTIVE[meta.tone]} hover:brightness-95`}
    >
      <Icon className="h-3 w-3" />
      {label ?? meta.label}
    </Link>
  );
}
