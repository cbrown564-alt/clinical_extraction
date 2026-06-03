"use client";

import { Suspense, useState, useMemo } from "react";
import { LayoutGrid, Filter, GitCompare, Eye, ArrowRight, CheckCircle, XCircle } from "lucide-react";
import { useObservatoryData } from "@/components/observatory/useObservatoryData";
import type { RowScore } from "@/lib/types";

type GalleryTab = "errors" | "transition";
type ErrorFilter = "all" | "purist_wrong" | "pragmatic_wrong" | "both_wrong" | "purist_only_wrong";

function GalleryInner() {
  const { selectedSummaries } = useObservatoryData();
  const [activeTab, setActiveTab] = useState<GalleryTab>("errors");
  const [errorFilter, setErrorFilter] = useState<ErrorFilter>("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [runA, setRunA] = useState<string>("");
  const [runB, setRunB] = useState<string>("");
  const [transitionFilter, setTransitionFilter] = useState<
    "all" | "a_wrong_b_right" | "a_right_b_wrong" | "both_wrong" | "both_right"
  >("all");

  const allRows = useMemo(() => {
    const rows: Array<RowScore & { runId: string; pipelineFamily: string }> = [];
    for (const summary of selectedSummaries) {
      for (const row of summary.rows) {
        rows.push({ ...row, runId: summary.runId, pipelineFamily: summary.pipelineFamily });
      }
    }
    return rows;
  }, [selectedSummaries]);

  const categories = useMemo(() => {
    const set = new Set<string>();
    for (const row of allRows) {
      set.add(row.goldCategory);
      set.add(row.predictedCategory);
    }
    return Array.from(set).sort();
  }, [allRows]);

  const filteredRows = useMemo(() => {
    return allRows.filter((row) => {
      if (categoryFilter !== "all") {
        if (row.goldCategory !== categoryFilter && row.predictedCategory !== categoryFilter) return false;
      }
      switch (errorFilter) {
        case "purist_wrong":
          return !row.puristCorrect;
        case "pragmatic_wrong":
          return !row.pragmaticCorrect;
        case "both_wrong":
          return !row.puristCorrect && !row.pragmaticCorrect;
        case "purist_only_wrong":
          return !row.puristCorrect && row.pragmaticCorrect;
        default:
          return true;
      }
    });
  }, [allRows, errorFilter, categoryFilter]);

  // Transition matrix data
  const transitionData = useMemo(() => {
    if (!runA || !runB) return [];
    const summaryA = selectedSummaries.find((s) => s.runId === runA);
    const summaryB = selectedSummaries.find((s) => s.runId === runB);
    if (!summaryA || !summaryB) return [];

    const mapA = new Map<number, RowScore>();
    for (const row of summaryA.rows) {
      // Use index in rows array as proxy for source_row_index
      mapA.set(summaryA.rows.indexOf(row), row);
    }

    const result: Array<{
      rowIdx: number;
      rowA: RowScore;
      rowB: RowScore;
      status: "a_wrong_b_right" | "a_right_b_wrong" | "both_wrong" | "both_right";
    }> = [];

    summaryB.rows.forEach((rowB, idx) => {
      const rowA = mapA.get(idx);
      if (!rowA) return;
      let status: typeof result[0]["status"];
      if (!rowA.puristCorrect && rowB.puristCorrect) status = "a_wrong_b_right";
      else if (rowA.puristCorrect && !rowB.puristCorrect) status = "a_right_b_wrong";
      else if (!rowA.puristCorrect && !rowB.puristCorrect) status = "both_wrong";
      else status = "both_right";

      if (transitionFilter !== "all" && status !== transitionFilter) return;
      result.push({ rowIdx: idx, rowA, rowB, status });
    });

    return result;
  }, [selectedSummaries, runA, runB, transitionFilter]);

  const runOptions = selectedSummaries.map((s) => ({ id: s.runId, label: `${s.runId} (${s.pipelineFamily})` }));

  return (
    <div className="flex h-full flex-col bg-background">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border bg-surface px-5 py-2.5 shadow-sm z-10">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-error/10">
            <LayoutGrid className="h-4 w-4 text-error" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="rounded bg-surface-raised px-1.5 py-0 text-[10px] font-medium uppercase tracking-wider text-muted border border-border">
                Gallery
              </span>
              <span className="text-[10px] text-muted">Phase 4 — Error Autopsy</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 rounded-md bg-surface-raised px-2.5 py-1 border border-border">
            <span className="text-[10px] text-muted">Rows:</span>
            <span className="text-[11px] font-semibold text-foreground">
              {activeTab === "errors" ? filteredRows.length : transitionData.length}
            </span>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="flex items-center gap-1 border-b border-border bg-surface px-5">
        <TabButton
          active={activeTab === "errors"}
          onClick={() => setActiveTab("errors")}
          icon={<Filter className="h-3.5 w-3.5" />}
          label="Error Gallery"
        />
        <TabButton
          active={activeTab === "transition"}
          onClick={() => setActiveTab("transition")}
          icon={<GitCompare className="h-3.5 w-3.5" />}
          label="Transition Matrix"
        />
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 border-b border-border bg-surface px-5 py-2">
        {activeTab === "errors" && (
          <>
            <select
              value={errorFilter}
              onChange={(e) => setErrorFilter(e.target.value as ErrorFilter)}
              className="rounded-lg border border-border bg-surface px-2.5 py-1 text-xs text-foreground focus:outline-none"
            >
              <option value="all">All rows</option>
              <option value="purist_wrong">Purist wrong</option>
              <option value="pragmatic_wrong">Pragmatic wrong</option>
              <option value="both_wrong">Both wrong</option>
              <option value="purist_only_wrong">Purist-only wrong</option>
            </select>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="rounded-lg border border-border bg-surface px-2.5 py-1 text-xs text-foreground focus:outline-none"
            >
              <option value="all">All categories</option>
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </>
        )}
        {activeTab === "transition" && (
          <>
            <select
              value={runA}
              onChange={(e) => setRunA(e.target.value)}
              className="rounded-lg border border-border bg-surface px-2.5 py-1 text-xs text-foreground focus:outline-none"
            >
              <option value="">Select run A</option>
              {runOptions.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.label}
                </option>
              ))}
            </select>
            <ArrowRight className="h-3 w-3 text-muted" />
            <select
              value={runB}
              onChange={(e) => setRunB(e.target.value)}
              className="rounded-lg border border-border bg-surface px-2.5 py-1 text-xs text-foreground focus:outline-none"
            >
              <option value="">Select run B</option>
              {runOptions.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.label}
                </option>
              ))}
            </select>
            <select
              value={transitionFilter}
              onChange={(e) => setTransitionFilter(e.target.value as typeof transitionFilter)}
              className="rounded-lg border border-border bg-surface px-2.5 py-1 text-xs text-foreground focus:outline-none ml-2"
            >
              <option value="all">All transitions</option>
              <option value="a_wrong_b_right">A wrong, B right</option>
              <option value="a_right_b_wrong">A right, B wrong</option>
              <option value="both_wrong">Both wrong</option>
              <option value="both_right">Both right</option>
            </select>
          </>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5">
        {selectedSummaries.length === 0 ? (
          <EmptyState message="Select runs in the Observatory first to populate the gallery." />
        ) : activeTab === "errors" ? (
          <ErrorGrid rows={filteredRows} />
        ) : (
          <TransitionGrid data={transitionData} runA={runA} runB={runB} />
        )}
      </div>
    </div>
  );
}

function ErrorGrid({
  rows,
}: {
  rows: Array<RowScore & { runId: string; pipelineFamily: string }>;
}) {
  if (rows.length === 0) {
    return <EmptyState message="No rows match the current filters." />;
  }

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {rows.slice(0, 300).map((row, idx) => (
        <ErrorCard key={`${row.runId}-${idx}`} row={row} />
      ))}
    </div>
  );
}

function ErrorCard({
  row,
}: {
  row: RowScore & { runId: string; pipelineFamily: string };
}) {
  return (
    <div className="rounded-lg border border-border bg-surface p-3 hover:border-error/30 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1.5">
          <span className="rounded bg-surface-raised px-1 py-0 text-[9px] font-mono text-muted border border-border">
            {row.runId.slice(0, 20)}…
          </span>
        </div>
        <div className="flex items-center gap-1">
          {row.puristCorrect ? (
            <CheckCircle className="h-3 w-3 text-success" />
          ) : (
            <XCircle className="h-3 w-3 text-error" />
          )}
          <span className="text-[9px] text-muted">P</span>
          {row.pragmaticCorrect ? (
            <CheckCircle className="h-3 w-3 text-success ml-1" />
          ) : (
            <XCircle className="h-3 w-3 text-error ml-1" />
          )}
          <span className="text-[9px] text-muted">G</span>
        </div>
      </div>

      <div className="space-y-1.5">
        <div className="flex items-center gap-2 text-[11px]">
          <span className="text-muted">Gold:</span>
          <span className="font-mono text-foreground">{row.goldLabel}</span>
        </div>
        <div className="flex items-center gap-2 text-[11px]">
          <span className="text-muted">Pred:</span>
          <span className="font-mono text-foreground">{row.predictedLabel}</span>
        </div>
        <div className="flex items-center gap-2 text-[10px]">
          <span className="text-muted">Categories:</span>
          <span
            className={`font-mono ${
              row.puristCorrect ? "text-success" : "text-error"
            }`}
          >
            {row.goldCategory}
          </span>
          <ArrowRight className="h-2.5 w-2.5 text-muted" />
          <span
            className={`font-mono ${
              row.puristCorrect ? "text-success" : "text-error"
            }`}
          >
            {row.predictedCategory}
          </span>
        </div>
      </div>

      {/* Mini stage trace dots (approximated) */}
      <div className="mt-2 flex items-center gap-1">
        {["extract", "normalise", "select", "score"].map((stage, i) => (
          <div
            key={stage}
            className={`h-1.5 w-1.5 rounded-full ${
              i === 3 && !row.puristCorrect
                ? "bg-error"
                : i === 3
                ? "bg-success"
                : "bg-deterministic/30"
            }`}
            title={stage}
          />
        ))}
      </div>
    </div>
  );
}

function TransitionGrid({
  data,
  runA,
  runB,
}: {
  data: Array<{
    rowIdx: number;
    rowA: RowScore;
    rowB: RowScore;
    status: string;
  }>;
  runA: string;
  runB: string;
}) {
  if (!runA || !runB) {
    return <EmptyState message="Select two runs to compare transitions." />;
  }

  if (data.length === 0) {
    return <EmptyState message="No transitions match the current filter." />;
  }

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {data.slice(0, 300).map((item, idx) => (
          <TransitionCard key={idx} item={item} />
        ))}
      </div>
    </div>
  );
}

function TransitionCard({
  item,
}: {
  item: {
    rowIdx: number;
    rowA: RowScore;
    rowB: RowScore;
    status: string;
  };
}) {
  const statusColor =
    item.status === "a_wrong_b_right"
      ? "border-success/30 bg-success/5"
      : item.status === "a_right_b_wrong"
      ? "border-error/30 bg-error/5"
      : item.status === "both_wrong"
      ? "border-error/20 bg-error/3"
      : "border-border";

  const statusLabel =
    item.status === "a_wrong_b_right"
      ? "B fixes A"
      : item.status === "a_right_b_wrong"
      ? "B regresses A"
      : item.status === "both_wrong"
      ? "Both wrong"
      : "Both right";

  return (
    <div className={`rounded-lg border ${statusColor} p-3 transition-colors`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-[9px] font-mono text-muted">Row {item.rowIdx}</span>
        <span
          className={`rounded px-1.5 py-0 text-[9px] font-medium ${
            item.status === "a_wrong_b_right"
              ? "bg-success/10 text-success"
              : item.status === "a_right_b_wrong"
              ? "bg-error/10 text-error"
              : "bg-muted/10 text-muted"
          }`}
        >
          {statusLabel}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div className="space-y-1">
          <div className="text-[9px] font-semibold uppercase text-muted">Run A</div>
          <div className="text-[10px] font-mono text-foreground">{item.rowA.predictedLabel}</div>
          <div className="text-[9px] text-muted">{item.rowA.predictedCategory}</div>
        </div>
        <div className="space-y-1">
          <div className="text-[9px] font-semibold uppercase text-muted">Run B</div>
          <div className="text-[10px] font-mono text-foreground">{item.rowB.predictedLabel}</div>
          <div className="text-[9px] text-muted">{item.rowB.predictedCategory}</div>
        </div>
      </div>

      <div className="mt-2 flex items-center gap-2 text-[10px]">
        <span className="text-muted">Gold:</span>
        <span className="font-mono text-foreground">{item.rowA.goldLabel}</span>
      </div>
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-surface py-12 text-center">
      <Eye className="h-8 w-8 text-muted/40 mb-3" />
      <p className="text-sm font-medium text-muted">{message}</p>
    </div>
  );
}

function TabButton({
  active,
  onClick,
  icon,
  label,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 border-b-2 px-3 py-2 text-[11px] font-medium transition-colors ${
        active
          ? "border-error text-foreground"
          : "border-transparent text-muted hover:text-foreground"
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

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
