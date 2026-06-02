"use client";

import { Mountain } from "lucide-react";
import type { RunSummary } from "@/lib/types";

interface GeneralisationGapProps {
  summaries: RunSummary[];
}

function formatPct(n: number): string {
  return `${(n * 100).toFixed(1)}%`;
}

export default function GeneralisationGap({ summaries }: GeneralisationGapProps) {
  // Only show runs that have both validation and test metrics
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
        <div className="rounded-lg border border-border bg-surface p-4 text-center text-xs text-muted">
          No selected runs contain both validation and test data.
          <br />
          Select a run with <code className="rounded bg-surface-raised px-1 py-0.5 text-[10px]">validation+test</code> split to visualise the gap.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Mountain className="h-4 w-4 text-muted" />
        <h3 className="text-xs font-semibold uppercase tracking-widest text-muted">
          Generalisation Gap
        </h3>
      </div>

      <div className="space-y-4">
        {paired.map((summary) => {
          const val = summary.validationMetrics!;
          const test = summary.testMetrics!;
          const puristGap = val.puristAccuracy - test.puristAccuracy;
          const pragmaticGap = val.pragmaticAccuracy - test.pragmaticAccuracy;

          return (
            <div key={summary.runId} className="rounded-lg border border-border bg-surface p-4">
              <div className="mb-3 text-[11px] font-medium text-foreground">
                {summary.runId}
              </div>

              {/* Purist gap */}
              <div className="mb-4 space-y-1.5">
                <div className="flex items-center justify-between text-[10px] text-muted">
                  <span>Purist Accuracy</span>
                  <span className="text-error">Gap: {formatPct(puristGap)}</span>
                </div>
                <div className="flex h-8 items-center gap-1">
                  {/* Validation cliff */}
                  <div className="flex h-full flex-col justify-end" style={{ width: `${val.puristAccuracy * 100}%`, maxWidth: "45%" }}>
                    <div className="flex items-center justify-center rounded-l bg-deterministic/20 text-[10px] font-semibold text-deterministic h-full border border-deterministic/30">
                      Val {formatPct(val.puristAccuracy)}
                    </div>
                  </div>
                  {/* Gap */}
                  <div
                    className="flex h-full items-center justify-center bg-error/10 text-[9px] text-error border-y border-error/20"
                    style={{ width: `${puristGap * 100}%`, minWidth: "24px" }}
                  >
                    {formatPct(puristGap)}
                  </div>
                  {/* Test cliff */}
                  <div className="flex h-full flex-col justify-end" style={{ width: `${test.puristAccuracy * 100}%`, maxWidth: "45%" }}>
                    <div className="flex items-center justify-center rounded-r bg-llm/20 text-[10px] font-semibold text-llm h-full border border-llm/30">
                      Test {formatPct(test.puristAccuracy)}
                    </div>
                  </div>
                </div>
              </div>

              {/* Pragmatic gap */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-[10px] text-muted">
                  <span>Pragmatic Accuracy</span>
                  <span className="text-error">Gap: {formatPct(pragmaticGap)}</span>
                </div>
                <div className="flex h-8 items-center gap-1">
                  <div className="flex h-full flex-col justify-end" style={{ width: `${val.pragmaticAccuracy * 100}%`, maxWidth: "45%" }}>
                    <div className="flex items-center justify-center rounded-l bg-deterministic/20 text-[10px] font-semibold text-deterministic h-full border border-deterministic/30">
                      Val {formatPct(val.pragmaticAccuracy)}
                    </div>
                  </div>
                  <div
                    className="flex h-full items-center justify-center bg-error/10 text-[9px] text-error border-y border-error/20"
                    style={{ width: `${pragmaticGap * 100}%`, minWidth: "24px" }}
                  >
                    {formatPct(pragmaticGap)}
                  </div>
                  <div className="flex h-full flex-col justify-end" style={{ width: `${test.pragmaticAccuracy * 100}%`, maxWidth: "45%" }}>
                    <div className="flex items-center justify-center rounded-r bg-llm/20 text-[10px] font-semibold text-llm h-full border border-llm/30">
                      Test {formatPct(test.pragmaticAccuracy)}
                    </div>
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
