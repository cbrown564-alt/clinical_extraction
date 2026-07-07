"use client";

import { Mountain, AlertTriangle } from "lucide-react";
import type { RunSummary } from "@/lib/types";
import { familyLabel } from "@/lib/plainLanguageLabels";

interface GeneralisationGapProps {
  summaries: RunSummary[];
}

function fmt(n: number): string {
  return `${(n * 100).toFixed(1)}%`;
}

const TICKS = [0, 0.25, 0.5, 0.75, 1.0];

export default function GeneralisationGap({ summaries }: GeneralisationGapProps) {
  const paired = summaries.filter((s) => s.validationMetrics && s.testMetrics);

  if (paired.length === 0) {
    return (
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Mountain className="h-4 w-4 text-muted" />
          <h3 className="text-xs font-semibold uppercase tracking-widest text-muted">
            Generalisation Gap
          </h3>
        </div>
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-surface py-10 text-center">
          <AlertTriangle className="h-6 w-6 text-muted/40 mb-2" />
          <p className="text-sm font-medium text-muted">No test data available</p>
          <p className="text-[11px] text-muted mt-1 max-w-sm">
            Select runs with a <code className="rounded bg-surface-raised px-1 py-0.5 text-[10px]">validation+test</code> split
            to see the generalisation gap. Use the{" "}
            <span className="text-llm font-medium">Has test data</span> filter in the registry table.
          </p>
        </div>
      </div>
    );
  }

  // Find the widest label to keep bars aligned
  const maxLabelWidth = 160;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Mountain className="h-4 w-4 text-muted" />
        <h3 className="text-xs font-semibold uppercase tracking-widest text-muted">
          Generalisation Gap
        </h3>
        <span className="text-[10px] text-muted">
          {paired.length} run{paired.length > 1 ? "s" : ""} with test data
        </span>
      </div>

      <div className="rounded-lg border border-border bg-surface p-5">
        {/* Legend */}
        <div className="flex items-center justify-end gap-4 mb-4">
          <div className="flex items-center gap-1.5">
            <div className="h-2.5 w-2.5 rounded-sm bg-[hsl(220,60%,45%)]" />
            <span className="text-[10px] text-muted uppercase tracking-wider">Validation</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-2.5 w-2.5 rounded-sm bg-[hsl(25,75%,45%)]" />
            <span className="text-[10px] text-muted uppercase tracking-wider">Test</span>
          </div>
        </div>

        {/* Chart rows */}
        <div className="space-y-4">
          {paired.map((summary) => {
            const val = summary.validationMetrics!;
            const test = summary.testMetrics!;
            const puristGap = val.puristAccuracy - test.puristAccuracy;
            const pragmaticGap = val.pragmaticAccuracy - test.pragmaticAccuracy;
            const archFamily = familyLabel(summary.pipelineFamily);
            const variant = summary.runId
              .replace(/^gan2026_/, "")
              .replace(/_2026-.*$/, "");

            return (
              <div key={summary.runId} className="group">
                {/* Label row */}
                <div className="flex items-baseline gap-2 mb-1">
                  <span
                    className="text-[11px] font-semibold text-foreground shrink-0 truncate"
                    style={{ width: maxLabelWidth }}
                    title={variant}
                  >
                    {archFamily}
                  </span>
                  <span className="text-[10px] text-muted truncate">{variant}</span>
                  <span className="ml-auto text-[10px] font-mono text-error">
                    Δ {fmt(puristGap)}
                    <span className="text-muted ml-1">({fmt(pragmaticGap)} lenient)</span>
                  </span>
                </div>

                {/* Bars */}
                <div className="flex items-center" style={{ marginLeft: maxLabelWidth }}>
                  <div className="flex-1 relative">
                    {/* Track line */}
                    <div className="absolute left-0 right-0 top-1/2 -translate-y-1/2 h-px bg-border" />

                    {/* Validation bar */}
                    <div className="relative h-5 mb-1">
                      <div
                        className="absolute left-0 top-0 h-full rounded-sm bg-[hsl(220,60%,45%)]/80 flex items-center justify-end pr-1.5"
                        style={{ width: `${val.puristAccuracy * 100}%` }}
                      >
                        {val.puristAccuracy >= 0.18 && (
                          <span className="text-[9px] font-semibold text-white">{fmt(val.puristAccuracy)}</span>
                        )}
                      </div>
                      {val.puristAccuracy < 0.18 && (
                        <span className="absolute text-[9px] font-semibold text-[hsl(220,60%,45%)] ml-1" style={{ left: `${val.puristAccuracy * 100}%` }}>
                          {fmt(val.puristAccuracy)}
                        </span>
                      )}
                    </div>

                    {/* Test bar */}
                    <div className="relative h-5">
                      <div
                        className="absolute left-0 top-0 h-full rounded-sm bg-[hsl(25,75%,45%)]/80 flex items-center justify-end pr-1.5"
                        style={{ width: `${test.puristAccuracy * 100}%` }}
                      >
                        {test.puristAccuracy >= 0.18 && (
                          <span className="text-[9px] font-semibold text-white">{fmt(test.puristAccuracy)}</span>
                        )}
                      </div>
                      {test.puristAccuracy < 0.18 && (
                        <span className="absolute text-[9px] font-semibold text-[hsl(25,75%,45%)] ml-1" style={{ left: `${test.puristAccuracy * 100}%` }}>
                          {fmt(test.puristAccuracy)}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* X-axis */}
        <div className="flex items-center mt-4" style={{ marginLeft: maxLabelWidth }}>
          <div className="flex-1 relative">
            <div className="h-px bg-border" />
            <div className="flex justify-between mt-1">
              {TICKS.map((t) => (
                <div key={t} className="flex flex-col items-center">
                  <div className="h-1 w-px bg-border" />
                  <span className="text-[9px] font-mono text-muted mt-0.5">{fmt(t)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Axis label */}
        <div className="flex justify-center mt-1" style={{ marginLeft: maxLabelWidth }}>
          <span className="text-[9px] uppercase tracking-widest text-muted">Strict label match</span>
        </div>
      </div>
    </div>
  );
}
