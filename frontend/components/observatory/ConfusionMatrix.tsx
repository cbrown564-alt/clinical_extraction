"use client";

import { useState } from "react";
import { Grid3X3, X } from "lucide-react";
import type { RunSummary, RowScore } from "@/lib/types";

interface ConfusionMatrixProps {
  summaries: RunSummary[];
}

const CATEGORY_ORDER = [
  "currently_no_seizure",
  "seizure_freq_unknown",
  "seizure_freq_1_per_yr",
  "seizure_freq_1_per_6mon",
  "seizure_freq_more1per6mon_less1mon",
  "seizure_freq_1_per_mon",
  "seizure_freq_more1mon_less1week",
  "seizure_freq_1_per_week",
  "seizure_freq_more1week_less1day",
  "seizure_freq_1ormore_daily",
  "seizure_infrequent",
  "seizure_frequent",
];

const CATEGORY_LABELS: Record<string, string> = {
  currently_no_seizure: "No seizure",
  seizure_freq_unknown: "Unknown",
  seizure_freq_1_per_yr: "1/yr",
  seizure_freq_1_per_6mon: "1/6mo",
  seizure_freq_more1per6mon_less1mon: "1/6–1/mo",
  seizure_freq_1_per_mon: "1/mo",
  seizure_freq_more1mon_less1week: "1/mo–1/wk",
  seizure_freq_1_per_week: "1/wk",
  seizure_freq_more1week_less1day: "1/wk–1/d",
  seizure_freq_1ormore_daily: "≥1/d",
  seizure_infrequent: "Infreq",
  seizure_frequent: "Freq",
};

function getPresentCategories(summaries: RunSummary[]): string[] {
  const present = new Set<string>();
  for (const s of summaries) {
    for (const row of s.rows) {
      present.add(row.goldCategory);
      present.add(row.predictedCategory);
    }
  }
  return CATEGORY_ORDER.filter((c) => present.has(c));
}

function maxCount(matrix: Map<string, Map<string, number>>, categories: string[]): number {
  let max = 0;
  for (const gold of categories) {
    const row = matrix.get(gold);
    if (!row) continue;
    for (const pred of categories) {
      max = Math.max(max, row.get(pred) ?? 0);
    }
  }
  return max;
}

function cellColor(count: number, max: number, isDiagonal: boolean): string {
  if (count === 0) return "bg-surface-raised";
  const intensity = Math.min(1, count / Math.max(1, max));
  if (isDiagonal) {
    // Green gradient for correct predictions
    const alpha = 0.08 + intensity * 0.72;
    return `bg-success/15`;
  }
  // Red gradient for errors
  return `bg-error/15`;
}

function cellIntensity(count: number, max: number): string {
  if (count === 0) return "";
  const intensity = Math.min(1, count / Math.max(1, max));
  return `opacity-${Math.max(20, Math.round(intensity * 100))}`;
}

function computeMergedMatrix(summaries: RunSummary[]): Map<string, Map<string, number>> {
  const merged = new Map<string, Map<string, number>>();
  for (const cat of CATEGORY_ORDER) {
    merged.set(cat, new Map<string, number>());
  }
  for (const summary of summaries) {
    for (const [gold, predMap] of summary.confusionMatrix.entries()) {
      const mergedRow = merged.get(gold) ?? new Map<string, number>();
      for (const [pred, count] of predMap.entries()) {
        mergedRow.set(pred, (mergedRow.get(pred) ?? 0) + count);
      }
      merged.set(gold, mergedRow);
    }
  }
  return merged;
}

function findRowsForCell(summaries: RunSummary[], gold: string, predicted: string): Array<{ runId: string; label: string; goldLabel: string }> {
  const results: Array<{ runId: string; label: string; goldLabel: string }> = [];
  for (const summary of summaries) {
    for (const row of summary.rows) {
      if (row.goldCategory === gold && row.predictedCategory === predicted) {
        results.push({
          runId: summary.runId,
          label: row.predictedLabel,
          goldLabel: row.goldLabel,
        });
      }
    }
  }
  return results;
}

export default function ConfusionMatrix({ summaries }: ConfusionMatrixProps) {
  const [selectedCell, setSelectedCell] = useState<{ gold: string; predicted: string } | null>(null);

  if (summaries.length === 0) {
    return (
      <div className="flex items-center gap-2 text-muted">
        <Grid3X3 className="h-4 w-4" />
        <span className="text-xs">Select runs to view confusion matrices.</span>
      </div>
    );
  }

  const categories = getPresentCategories(summaries);
  const mergedMatrix = computeMergedMatrix(summaries);
  const max = maxCount(mergedMatrix, categories);

  const cellRows = selectedCell
    ? findRowsForCell(summaries, selectedCell.gold, selectedCell.predicted)
    : [];

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Grid3X3 className="h-4 w-4 text-muted" />
        <h3 className="text-xs font-semibold uppercase tracking-widest text-muted">
          Confusion Matrix
        </h3>
        <span className="text-[10px] text-muted">
          Merged across {summaries.length} run{summaries.length > 1 ? "s" : ""}
        </span>
      </div>

      <div className="flex gap-4">
        {/* Matrix */}
        <div className="overflow-auto">
          <div className="min-w-max">
            {/* Header row */}
            <div className="flex">
              <div className="w-20 shrink-0" />
              {categories.map((cat) => (
                <div
                  key={cat}
                  className="flex w-14 items-center justify-center py-1 text-[9px] font-medium text-muted"
                >
                  <span className="rotate-0 text-center leading-tight">
                    {CATEGORY_LABELS[cat] ?? cat}
                  </span>
                </div>
              ))}
            </div>

            {/* Rows */}
            {categories.map((gold) => (
              <div key={gold} className="flex items-center">
                <div className="w-20 shrink-0 pr-2 text-right text-[9px] font-medium text-muted">
                  {CATEGORY_LABELS[gold] ?? gold}
                </div>
                {categories.map((predicted) => {
                  const count = mergedMatrix.get(gold)?.get(predicted) ?? 0;
                  const isDiagonal = gold === predicted;
                  const selected =
                    selectedCell?.gold === gold && selectedCell?.predicted === predicted;

                  return (
                    <button
                      key={predicted}
                      onClick={() => {
                        if (count === 0) {
                          setSelectedCell(null);
                          return;
                        }
                        setSelectedCell({ gold, predicted });
                      }}
                      className={`relative m-0.5 flex h-10 w-14 items-center justify-center rounded border text-[10px] font-medium transition-all ${
                        count > 0
                          ? isDiagonal
                            ? "border-success/40 text-success hover:border-success"
                            : "border-error/40 text-error hover:border-error"
                          : "border-border text-muted"
                      } ${selected ? "ring-2 ring-hybrid" : ""}`}
                      style={{
                        backgroundColor:
                          count > 0
                            ? isDiagonal
                              ? `rgba(129, 178, 154, ${0.08 + (count / Math.max(1, max)) * 0.42})`
                              : `rgba(224, 122, 95, ${0.08 + (count / Math.max(1, max)) * 0.42})`
                            : undefined,
                      }}
                    >
                      {count > 0 ? count : ""}
                    </button>
                  );
                })}
              </div>
            ))}
          </div>
        </div>

        {/* Cell detail panel */}
        {selectedCell && (
          <div className="flex w-64 shrink-0 flex-col rounded-lg border border-border bg-surface p-3">
            <div className="mb-2 flex items-center justify-between">
              <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
                Cell Detail
              </div>
              <button
                onClick={() => setSelectedCell(null)}
                className="rounded p-0.5 text-muted hover:bg-surface-raised"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
            <div className="mb-2 text-[11px]">
              <span className="text-muted">Gold:</span>{" "}
              <span className="font-medium">{CATEGORY_LABELS[selectedCell.gold] ?? selectedCell.gold}</span>
              <br />
              <span className="text-muted">Predicted:</span>{" "}
              <span className="font-medium">{CATEGORY_LABELS[selectedCell.predicted] ?? selectedCell.predicted}</span>
              <br />
              <span className="text-muted">Count:</span>{" "}
              <span className="font-medium">{cellRows.length}</span>
            </div>
            <div className="flex-1 overflow-y-auto space-y-1">
              {cellRows.slice(0, 50).map((row, i) => (
                <div
                  key={i}
                  className="rounded border border-border bg-surface-raised p-1.5 text-[10px]"
                >
                  <div className="truncate text-muted">{row.runId.slice(0, 30)}…</div>
                  <div className="flex gap-1">
                    <span className="text-error">{row.label}</span>
                    <span className="text-muted">→</span>
                    <span className="text-success">{row.goldLabel}</span>
                  </div>
                </div>
              ))}
              {cellRows.length > 50 && (
                <div className="text-center text-[9px] text-muted">
                  + {cellRows.length - 50} more
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
