"use client";

import { Suspense, useState, useMemo } from "react";
import {
  Filter,
  Eye,
  ArrowRight,
  CheckCircle,
  XCircle,
  ChevronDown,
  ChevronUp,
  GitCompare,
  ArrowUpCircle,
  ArrowDownCircle,
  MinusCircle,
  AlertTriangle,
  AlertCircle,
  TrendingUp,
  TrendingDown,
  Target,
  BarChart3,
  Activity,
  Layers,
  BrainCircuit,
  Zap,
  ExternalLink,
} from "lucide-react";
import Link from "next/link";
import { useObservatoryData } from "@/components/observatory/useObservatoryData";
import { useGalleryUrlSync } from "@/lib/hooks";
import type { RowScore, RunSummary } from "@/lib/types";
import {
  type EnrichedRow,
  type ErrorFilter,
  type SortKey,
  type ComparisonResult,
  type ErrorSummary,
  type ConfusedPair,
  type FamilyBreakdown,
  ERROR_TYPE_LABELS,
  ERROR_TYPE_COLORS,
  CATEGORY_SHORT_NAMES,
  CATEGORY_DISPLAY_NAMES,
  severityDotClass,
  severityRowClass,
  enrichRow,
  filterRows,
  sortRows,
  computeSummary,
  getTopConfusedPairs,
  getFamilyBreakdown,
  getSeverityDistribution,
  getDominantErrorType,
  familyColorClass,
  comparisonStatusLabel,
  comparisonStatusColor,
} from "@/lib/gallery-utils";

// ── Clinical descriptions for error types ────────────────────────────

const ERROR_TYPE_DESCRIPTIONS: Record<EnrichedRow["errorType"], string> = {
  correct: "Predictions that exactly match the gold standard.",
  false_negative:
    "The model predicted 'no seizure' or 'unknown' when the clinical note actually describes a seizure frequency. These are the most clinically dangerous misses.",
  false_positive:
    "The model invented a seizure frequency when the gold standard is 'no seizure' or 'unknown'. These suggest over-extraction from irrelevant text.",
  over_estimate:
    "The model predicted a higher frequency than the gold standard. For example, '1 per day' instead of '1 per week'.",
  under_estimate:
    "The model predicted a lower frequency than the gold standard. For example, '1 per year' instead of '1 per month'.",
  near_miss:
    "The model was off by exactly one category bucket — close, but not correct. These are the easiest errors to fix.",
};

const ERROR_TYPE_ORDER: EnrichedRow["errorType"][] = [
  "false_negative",
  "false_positive",
  "over_estimate",
  "under_estimate",
  "near_miss",
  "correct",
];

// ── Executive Summary ────────────────────────────────────────────────

function ExecutiveSummary({
  summary,
  topPair,
  worstFamily,
}: {
  summary: ErrorSummary;
  topPair: ConfusedPair | null;
  worstFamily: FamilyBreakdown | null;
}) {
  const errorCount = summary.total - summary.correct;
  const errorRate = summary.total > 0 ? errorCount / summary.total : 0;
  const dominant = getDominantErrorType(summary);

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {/* Error rate */}
      <div className="rounded-lg border border-border bg-surface p-3">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-muted mb-1">
          Error Rate
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-2xl font-semibold text-error">
            {(errorRate * 100).toFixed(1)}%
          </span>
          <span className="text-[10px] text-muted">
            {errorCount} of {summary.total}
          </span>
        </div>
      </div>

      {/* Dominant error */}
      <div className="rounded-lg border border-border bg-surface p-3">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-muted mb-1">
          Dominant Error
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-lg font-semibold text-foreground">
            {dominant ? ERROR_TYPE_LABELS[dominant.type] : "—"}
          </span>
          <span className="text-[10px] text-muted">{dominant?.count ?? 0}</span>
        </div>
      </div>

      {/* Top confusion */}
      <div className="rounded-lg border border-border bg-surface p-3">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-muted mb-1">
          Top Confusion
        </div>
        {topPair ? (
          <div className="flex items-center gap-1 text-[11px]">
            <span className="font-medium text-foreground">
              {CATEGORY_SHORT_NAMES[topPair.gold] ?? topPair.gold}
            </span>
            <ArrowRight className="h-2.5 w-2.5 text-muted" />
            <span className="font-medium text-error">
              {CATEGORY_SHORT_NAMES[topPair.predicted] ?? topPair.predicted}
            </span>
            <span className="text-[10px] text-muted ml-1">×{topPair.count}</span>
          </div>
        ) : (
          <span className="text-[11px] text-muted">—</span>
        )}
      </div>

      {/* Worst family */}
      <div className="rounded-lg border border-border bg-surface p-3">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-muted mb-1">
          Worst Family
        </div>
        {worstFamily ? (
          <div className="flex items-baseline gap-1.5">
            <span className="text-lg font-semibold text-foreground">
              {worstFamily.family.replace(/_/g, " ")}
            </span>
            <span className="text-[10px] text-muted">
              {(worstFamily.errorRate * 100).toFixed(0)}%
            </span>
          </div>
        ) : (
          <span className="text-[11px] text-muted">—</span>
        )}
      </div>
    </div>
  );
}

// ── Error Distribution Bar ───────────────────────────────────────────

function ErrorDistributionBar({
  summary,
  activeFilter,
  onFilter,
}: {
  summary: ErrorSummary;
  activeFilter: ErrorFilter;
  onFilter: (filter: ErrorFilter) => void;
}) {
  const errorTotal = summary.total - summary.correct;
  if (errorTotal === 0) return null;

  const segments = (
    [
      { type: "false_negative" as const, count: summary.false_negative, color: "bg-error" },
      { type: "false_positive" as const, count: summary.false_positive, color: "bg-llm-alt" },
      { type: "over_estimate" as const, count: summary.over_estimate, color: "bg-error/70" },
      { type: "under_estimate" as const, count: summary.under_estimate, color: "bg-deterministic-alt" },
      { type: "near_miss" as const, count: summary.near_miss, color: "bg-muted" },
    ] as Array<{ type: EnrichedRow["errorType"]; count: number; color: string }>
  ).filter((s) => s.count > 0);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
          Error Distribution
        </div>
        <span className="text-[10px] text-muted">{errorTotal} errors total</span>
      </div>

      {/* Stacked bar */}
      <div className="flex h-3 rounded-full overflow-hidden bg-surface-raised border border-border">
        {segments.map((seg) => (
          <button
            key={seg.type}
            onClick={() =>
              onFilter(activeFilter === seg.type ? "all_errors" : seg.type)
            }
            className={`${seg.color} hover:opacity-80 transition-opacity ${
              activeFilter === seg.type ? "ring-2 ring-inset ring-foreground/30" : ""
            }`}
            style={{ width: `${(seg.count / errorTotal) * 100}%` }}
            title={`${ERROR_TYPE_LABELS[seg.type]}: ${seg.count}`}
          />
        ))}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3">
        {segments.map((seg) => (
          <button
            key={seg.type}
            onClick={() =>
              onFilter(activeFilter === seg.type ? "all_errors" : seg.type)
            }
            className={`flex items-center gap-1.5 text-[10px] transition-opacity hover:opacity-70 ${
              activeFilter === seg.type ? "font-semibold" : ""
            }`}
          >
            <div className={`h-2 w-2 rounded-full ${seg.color}`} />
            <span className="text-muted">{ERROR_TYPE_LABELS[seg.type]}</span>
            <span className="font-medium text-foreground">{seg.count}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

// ── Dimensional Breakdowns ───────────────────────────────────────────

function DimensionalBreakdown({
  confusedPairs,
  familyBreakdown,
}: {
  confusedPairs: ConfusedPair[];
  familyBreakdown: FamilyBreakdown[];
}) {
  const maxPairCount = Math.max(...confusedPairs.map((p) => p.count), 1);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Top confused pairs */}
      <div className="rounded-lg border border-border bg-surface p-4 space-y-3">
        <div className="flex items-center gap-2">
          <Activity className="h-3.5 w-3.5 text-muted" />
          <span className="text-[10px] font-semibold uppercase tracking-wider text-muted">
            Top Category Confusions
          </span>
        </div>
        {confusedPairs.length === 0 ? (
          <p className="text-[11px] text-muted">No confusions found.</p>
        ) : (
          <div className="space-y-2">
            {confusedPairs.map((pair, i) => (
              <div key={i} className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <div className="flex items-center gap-1">
                    <span className="font-medium text-foreground">
                      {CATEGORY_SHORT_NAMES[pair.gold] ?? pair.gold}
                    </span>
                    <ArrowRight className="h-2.5 w-2.5 text-muted" />
                    <span className="font-medium text-error">
                      {CATEGORY_SHORT_NAMES[pair.predicted] ?? pair.predicted}
                    </span>
                  </div>
                  <span className="text-muted tabular-nums">{pair.count}</span>
                </div>
                <div className="h-1.5 bg-surface-raised rounded-full overflow-hidden">
                  <div
                    className="h-full bg-error/60 rounded-full"
                    style={{ width: `${(pair.count / maxPairCount) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Family breakdown */}
      <div className="rounded-lg border border-border bg-surface p-4 space-y-3">
        <div className="flex items-center gap-2">
          <Layers className="h-3.5 w-3.5 text-muted" />
          <span className="text-[10px] font-semibold uppercase tracking-wider text-muted">
            Errors by Pipeline Family
          </span>
        </div>
        {familyBreakdown.length === 0 ? (
          <p className="text-[11px] text-muted">No family data.</p>
        ) : (
          <div className="space-y-2.5">
            {familyBreakdown.map((fam) => (
              <div key={fam.family} className="space-y-1">
                <div className="flex items-center justify-between text-[10px]">
                  <div className="flex items-center gap-1.5">
                    <FamilyIcon family={fam.family} />
                    <span className="font-medium text-foreground">
                      {fam.family.replace(/_/g, " ")}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-muted">
                      {fam.errors} of {fam.total}
                    </span>
                    <span className="font-semibold text-error tabular-nums">
                      {(fam.errorRate * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                <div className="h-1.5 bg-surface-raised rounded-full overflow-hidden">
                  <div
                    className="h-full bg-error/50 rounded-full"
                    style={{ width: `${fam.errorRate * 100}%` }}
                  />
                </div>
                {fam.dominantErrorType && (
                  <div className="text-[9px] text-muted">
                    Mostly{" "}
                    <span className="text-foreground">
                      {ERROR_TYPE_LABELS[fam.dominantErrorType].toLowerCase()}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function FamilyIcon({ family }: { family: string }) {
  if (family.includes("rules_only") || family.includes("deterministic")) {
    return <Zap className="h-3 w-3 text-deterministic" />;
  }
  if (family.includes("hybrid")) {
    return <BrainCircuit className="h-3 w-3 text-hybrid" />;
  }
  return <BarChart3 className="h-3 w-3 text-llm" />;
}

// ── Semantic Error Groups ────────────────────────────────────────────

function SemanticErrorGroups({
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
  // Group by error type
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

  // Collapse state per group
  const [collapsedGroups, setCollapsedGroups] = useState<Set<EnrichedRow["errorType"]>>(
    () => new Set(["correct", "near_miss"])
  );

  const toggleGroup = (type: EnrichedRow["errorType"]) => {
    setCollapsedGroups((prev) => {
      const next = new Set(prev);
      if (next.has(type)) next.delete(type);
      else next.add(type);
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
            {/* Group header */}
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

            {/* Group rows */}
            {!isCollapsed && (
              <div className="px-2 pb-2">
                {/* Sub-header */}
                <div className="grid grid-cols-[28px_1fr_120px_80px_28px] items-center gap-2 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted/60 border-b border-border/30">
                  <div />
                  <div>Label Transition</div>
                  <div>Category</div>
                  <div>Run</div>
                  <div />
                </div>

                <div className="space-y-0.5 mt-1">
                  {groupRows.map((row) => {
                    const rowKey = `${row.runId}-${row.sourceRowIndex}`;
                    const isExpanded = expandedRowKey === rowKey;

                    let compareRow: EnrichedRow | null = null;
                    let compareStatus: ComparisonResult["status"] = "no_compare";
                    if (compareSummary && row.sourceRowIndex < compareSummary.rows.length) {
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
                          {/* Severity dot */}
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

                          {/* Labels */}
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

                          {/* Categories */}
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

                          {/* Run */}
                          <div className="truncate">
                            <span
                              className="rounded bg-surface-raised px-1.5 py-0 text-[9px] font-mono text-muted border border-border truncate"
                              title={row.runId}
                            >
                              {row.runId.slice(0, 12)}
                              {row.runId.length > 12 ? "…" : ""}
                            </span>
                          </div>

                          {/* Expand */}
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
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ── Error Detail ─────────────────────────────────────────────────────

function ErrorDetail({
  row,
  compareRow,
  compareStatus,
  compareRunId,
}: {
  row: EnrichedRow;
  compareRow: EnrichedRow | null;
  compareStatus: ComparisonResult["status"];
  compareRunId: string | null;
}) {
  const workbenchHref = `/workbench?pipeline=${encodeURIComponent(row.pipelineFamily)}&split=${encodeURIComponent(row.split ?? "validation")}&row=${row.sourceRowIndex}&stage=score`;

  return (
    <div className="px-3 pb-3 pt-1 border-t border-border/50">
      <div className="mt-2 mb-2">
        <Link
          href={workbenchHref}
          className="inline-flex items-center gap-1.5 rounded-md border border-deterministic/20 bg-deterministic/5 px-2.5 py-1 text-[10px] font-medium text-deterministic hover:bg-deterministic/10 transition-colors"
        >
          <ExternalLink className="h-3 w-3" />
          Open in Workbench
        </Link>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* Primary prediction */}
        <div className="space-y-2">
          <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
            Primary Prediction
          </div>
          <div className="rounded-md border border-border bg-surface p-3 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-muted">Run</span>
              <span className="text-[10px] font-mono text-foreground">{row.runId}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-muted">Family</span>
              <span className="text-[10px] font-medium text-foreground">{row.pipelineFamily}</span>
            </div>
            <div className="border-t border-border/50 pt-2 space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-muted w-12">Gold</span>
                <span className="text-sm font-mono text-foreground">{row.goldLabel}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-muted w-12">Pred</span>
                <span
                  className={`text-sm font-mono ${
                    row.puristCorrect ? "text-foreground" : "text-error font-medium"
                  }`}
                >
                  {row.predictedLabel}
                </span>
              </div>
            </div>
            <div className="border-t border-border/50 pt-2 flex items-center gap-3">
              <CorrectnessBadge correct={row.puristCorrect} label="Purist" />
              <CorrectnessBadge correct={row.pragmaticCorrect} label="Pragmatic" />
            </div>
          </div>
        </div>

        {/* Category & comparison */}
        <div className="space-y-2">
          <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
            Category Analysis
          </div>
          <div className="rounded-md border border-border bg-surface p-3 space-y-2">
            <div className="flex items-center gap-2 text-[11px]">
              <span className="text-muted">Gold:</span>
              <span className="font-medium text-foreground">
                {CATEGORY_DISPLAY_NAMES[row.goldCategory] ?? row.goldCategory}
              </span>
              <span className="text-[9px] font-mono text-muted">({row.goldCategory})</span>
            </div>
            <div className="flex items-center gap-2 text-[11px]">
              <span className="text-muted">Pred:</span>
              <span
                className={`font-medium ${
                  row.puristCorrect ? "text-foreground" : "text-error"
                }`}
              >
                {CATEGORY_DISPLAY_NAMES[row.predictedCategory] ?? row.predictedCategory}
              </span>
              <span className="text-[9px] font-mono text-muted">({row.predictedCategory})</span>
            </div>
            {row.errorType !== "correct" && (
              <div className="flex items-center gap-2 text-[10px]">
                <span className="text-muted">Severity:</span>
                <span className="font-medium text-error capitalize">{row.severityLevel}</span>
                <span className="text-muted">({row.severity} magnitude levels)</span>
              </div>
            )}

            {compareRow && compareRunId && (
              <>
                <div className="border-t border-border/50 pt-2">
                  <div className="text-[10px] font-semibold uppercase tracking-wider text-muted mb-1.5">
                    Comparison — {compareRunId.slice(0, 40)}
                    {compareRunId.length > 40 ? "…" : ""}
                  </div>
                  <div className="flex items-center gap-2 text-[11px]">
                    <span className="text-muted">Pred:</span>
                    <span
                      className={`font-mono ${
                        compareRow.puristCorrect ? "text-success" : "text-error"
                      }`}
                    >
                      {compareRow.predictedLabel}
                    </span>
                    <span
                      className={`inline-flex items-center gap-1 rounded border px-1.5 py-0 text-[9px] font-medium ${comparisonStatusColor(compareStatus)}`}
                    >
                      <ComparisonIcon status={compareStatus} />
                      {comparisonStatusLabel(compareStatus)}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-[10px] mt-1">
                    <span className="text-muted">Category:</span>
                    <span>
                      {CATEGORY_SHORT_NAMES[compareRow.predictedCategory] ?? compareRow.predictedCategory}
                    </span>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Evidence & Rationale */}
      {(row.evidence || row.rationale) && (
        <div className="mt-3 space-y-3">
          {row.evidence && (
            <div className="space-y-1.5">
              <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
                Selected Evidence
              </div>
              <div className="rounded-md border border-border bg-surface p-3">
                <blockquote className="text-[11px] leading-relaxed text-foreground font-serif italic border-l-2 border-deterministic/30 pl-3">
                  {row.evidence}
                </blockquote>
              </div>
            </div>
          )}
          {row.rationale && (
            <div className="space-y-1.5">
              <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
                Model Rationale
              </div>
              <div className="rounded-md border border-border bg-surface p-3">
                <p className="text-[11px] leading-relaxed text-foreground">{row.rationale}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Small Components ─────────────────────────────────────────────────

function CorrectnessBadge({ correct, label }: { correct: boolean; label: string }) {
  return (
    <span className="flex items-center gap-1 text-[10px]">
      {correct ? (
        <CheckCircle className="h-3 w-3 text-success" />
      ) : (
        <XCircle className="h-3 w-3 text-error" />
      )}
      <span className={correct ? "text-success" : "text-error"}>{label}</span>
    </span>
  );
}

function ErrorTypeIcon({ type }: { type: EnrichedRow["errorType"] }) {
  const className = "h-4 w-4 shrink-0";
  switch (type) {
    case "correct":
      return <CheckCircle className={`${className} text-success`} />;
    case "false_negative":
      return <AlertTriangle className={`${className} text-error`} />;
    case "false_positive":
      return <AlertCircle className={`${className} text-llm-alt`} />;
    case "over_estimate":
      return <TrendingUp className={`${className} text-error`} />;
    case "under_estimate":
      return <TrendingDown className={`${className} text-deterministic-alt`} />;
    case "near_miss":
      return <Target className={`${className} text-error/70`} />;
  }
}

function ComparisonIcon({ status }: { status: ComparisonResult["status"] }) {
  const className = "h-3 w-3";
  switch (status) {
    case "fix":
      return <ArrowUpCircle className={`${className} text-success`} />;
    case "regression":
      return <ArrowDownCircle className={`${className} text-error`} />;
    case "both_wrong":
    case "both_right":
      return <MinusCircle className={`${className} text-muted`} />;
    case "no_compare":
      return <MinusCircle className={`${className} text-muted/50`} />;
  }
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-surface py-12 text-center">
      <Eye className="h-8 w-8 text-muted/40 mb-3" />
      <p className="text-sm font-medium text-muted">{message}</p>
    </div>
  );
}

// ── Gallery Inner ────────────────────────────────────────────────────

function GalleryInner() {
  const { selectedSummaries } = useObservatoryData();

  const [errorFilter, setErrorFilter] = useState<ErrorFilter>("all_errors");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [sortKey, setSortKey] = useState<SortKey>("severity");
  const [compareRunId, setCompareRunId] = useState<string>("");
  const [expandedRowKey, setExpandedRowKey] = useState<string | null>(null);

  useGalleryUrlSync(
    errorFilter,
    setErrorFilter,
    categoryFilter,
    setCategoryFilter,
    sortKey,
    setSortKey,
    compareRunId,
    setCompareRunId,
    expandedRowKey,
    setExpandedRowKey
  );

  const allEnrichedRows = useMemo(() => {
    const rows: EnrichedRow[] = [];
    for (const summary of selectedSummaries) {
      for (let i = 0; i < summary.rows.length; i++) {
        const row = summary.rows[i];
        rows.push(
          enrichRow({
            ...row,
            runId: summary.runId,
            pipelineFamily: summary.pipelineFamily,
            sourceRowIndex: i,
          })
        );
      }
    }
    return rows;
  }, [selectedSummaries]);

  const categories = useMemo(() => {
    const set = new Set<string>();
    for (const row of allEnrichedRows) {
      set.add(row.goldCategory);
      set.add(row.predictedCategory);
    }
    return Array.from(set).sort();
  }, [allEnrichedRows]);

  const filteredRows = useMemo(() => {
    let rows = filterRows(allEnrichedRows, errorFilter);
    if (categoryFilter !== "all") {
      rows = rows.filter(
        (r) => r.goldCategory === categoryFilter || r.predictedCategory === categoryFilter
      );
    }
    return sortRows(rows, sortKey);
  }, [allEnrichedRows, errorFilter, categoryFilter, sortKey]);

  const summary = useMemo(() => computeSummary(allEnrichedRows), [allEnrichedRows]);
  const topPairs = useMemo(() => getTopConfusedPairs(allEnrichedRows, 5), [allEnrichedRows]);
  const familyBreakdown = useMemo(() => getFamilyBreakdown(allEnrichedRows), [allEnrichedRows]);
  const worstFamily = familyBreakdown[0] ?? null;

  const compareSummary = useMemo(
    () => selectedSummaries.find((s) => s.runId === compareRunId) ?? null,
    [selectedSummaries, compareRunId]
  );

  const runOptions = selectedSummaries.map((s) => ({
    id: s.runId,
    label: `${s.runId.slice(0, 40)}${s.runId.length > 40 ? "…" : ""} (${s.pipelineFamily})`,
  }));

  return (
    <div className="flex h-full flex-col bg-background">
      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {selectedSummaries.length === 0 ? (
          <div className="p-5">
            <EmptyState message="Select runs in the Observatory first to populate the gallery." />
          </div>
        ) : (
          <div className="max-w-[1200px] mx-auto p-5 space-y-6">
            {/* 1. Executive Summary */}
            <ExecutiveSummary
              summary={summary}
              topPair={topPairs[0] ?? null}
              worstFamily={worstFamily}
            />

            {/* 2. Error Distribution + Controls */}
            <div className="rounded-lg border border-border bg-surface p-4 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <ErrorDistributionBar
                    summary={summary}
                    activeFilter={errorFilter}
                    onFilter={setErrorFilter}
                  />
                  <div className="flex items-center gap-1.5 rounded-md bg-surface-raised px-2 py-1 border border-border">
                    <span className="text-[10px] text-muted">Errors:</span>
                    <span className="text-[11px] font-semibold text-error">
                      {summary.total - summary.correct}
                    </span>
                    <span className="text-[10px] text-muted">/ {summary.total}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <select
                    value={sortKey}
                    onChange={(e) => setSortKey(e.target.value as SortKey)}
                    className="rounded-md border border-border bg-surface px-2 py-1 text-xs text-foreground focus:outline-none"
                  >
                    <option value="severity">Severity</option>
                    <option value="error_type">Error type</option>
                    <option value="gold_category">Gold category</option>
                    <option value="run">Run</option>
                  </select>
                  <select
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value)}
                    className="rounded-md border border-border bg-surface px-2 py-1 text-xs text-foreground focus:outline-none"
                  >
                    <option value="all">All categories</option>
                    {categories.map((c) => (
                      <option key={c} value={c}>
                        {CATEGORY_SHORT_NAMES[c] ?? c}
                      </option>
                    ))}
                  </select>
                  <div className="flex items-center gap-1.5">
                    <GitCompare className="h-3.5 w-3.5 text-muted" />
                    <select
                      value={compareRunId}
                      onChange={(e) => setCompareRunId(e.target.value)}
                      className="rounded-md border border-border bg-surface px-2 py-1 text-xs text-foreground focus:outline-none"
                    >
                      <option value="">Compare…</option>
                      {runOptions.map((r) => (
                        <option key={r.id} value={r.id}>
                          {r.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>

            {/* 3. Dimensional Breakdowns */}
            <DimensionalBreakdown
              confusedPairs={topPairs}
              familyBreakdown={familyBreakdown}
            />

            {/* 4. Semantic Error Groups */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Layers className="h-4 w-4 text-muted" />
                <span className="text-xs font-semibold uppercase tracking-wider text-muted">
                  Error Cases
                </span>
                <span className="text-[10px] text-muted">{filteredRows.length} rows</span>
              </div>
              <SemanticErrorGroups
                rows={filteredRows}
                compareSummary={compareSummary}
                expandedRowKey={expandedRowKey}
                onToggleRow={(key) =>
                  setExpandedRowKey((prev) => (prev === key ? null : key))
                }
                activeFilter={errorFilter}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Page Export ──────────────────────────────────────────────────────

export default function GalleryPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center bg-background text-muted">
          <div className="text-center">
            <p className="text-lg font-medium">Loading gallery…</p>
          </div>
        </div>
      }
    >
      <GalleryInner />
    </Suspense>
  );
}
