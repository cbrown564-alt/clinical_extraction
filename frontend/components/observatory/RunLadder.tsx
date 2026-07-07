"use client";

import { Rocket } from "lucide-react";
import type { RunSummary } from "@/lib/types";
import { LANE_META, type LaneId } from "@/lib/observatoryLanes";
import { familyLabel, splitLabel } from "@/lib/plainLanguageLabels";

interface RunLadderProps {
  summaries: RunSummary[];
}

function isSaturated(summary: RunSummary): boolean {
  const isValidation = summary.split === "validation";
  return isValidation && summary.rowCount >= 250 && summary.pragmaticAccuracy >= 0.95;
}

function formatPct(n: number): string {
  return `${(n * 100).toFixed(1)}%`;
}

function familyColorClass(family: string): string {
  if (family.includes("rules_only") || family.includes("deterministic")) {
    return "border-deterministic/25 bg-deterministic/5";
  }
  if (family.includes("hybrid")) {
    return "border-hybrid/25 bg-hybrid/5";
  }
  return "border-llm/25 bg-llm/5";
}

function familyTextClass(family: string): string {
  if (family.includes("rules_only") || family.includes("deterministic")) {
    return "text-deterministic";
  }
  if (family.includes("hybrid")) {
    return "text-hybrid";
  }
  return "text-llm";
}

export default function RunLadder({ summaries }: RunLadderProps) {
  if (summaries.length === 0) {
    return (
      <div className="flex items-center gap-2 text-muted">
        <Rocket className="h-4 w-4" />
        <span className="text-xs">Select runs to populate the ladder.</span>
      </div>
    );
  }

  // Sort: lane-tagged runs first (production → ceiling → floor), then by row
  // count ascending (smoke → signal → decision gate → full).
  const ordered = [...summaries].sort((a, b) => {
    const la = a.lane ? LANE_META[a.lane].order : Number.MAX_SAFE_INTEGER;
    const lb = b.lane ? LANE_META[b.lane].order : Number.MAX_SAFE_INTEGER;
    if (la !== lb) return la - lb;
    return a.rowCount - b.rowCount;
  });

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Rocket className="h-4 w-4 text-muted" />
        <h3 className="text-xs font-semibold uppercase tracking-widest text-muted">
          Run Ladder
        </h3>
        <span className="text-[10px] text-muted">
          {ordered.length} run{ordered.length > 1 ? "s" : ""} · sorted by size
        </span>
      </div>

      <div className="flex items-stretch gap-3 overflow-x-auto pb-2">
        {ordered.map((summary) => {
          const saturated = isSaturated(summary);
          const archFamily = familyLabel(summary.pipelineFamily);
          const lane = summary.lane ? LANE_META[summary.lane as LaneId] : null;

          return (
            <div
              key={summary.runId}
              className={`relative flex min-w-[200px] max-w-[260px] flex-1 flex-col rounded-lg border p-3 transition-all ${familyColorClass(
                summary.pipelineFamily
              )} ${saturated ? "ring-1 ring-success/30" : ""} ${lane ? lane.ringClass : ""}`}
            >
              {saturated && (
                <div className="pointer-events-none absolute inset-0 rounded-lg bg-gradient-to-br from-success/5 to-transparent" />
              )}

              <div className="relative z-10 flex flex-1 flex-col gap-2">
                {/* Top row: family + lane/saturated badge */}
                <div className="flex items-start justify-between gap-2">
                  <span className={`text-[10px] font-semibold uppercase tracking-wider ${familyTextClass(summary.pipelineFamily)}`}>
                    {archFamily}
                  </span>
                  <div className="flex shrink-0 items-center gap-1">
                    {lane && (
                      <span
                        className={`rounded border px-1.5 py-0 text-[9px] font-semibold ${lane.badgeClass} ${lane.textClass}`}
                        title={lane.title}
                      >
                        {lane.label}
                      </span>
                    )}
                    {saturated && (
                      <span
                        className="rounded bg-success/12 px-1.5 py-0 text-[9px] font-medium text-success"
                        title="Saturated surface — low information content"
                      >
                        Saturated
                      </span>
                    )}
                  </div>
                </div>

                {/* Run ID */}
                <div className="text-[11px] font-medium text-foreground leading-tight truncate">
                  {summary.runId.replace(/^gan2026_/, "").replace(/_2026-.*$/, "")}
                </div>

                {/* Meta row */}
                <div className="flex items-center gap-1.5 text-[10px] text-muted">
                  <span className="rounded bg-surface-raised px-1 py-0 border border-border">
                    {splitLabel(summary.split)}
                  </span>
                  <span>{summary.rowCount.toLocaleString()} rows</span>
                </div>

                {/* Metrics */}
                <div className="mt-auto grid grid-cols-2 gap-2">
                  <div className="rounded bg-surface p-2 border border-border">
                    <div className="text-[9px] uppercase tracking-wider text-muted">Strict</div>
                    <div className={`text-sm font-semibold ${familyTextClass(summary.pipelineFamily)}`}>
                      {formatPct(summary.puristAccuracy)}
                    </div>
                    <div className="text-[9px] text-muted">F1 {formatPct(summary.puristF1)}</div>
                  </div>
                  <div className="rounded bg-surface p-2 border border-border">
                    <div className="text-[9px] uppercase tracking-wider text-muted">Lenient</div>
                    <div className={`text-sm font-semibold ${familyTextClass(summary.pipelineFamily)}`}>
                      {formatPct(summary.pragmaticAccuracy)}
                    </div>
                    <div className="text-[9px] text-muted">F1 {formatPct(summary.pragmaticF1)}</div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
