"use client";

import { Suspense, useState } from "react";
import { Telescope, BarChart3, Mountain, Grid3X3 } from "lucide-react";
import { useObservatoryData } from "@/components/observatory/useObservatoryData";
import RunSelector from "@/components/observatory/RunSelector";
import RunLadder from "@/components/observatory/RunLadder";
import GeneralisationGap from "@/components/observatory/GeneralisationGap";
import ConfusionMatrix from "@/components/observatory/ConfusionMatrix";

type VizTab = "ladder" | "gap" | "matrix";

function ObservatoryInner() {
  const {
    registryLoading,
    selectedRunIds,
    selectedSummaries,
    loadingRuns,
    runErrors,
    toggleRun,
    selectRuns,
    hasTestData,
    runs,
  } = useObservatoryData();

  const [activeTab, setActiveTab] = useState<VizTab>("ladder");

  // Aggregate stats across selected runs
  const totalRows = selectedSummaries.reduce((sum, s) => sum + s.rowCount, 0);
  const avgPurist =
    selectedSummaries.length > 0
      ? selectedSummaries.reduce((sum, s) => sum + s.puristAccuracy, 0) / selectedSummaries.length
      : 0;
  const avgPragmatic =
    selectedSummaries.length > 0
      ? selectedSummaries.reduce((sum, s) => sum + s.pragmaticAccuracy, 0) / selectedSummaries.length
      : 0;

  return (
    <div className="flex h-full flex-col bg-background">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border bg-surface px-5 py-2.5 shadow-sm z-10">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-llm-alt/10">
            <Telescope className="h-4 w-4 text-llm" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="rounded bg-surface-raised px-1.5 py-0 text-[10px] font-medium uppercase tracking-wider text-muted border border-border">
                Observatory
              </span>
              <span className="text-[10px] text-muted">Phase 3 — Corpus &amp; Ladder</span>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {registryLoading ? (
          <div className="flex h-full items-center justify-center text-muted">
            <div className="text-center">
              <p className="text-sm font-medium">Loading registry…</p>
            </div>
          </div>
        ) : (
          <div className="space-y-5 p-5 max-w-[1400px] mx-auto">
            {/* Run Selector Table */}
            <RunSelector
              runs={runs}
              selectedIds={selectedRunIds}
              loadingIds={loadingRuns}
              errors={runErrors}
              onToggle={toggleRun}
              onSelectRuns={selectRuns}
            />

            {/* Dashboard stats */}
            {selectedSummaries.length > 0 && (
              <div className="grid grid-cols-4 gap-3">
                <div className="rounded-lg border border-border bg-surface p-3">
                  <div className="text-[9px] font-semibold uppercase tracking-wider text-muted">
                    Selected Runs
                  </div>
                  <div className="mt-1 text-xl font-semibold text-foreground">
                    {selectedSummaries.length}
                  </div>
                </div>
                <div className="rounded-lg border border-border bg-surface p-3">
                  <div className="text-[9px] font-semibold uppercase tracking-wider text-muted">
                    Total Rows
                  </div>
                  <div className="mt-1 text-xl font-semibold text-foreground">
                    {totalRows.toLocaleString()}
                  </div>
                </div>
                <div className="rounded-lg border border-border bg-surface p-3">
                  <div className="text-[9px] font-semibold uppercase tracking-wider text-muted">
                    Avg Purist Acc
                  </div>
                  <div className="mt-1 text-xl font-semibold text-deterministic">
                    {(avgPurist * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="rounded-lg border border-border bg-surface p-3">
                  <div className="text-[9px] font-semibold uppercase tracking-wider text-muted">
                    Avg Pragmatic Acc
                  </div>
                  <div className="mt-1 text-xl font-semibold text-success">
                    {(avgPragmatic * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            )}

            {/* Test data banner */}
            {selectedSummaries.length > 0 && hasTestData && (
              <div className="flex items-center gap-2 rounded-lg border border-llm/20 bg-llm/5 px-3 py-2">
                <div className="h-2 w-2 rounded-full bg-llm animate-pulse" />
                <span className="text-[11px] font-medium text-llm">
                  Test data detected — Generalisation Gap visualisation is available.
                </span>
                <button
                  onClick={() => setActiveTab("gap")}
                  className="ml-auto text-[10px] font-medium text-llm underline hover:no-underline"
                >
                  View gap →
                </button>
              </div>
            )}

            {/* Visualization tabs */}
            {selectedSummaries.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center gap-1 border-b border-border">
                  <TabButton
                    active={activeTab === "ladder"}
                    onClick={() => setActiveTab("ladder")}
                    icon={<BarChart3 className="h-3.5 w-3.5" />}
                    label="Run Ladder"
                  />
                  <TabButton
                    active={activeTab === "gap"}
                    onClick={() => setActiveTab("gap")}
                    icon={<Mountain className="h-3.5 w-3.5" />}
                    label="Generalisation Gap"
                    badge={hasTestData ? "test data" : undefined}
                  />
                  <TabButton
                    active={activeTab === "matrix"}
                    onClick={() => setActiveTab("matrix")}
                    icon={<Grid3X3 className="h-3.5 w-3.5" />}
                    label="Confusion Matrix"
                  />
                </div>

                <div className="min-h-[300px]">
                  {activeTab === "ladder" && <RunLadder summaries={selectedSummaries} />}
                  {activeTab === "gap" && <GeneralisationGap summaries={selectedSummaries} />}
                  {activeTab === "matrix" && <ConfusionMatrix summaries={selectedSummaries} />}
                </div>
              </div>
            )}

            {/* Empty state when nothing selected */}
            {selectedSummaries.length === 0 && (
              <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-surface py-12 text-center">
                <Telescope className="h-8 w-8 text-muted/40 mb-3" />
                <p className="text-sm font-medium text-muted">No runs selected</p>
                <p className="text-[11px] text-muted mt-1 max-w-md">
                  Select runs from the registry table above. Runs with test data are highlighted in the{" "}
                  <span className="text-llm font-medium">Has test data</span> filter.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function TabButton({
  active,
  onClick,
  icon,
  label,
  badge,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
  badge?: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 border-b-2 px-3 py-2 text-[11px] font-medium transition-colors ${
        active
          ? "border-llm text-foreground"
          : "border-transparent text-muted hover:text-foreground"
      }`}
    >
      {icon}
      {label}
      {badge && (
        <span className="ml-1 rounded-full bg-llm/10 px-1.5 py-0 text-[9px] font-medium text-llm">
          {badge}
        </span>
      )}
    </button>
  );
}

export default function ObservatoryPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center bg-background text-muted">
          <div className="text-center">
            <p className="text-lg font-medium">Loading observatory…</p>
          </div>
        </div>
      }
    >
      <ObservatoryInner />
    </Suspense>
  );
}
