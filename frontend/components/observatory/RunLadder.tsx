"use client";

import { Rocket } from "lucide-react";
import type { RunSummary } from "@/lib/types";

interface RunLadderProps {
  summaries: RunSummary[];
}

function isSaturated(summary: RunSummary): boolean {
  // Validation surfaces with > 250 rows and near-ceiling pragmatic accuracy
  const isValidation = summary.split.includes("validation") && !summary.split.includes("test");
  return isValidation && summary.rowCount >= 250 && summary.pragmaticAccuracy >= 0.95;
}

function formatPct(n: number): string {
  return `${(n * 100).toFixed(1)}%`;
}

function familyColorClass(family: string): string {
  if (family.includes("rules_only") || family.includes("deterministic")) {
    return "border-deterministic/30 bg-deterministic/5";
  }
  if (family.includes("hybrid")) {
    return "border-hybrid/30 bg-hybrid/5";
  }
  return "border-llm/30 bg-llm/5";
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
        <span className="text-xs">Select runs above to populate the ladder.</span>
      </div>
    );
  }

  // Sort by row count ascending (smoke → signal → decision gate → full)
  const ordered = [...summaries].sort((a, b) => a.rowCount - b.rowCount);

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Rocket className="h-4 w-4 text-muted" />
        <h3 className="text-xs font-semibold uppercase tracking-widest text-muted">
          Run Ladder
        </h3>
      </div>

      <div className="flex items-stretch gap-3 overflow-x-auto pb-2">
        {ordered.map((summary) => {
          const saturated = isSaturated(summary);
          return (
            <div
              key={summary.runId}
              className={`relative flex min-w-[220px] flex-col rounded-lg border p-3 transition-all ${familyColorClass(
                summary.pipelineFamily
              )} ${saturated ? "shadow-sm" : ""}`}
            >
              {saturated && (
                <div className="pointer-events-none absolute inset-0 rounded-lg bg-gradient-to-br from-success/5 to-transparent" />
              )}

              <div className="relative z-10 space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
                      {summary.pipelineFamily.replace(/_/g, " ")}
                    </div>
                    <div className="text-[11px] font-medium text-foreground leading-tight">
                      {summary.runId.length > 35
                        ? summary.runId.slice(0, 35) + "…"
                        : summary.runId}
                    </div>
                  </div>
                  {saturated && (
                    <span
                      className="shrink-0 rounded-full bg-success/15 px-1.5 py-0.5 text-[9px] font-medium text-success"
                      title="Saturated surface — low information content"
                    >
                      Saturated
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2 text-[10px] text-muted">
                  <span className="rounded bg-surface-raised px-1 py-0.5 border border-border">
                    {summary.split}
                  </span>
                  <span>{summary.rowCount} rows</span>
                  <span className="rounded bg-surface-raised px-1 py-0.5 border border-border capitalize">
                    {summary.decision}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div className="rounded bg-surface p-2 border border-border">
                    <div className="text-[9px] uppercase tracking-wider text-muted">Purist</div>
                    <div className={`text-sm font-semibold ${familyTextClass(summary.pipelineFamily)}`}>
                      {formatPct(summary.puristAccuracy)}
                    </div>
                    <div className="text-[9px] text-muted">F1 {formatPct(summary.puristF1)}</div>
                  </div>
                  <div className="rounded bg-surface p-2 border border-border">
                    <div className="text-[9px] uppercase tracking-wider text-muted">Pragmatic</div>
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
