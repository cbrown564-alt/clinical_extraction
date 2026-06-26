"use client";

import { useMemo, useState } from "react";
import { ArrowRight, ChevronDown, ChevronUp } from "lucide-react";
import type { RunSummary } from "@/lib/types";
import {
  type EnrichedRow,
  type ErrorFilter,
  type ComparisonResult,
  ERROR_TYPE_LABELS,
  CATEGORY_SHORT_NAMES,
  severityDotClass,
  severityRowClass,
  enrichRow,
} from "@/lib/gallery-utils";
import { ERROR_TYPE_DESCRIPTIONS, ERROR_TYPE_ORDER } from "./galleryConstants";
import { ErrorTypeIcon, ComparisonIcon, EmptyState } from "./GalleryShared";
import { ErrorDetail } from "./ErrorDetail";

const ROW_LIMIT = 100;

export function SemanticErrorGroups({
  rows,
  compareSummary,
  expandedRowKey,
  onToggleRow,
  activeFilter,
}: {
  rows: EnrichedRow[];
  compareSummary: RunSummary | null;
  expandedRowKey: string | null;
  onToggleRow: (key: string) => void;
  activeFilter: ErrorFilter;
}) {
  const grouped = useMemo(() => {
    const map = new Map<EnrichedRow["errorType"], EnrichedRow[]>();
    for (const type of ERROR_TYPE_ORDER) {
      map.set(type, []);
    }
    for (const row of rows) {
      map.get(row.errorType)?.push(row);
    }
    return map;
  }, [rows]);

  const [collapsedGroups, setCollapsedGroups] = useState<Set<EnrichedRow["errorType"]>>(
    () => new Set(["correct", "near_miss"])
  );
  const [loadedAllGroups, setLoadedAllGroups] = useState<Set<EnrichedRow["errorType"]>>(new Set());

  const toggleGroup = (type: EnrichedRow["errorType"]) => {
    setCollapsedGroups((prev) => {
      const next = new Set(prev);
      if (next.has(type)) next.delete(type);
      else next.add(type);
      return next;
    });
  };

  const loadMore = (type: EnrichedRow["errorType"]) => {
    setLoadedAllGroups((prev) => {
      const next = new Set(prev);
      next.add(type);
      return next;
    });
  };

  const visibleTypes = ERROR_TYPE_ORDER.filter((type) => {
    const groupRows = grouped.get(type) ?? [];
    if (groupRows.length === 0) return false;
    if (activeFilter !== "all_errors" && activeFilter !== "all_rows" && activeFilter !== type) return false;
    return true;
  });

  if (visibleTypes.length === 0) {
    return <EmptyState message="No rows match the current filters." />;
  }

  return (
    <div className="space-y-4">
      {visibleTypes.map((type) => {
        const groupRows = grouped.get(type) ?? [];
        const isCollapsed = collapsedGroups.has(type);
        const avgSeverity =
          groupRows.length > 0
            ? groupRows.reduce((sum, r) => sum + r.severity, 0) / groupRows.length
            : 0;

        return (
          <div
            key={type}
            className={`rounded-lg border transition-colors ${
              type === "correct"
                ? "border-border/50 bg-surface"
                : "border-error/15 bg-error/[0.02]"
            }`}
          >
            <button
              onClick={() => toggleGroup(type)}
              className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-surface-raised/30 transition-colors"
            >
              <ErrorTypeIcon type={type} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-foreground">
                    {ERROR_TYPE_LABELS[type]}
                  </span>
                  <span className="rounded bg-surface-raised px-1.5 py-0 text-[10px] font-medium text-muted border border-border">
                    {groupRows.length}
                  </span>
                  {type !== "correct" && avgSeverity > 0 && (
                    <span className="text-[10px] text-error/70">
                      avg severity {(avgSeverity).toFixed(1)}
                    </span>
                  )}
                </div>
                <p className="text-[10px] text-muted mt-0.5 leading-relaxed">
                  {ERROR_TYPE_DESCRIPTIONS[type]}
                </p>
              </div>
              {isCollapsed ? (
                <ChevronDown className="h-4 w-4 text-muted shrink-0" />
              ) : (
                <ChevronUp className="h-4 w-4 text-muted shrink-0" />
              )}
            </button>

            {!isCollapsed && (
              <div className="px-2 pb-2">
                <div className="grid grid-cols-[28px_1fr_120px_80px_28px] items-center gap-2 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted/60 border-b border-border/30">
                  <div />
                  <div>Label Transition</div>
                  <div>Category</div>
                  <div>Run</div>
                  <div />
                </div>

                <div className="space-y-0.5 mt-1">
                  {(() => {
                    const showAll = loadedAllGroups.has(type);
                    const visibleRows = showAll ? groupRows : groupRows.slice(0, ROW_LIMIT);
                    return (
                      <>
                        {visibleRows.map((row) => {
                          const rowKey = `${row.runId}-${row.sourceRowIndex}`;
                          const isExpanded = expandedRowKey === rowKey;

                          let compareRow: EnrichedRow | null = null;
                          let compareStatus: ComparisonResult["status"] = "no_compare";
                          if (compareSummary && compareSummary.rows && row.sourceRowIndex < compareSummary.rows.length) {
                            const cr = compareSummary.rows[row.sourceRowIndex];
                            compareRow = enrichRow({
                              ...cr,
                              runId: compareSummary.runId,
                              pipelineFamily: compareSummary.pipelineFamily,
                              sourceRowIndex: row.sourceRowIndex,
                            });
                            if (!row.puristCorrect && compareRow.puristCorrect) compareStatus = "fix";
                            else if (row.puristCorrect && !compareRow.puristCorrect) compareStatus = "regression";
                            else if (!row.puristCorrect && !compareRow.puristCorrect) compareStatus = "both_wrong";
                            else compareStatus = "both_right";
                          }

                          return (
                            <div
                              key={rowKey}
                              className={`rounded-md border transition-colors ${severityRowClass(
                                row.severityLevel
                              )}`}
                            >
                              <button
                                onClick={() => onToggleRow(rowKey)}
                                className="w-full grid grid-cols-[28px_1fr_120px_80px_28px] items-center gap-2 px-3 py-2 text-left hover:bg-surface-raised/50 transition-colors"
                              >
                                <div className="flex items-center justify-center">
                                  {row.errorType !== "correct" && (
                                    <div
                                      className={`rounded-full ${severityDotClass(row.severityLevel)}`}
                                      style={{
                                        width:
                                          row.severityLevel === "severe"
                                            ? 10
                                            : row.severityLevel === "significant"
                                            ? 8
                                            : 6,
                                        height:
                                          row.severityLevel === "severe"
                                            ? 10
                                            : row.severityLevel === "significant"
                                            ? 8
                                            : 6,
                                      }}
                                      title={`Severity: ${row.severityLevel}`}
                                    />
                                  )}
                                </div>

                                <div className="flex items-center gap-1.5 text-[11px] min-w-0">
                                  <span
                                    className="text-muted truncate"
                                    title={`Gold: ${row.goldLabel}`}
                                  >
                                    {row.goldLabel}
                                  </span>
                                  <ArrowRight className="h-3 w-3 text-muted shrink-0" />
                                  <span
                                    className={`font-mono truncate font-medium ${
                                      row.puristCorrect ? "text-foreground" : "text-error"
                                    }`}
                                    title={`Predicted: ${row.predictedLabel}`}
                                  >
                                    {row.predictedLabel}
                                  </span>
                                  {compareRow && (
                                    <span className="flex items-center gap-1 ml-1 shrink-0">
                                      <ComparisonIcon status={compareStatus} />
                                      <span
                                        className={`font-mono text-[10px] ${
                                          compareRow.puristCorrect ? "text-success" : "text-error"
                                        }`}
                                      >
                                        {compareRow.predictedLabel}
                                      </span>
                                    </span>
                                  )}
                                </div>

                                <div className="flex items-center gap-1 text-[10px]">
                                  <span className="text-muted truncate">
                                    {CATEGORY_SHORT_NAMES[row.goldCategory] ?? row.goldCategory}
                                  </span>
                                  <ArrowRight className="h-2.5 w-2.5 text-muted shrink-0" />
                                  <span
                                    className={`truncate ${
                                      row.puristCorrect ? "text-success" : "text-error"
                                    }`}
                                  >
                                    {CATEGORY_SHORT_NAMES[row.predictedCategory] ?? row.predictedCategory}
                                  </span>
                                </div>

                                <div className="truncate">
                                  <span
                                    className="rounded bg-surface-raised px-1.5 py-0 text-[9px] font-mono text-muted border border-border truncate"
                                    title={row.runId}
                                  >
                                    {row.runId.slice(0, 12)}
                                    {row.runId.length > 12 ? "…" : ""}
                                  </span>
                                </div>

                                <div className="flex items-center justify-center">
                                  {isExpanded ? (
                                    <ChevronUp className="h-3.5 w-3.5 text-muted" />
                                  ) : (
                                    <ChevronDown className="h-3.5 w-3.5 text-muted" />
                                  )}
                                </div>
                              </button>

                              {isExpanded && (
                                <ErrorDetail
                                  row={row}
                                  compareRow={compareRow}
                                  compareStatus={compareStatus}
                                  compareRunId={compareSummary?.runId ?? null}
                                />
                              )}
                            </div>
                          );
                        })}
                        {!showAll && groupRows.length > ROW_LIMIT && (
                          <button
                            onClick={() => loadMore(type)}
                            className="w-full rounded-md border border-dashed border-border bg-surface-raised/50 py-2 text-[11px] font-medium text-muted hover:text-foreground hover:bg-surface-raised transition-colors mt-1"
                          >
                            Load {groupRows.length - ROW_LIMIT} more…
                            <span className="text-muted ml-1">
                              (showing {ROW_LIMIT} of {groupRows.length})
                            </span>
                          </button>
                        )}
                      </>
                    );
                  })()}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
