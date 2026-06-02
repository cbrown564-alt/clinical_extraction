"use client";

import { Mountain, AlertTriangle } from "lucide-react";
import type { RunSummary } from "@/lib/types";

interface GeneralisationGapProps {
  summaries: RunSummary[];
}

function formatPct(n: number): string {
  return `${(n * 100).toFixed(1)}%`;
}

const FAMILY_LABELS: Record<string, string> = {
  rules_only: "Rules",
  llm_only_claim_table_selector: "LLM Claim",
  llm_heavy_clinical_frequency_reasoner: "LLM Heavy",
  llm_replacement_postprocessing_ablation: "LLM Repl",
  hybrid_rules_candidates_llm_adjudicator: "Hybrid",
  hybrid_clinical_frequency_state_graph: "Hybrid Graph",
};

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

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Mountain className="h-4 w-4 text-muted" />
        <h3 className="text-xs font-semibold uppercase tracking-widest text-muted">
          Generalisation Gap
        </h3>
        <span className="text-[10px] text-muted">
          {paired.length} run{paired.length > 1 ? "s" : ""} with test data
        </span>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {paired.map((summary) => {
          const val = summary.validationMetrics!;
          const test = summary.testMetrics!;
          const puristGap = val.puristAccuracy - test.puristAccuracy;
          const pragmaticGap = val.pragmaticAccuracy - test.pragmaticAccuracy;
          const familyLabel = FAMILY_LABELS[summary.pipelineFamily] ?? summary.pipelineFamily;

          return (
            <div key={summary.runId} className="rounded-lg border border-border bg-surface p-4">
              <div className="mb-3 flex items-center justify-between">
                <div>
                  <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
                    {familyLabel}
                  </div>
                  <div className="text-[11px] font-medium text-foreground">
                    {summary.runId.replace(/^gan2026_/, "").replace(/_2026-.*$/, "")}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-[9px] text-muted">Val rows</div>
                  <div className="text-[11px] font-mono">{val.rowCount}</div>
                  <div className="text-[9px] text-muted">Test rows</div>
                  <div className="text-[11px] font-mono">{test.rowCount}</div>
                </div>
              </div>

              {/* Purist */}
              <div className="mb-4 space-y-1.5">
                <div className="flex items-center justify-between text-[10px] text-muted">
                  <span className="font-medium text-foreground">Purist Accuracy</span>
                  <span className="rounded bg-error/10 px-1 py-0 text-[9px] font-medium text-error">
                    Gap {formatPct(puristGap)}
                  </span>
                </div>
                <div className="flex h-7 items-center gap-0">
                  <div
                    className="flex h-full items-center justify-center rounded-l bg-deterministic/15 text-[10px] font-semibold text-deterministic border-y border-l border-deterministic/25"
                    style={{ width: `${Math.min(val.puristAccuracy * 100, 45)}%` }}
                  >
                    {formatPct(val.puristAccuracy)}
                  </div>
                  <div
                    className="flex h-full items-center justify-center bg-error/10 text-[9px] font-medium text-error border-y border-error/20"
                    style={{ width: `${Math.max(puristGap * 100, 2)}%` }}
                  >
                    {puristGap > 0.03 ? formatPct(puristGap) : ""}
                  </div>
                  <div
                    className="flex h-full items-center justify-center rounded-r bg-llm/15 text-[10px] font-semibold text-llm border-y border-r border-llm/25"
                    style={{ width: `${Math.min(test.puristAccuracy * 100, 45)}%` }}
                  >
                    {formatPct(test.puristAccuracy)}
                  </div>
                </div>
                <div className="flex justify-between text-[9px] text-muted">
                  <span>Validation</span>
                  <span>Test</span>
                </div>
              </div>

              {/* Pragmatic */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-[10px] text-muted">
                  <span className="font-medium text-foreground">Pragmatic Accuracy</span>
                  <span className="rounded bg-error/10 px-1 py-0 text-[9px] font-medium text-error">
                    Gap {formatPct(pragmaticGap)}
                  </span>
                </div>
                <div className="flex h-7 items-center gap-0">
                  <div
                    className="flex h-full items-center justify-center rounded-l bg-deterministic/15 text-[10px] font-semibold text-deterministic border-y border-l border-deterministic/25"
                    style={{ width: `${Math.min(val.pragmaticAccuracy * 100, 45)}%` }}
                  >
                    {formatPct(val.pragmaticAccuracy)}
                  </div>
                  <div
                    className="flex h-full items-center justify-center bg-error/10 text-[9px] font-medium text-error border-y border-error/20"
                    style={{ width: `${Math.max(pragmaticGap * 100, 2)}%` }}
                  >
                    {pragmaticGap > 0.03 ? formatPct(pragmaticGap) : ""}
                  </div>
                  <div
                    className="flex h-full items-center justify-center rounded-r bg-llm/15 text-[10px] font-semibold text-llm border-y border-r border-llm/25"
                    style={{ width: `${Math.min(test.pragmaticAccuracy * 100, 45)}%` }}
                  >
                    {formatPct(test.pragmaticAccuracy)}
                  </div>
                </div>
                <div className="flex justify-between text-[9px] text-muted">
                  <span>Validation</span>
                  <span>Test</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
