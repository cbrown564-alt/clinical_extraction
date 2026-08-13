"use client";

import { useMemo, useState } from "react";
import {
  BarChart3,
  Grid3X3,
  CheckCircle,
  Mountain,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { useObservatoryData } from "@/components/observatory/useObservatoryData";
import { useReviewUrlSync } from "@/lib/hooks";
import RunSelector from "@/components/observatory/RunSelector";
import PaperTable from "./PaperTable";
import ExportPanel from "./ExportPanel";
import type { RunSummary } from "@/lib/types";
import GeneralisationGap from "@/components/observatory/GeneralisationGap";
import ConfusionMatrix from "@/components/observatory/ConfusionMatrix";
import { gan2026Dataset } from "@/lib/datasets";
import { SurfaceHeader, SurfaceLayout } from "@/components/surface";

type ReviewTab = "comparison" | "matrix";

/** Abbreviate a long run ID to something readable. */
function abbreviateRunId(runId: string): string {
  const s = runId.replace(/^gan2026_/, "").replace(/_2026-\d{2}-\d{2}$/, "");
  if (s.length > 28) {
    return s.slice(0, 13) + "…" + s.slice(-12);
  }
  return s;
}

function RunLegend({ summaries }: { summaries: RunSummary[] }) {
  if (summaries.length === 0) return null;
  return (
    <div className="rounded-md border border-border bg-surface-raised px-3 py-2 space-y-1">
      <p className="text-[11px] font-semibold uppercase tracking-wider text-muted">Run Legend</p>
      <div className="flex flex-wrap gap-x-4 gap-y-1">
        {summaries.map((s, i) => (
          <div key={s.runId} className="flex items-center gap-1.5 text-[11px]">
            <span className="rounded bg-surface px-1 py-0 border border-border font-mono text-[11px] text-muted">
              R{i + 1}
            </span>
            <span className="text-foreground truncate max-w-[200px]" title={s.runId}>
              {abbreviateRunId(s.runId)}
            </span>
          </div>
        ))}
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
      className={`flex items-center gap-1.5 border-b-2 px-3 py-2 text-xs font-medium transition-colors ${
        active
          ? "border-llm text-foreground"
          : "border-transparent text-muted hover:text-foreground"
      }`}
    >
      {icon}
      {label}
      {badge && (
        <span className="ml-0.5 rounded bg-surface-raised px-1 py-0 text-[11px] text-muted border border-border">
          {badge}
        </span>
      )}
    </button>
  );
}

export default function ReportBuilder() {
  const {
    registryLoading,
    selectedRunIds,
    selectedSummaries,
    loadingRuns,
    runErrors,
    toggleRun,
    selectRuns,
    runs,
  } = useObservatoryData();

  const [activeTab, setActiveTab] = useState<ReviewTab>("comparison");
  const [showGap, setShowGap] = useState(false);
  useReviewUrlSync(activeTab, setActiveTab);

  const hasTestData = useMemo(() => {
    return selectedSummaries.some((s) => s.testMetrics);
  }, [selectedSummaries]);

  // Sort summaries by purist F1 descending
  const sortedSummaries = useMemo(
    () => [...selectedSummaries].sort((a, b) => b.puristF1 - a.puristF1),
    [selectedSummaries]
  );

  // ── Run Comparison data ──
  const comparisonRows = useMemo(() => {
    return sortedSummaries.map((s) => {
      const gap =
        s.validationMetrics && s.testMetrics
          ? s.validationMetrics.puristAccuracy - s.testMetrics.puristAccuracy
          : null;
      return [
        s.runId,
        s.pipelineFamily,
        s.split,
        s.rowCount,
        s.puristAccuracy,
        s.puristF1,
        s.pragmaticAccuracy,
        s.pragmaticF1,
        gap,
      ];
    });
  }, [sortedSummaries]);

  const comparisonHeaders = useMemo(
    () => [
      "Run ID",
      "Family",
      "Split",
      "Rows",
      "Strict Acc",
      "Strict F1",
      "Lenient Acc",
      "Lenient F1",
      "Val→Test Gap",
    ],
    []
  );
  const comparisonAlign = useMemo<("left" | "right" | "center")[]>(
    () => ["left", "left", "left", "right", "right", "right", "right", "right", "right"],
    []
  );

  const comparisonCellClasses = useMemo(() => {
    return comparisonRows.map(() => [
      "max-w-[200px] truncate",
      "max-w-[160px] truncate",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
    ]);
  }, [comparisonRows]);

  const reportSections = useMemo(
    () => [
      {
        title: "Run Comparison",
        headers: comparisonHeaders,
        rows: comparisonRows,
        align: comparisonAlign,
      },
    ],
    [comparisonHeaders, comparisonRows, comparisonAlign]
  );

  if (registryLoading) {
    return (
      <div className="flex h-full items-center justify-center text-muted">
        <p className="text-sm font-medium">Loading registry…</p>
      </div>
    );
  }

  return (
    <SurfaceLayout
      variant="fill"
      header={
        <SurfaceHeader surface="observatory" dataset={gan2026Dataset} />
      }
    >
      {/* Tab bar */}
      <div className="flex shrink-0 items-center gap-1 border-b border-border px-5">
        <TabButton
          active={activeTab === "comparison"}
          onClick={() => setActiveTab("comparison")}
          icon={<BarChart3 className="h-3.5 w-3.5" />}
          label="Run Comparison"
          badge={selectedSummaries.length > 0 ? `${selectedSummaries.length}` : undefined}
        />
        <TabButton
          active={activeTab === "matrix"}
          onClick={() => setActiveTab("matrix")}
          icon={<Grid3X3 className="h-3.5 w-3.5" />}
          label="Confusion Matrix"
        />
      </div>

      {/* Content */}
      <div className="min-h-0 flex-1 overflow-hidden">
        {activeTab === "comparison" && (
          <div className="h-full overflow-y-auto p-5 max-w-[1400px] mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              <div className="lg:col-span-2 space-y-5">
                {/* Export actions */}
                {selectedSummaries.length > 0 && (
                  <ExportPanel
                    sections={reportSections}
                    runIds={Array.from(selectedRunIds)}
                    metadata={{
                      generatedAt: new Date().toISOString(),
                      url: typeof window !== "undefined" ? window.location.href : undefined,
                    }}
                  />
                )}
                <PaperTable
                  title="Run Comparison"
                  caption="Component ablation table. Generalisation gap shown when both validation and test metrics are available."
                  headers={comparisonHeaders}
                  rows={comparisonRows}
                  align={comparisonAlign}
                  cellClasses={comparisonCellClasses}
                  footer={`Runs: ${Array.from(selectedRunIds).join(", ") || "none selected"}`}
                />
                <RunLegend summaries={sortedSummaries} />

                {/* Inline Generalisation Gap */}
                {hasTestData && (
                  <div className="space-y-3">
                    <button
                      onClick={() => setShowGap((s) => !s)}
                      className="flex items-center gap-2 rounded-md border border-border bg-surface-raised px-4 py-2 text-xs font-medium text-muted hover:text-foreground transition-colors"
                    >
                      <Mountain className="h-3.5 w-3.5" />
                      {showGap ? "Hide" : "Show"} generalisation gap
                      {showGap ? (
                        <ChevronUp className="h-3 w-3 ml-auto" />
                      ) : (
                        <ChevronDown className="h-3 w-3 ml-auto" />
                      )}
                    </button>
                    {showGap && (
                      <div className="transition-opacity duration-200">
                        <GeneralisationGap summaries={selectedSummaries} />
                      </div>
                    )}
                  </div>
                )}
              </div>
              <div>
                <RunSelector
                  runs={runs}
                  selectedIds={selectedRunIds}
                  loadingIds={loadingRuns}
                  errors={runErrors}
                  onToggle={toggleRun}
                  onSelectRuns={selectRuns}
                />
              </div>
            </div>
          </div>
        )}

        {activeTab === "matrix" && (
          <div className="h-full overflow-y-auto p-5 max-w-[1400px] mx-auto space-y-5">
            {selectedSummaries.length === 0 ? (
              <div className="rounded-lg border border-border bg-surface p-8 text-center">
                <CheckCircle className="h-6 w-6 text-muted mx-auto mb-2" />
                <p className="text-sm text-muted font-medium">No runs selected</p>
                <p className="text-xs text-muted mt-1">
                  Select runs from the registry in the <strong>Run Comparison</strong> tab.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="rounded-md border border-border bg-surface-raised px-4 py-3">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-foreground mb-1">
                    Confusion Matrix
                  </h3>
                  <p className="text-xs text-muted">
                    Heatmap breakdown of true category labels vs model predictions.
                  </p>
                </div>
                <ConfusionMatrix summaries={selectedSummaries} />
              </div>
            )}
          </div>
        )}
      </div>
    </SurfaceLayout>
  );
}
