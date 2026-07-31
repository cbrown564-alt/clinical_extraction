"use client";

import { useState, useMemo, useEffect } from "react";
import { GitCompare, Layers } from "lucide-react";
import { useObservatoryData } from "@/components/observatory/useObservatoryData";
import { useGalleryUrlSync } from "@/lib/hooks";
import { gan2026Dataset } from "@/lib/datasets/gan2026";
import { SurfaceHeader, SurfaceLayout } from "@/components/surface";
import {
  type EnrichedRow,
  type ErrorFilter,
  type SortKey,
  CATEGORY_SHORT_NAMES,
  enrichRow,
  filterRows,
  sortRows,
  computeSummary,
  getTopConfusedPairs,
} from "@/lib/gallery-utils";
import { ExecutiveSummary } from "@/components/gallery/ExecutiveSummary";
import { ErrorDistributionBar } from "@/components/gallery/ErrorDistributionBar";
import { DimensionalBreakdown } from "@/components/gallery/DimensionalBreakdown";
import { SemanticErrorGroups } from "@/components/gallery/SemanticErrorGroups";
import { EmptyState } from "@/components/gallery/GalleryShared";

export function GanErrorGallery() {
  const { selectedSummaries, selectedRunIds, loadRunDetail } = useObservatoryData();

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

  useEffect(() => {
    for (const runId of selectedRunIds) {
      const summary = selectedSummaries.find((s) => s.runId === runId);
      if (summary && !summary.rows) {
        loadRunDetail(runId);
      }
    }
  }, [selectedRunIds, selectedSummaries, loadRunDetail]);

  const allEnrichedRows = useMemo(() => {
    const rows: EnrichedRow[] = [];
    for (const summary of selectedSummaries) {
      if (!summary.rows) continue;
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

  const compareSummary = useMemo(
    () => selectedSummaries.find((s) => s.runId === compareRunId) ?? null,
    [selectedSummaries, compareRunId]
  );

  const runOptions = selectedSummaries.map((s) => ({
    id: s.runId,
    label: `${s.runId.slice(0, 40)}${s.runId.length > 40 ? "…" : ""} (${s.pipelineFamily})`,
  }));

  return (
    <SurfaceLayout
      variant="fill"
      header={
        <SurfaceHeader
          surface="gallery"
          dataset={gan2026Dataset}
          description="Residual seizure-frequency errors grouped by type, with severity, evidence, and run-to-run comparison. Populated from the runs selected in Aggregate Performance."
        />
      }
    >
      <div className="min-h-0 flex-1 overflow-y-auto">
        {selectedSummaries.length === 0 ? (
          <div className="p-5">
            <EmptyState message="Select runs in Aggregate Performance first to populate the gallery." />
          </div>
        ) : (
          <div className="max-w-[1200px] mx-auto p-5 space-y-6">
            <ExecutiveSummary
              summary={summary}
              topPair={topPairs[0] ?? null}
            />

            <div className="rounded-lg border border-border bg-surface p-4 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <ErrorDistributionBar
                    summary={summary}
                    activeFilter={errorFilter}
                    onFilter={setErrorFilter}
                  />
                  <div className="flex items-center gap-1.5 rounded-md bg-surface-raised px-2 py-1 border border-border">
                    <span className="text-[11px] text-muted">Errors:</span>
                    <span className="text-xs font-semibold text-error">
                      {summary.total - summary.correct}
                    </span>
                    <span className="text-[11px] text-muted">/ {summary.total}</span>
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

            <DimensionalBreakdown confusedPairs={topPairs} />

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Layers className="h-4 w-4 text-muted" />
                <span className="text-xs font-semibold uppercase tracking-wider text-muted">
                  Error Cases
                </span>
                <span className="text-[11px] text-muted">{filteredRows.length} rows</span>
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
    </SurfaceLayout>
  );
}
