"use client";

import { useMemo, useState } from "react";
import {
  BarChart3,
  Grid3X3,
  AlertTriangle,
  ShieldCheck,
  FileText,
  CheckCircle,
} from "lucide-react";
import { useObservatoryData } from "@/components/observatory/useObservatoryData";
import RunSelector from "@/components/observatory/RunSelector";
import PaperTable from "./PaperTable";
import ExportPanel from "./ExportPanel";
import { classifyError, ERROR_TYPE_LABELS } from "@/lib/gallery-utils";
import type { RunSummary } from "@/lib/types";

type ReviewTab = "assembly" | "comparison" | "perlabel" | "errors" | "evidence";

const PURIST_CATEGORIES = [
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

const CATEGORY_SHORT_NAMES: Record<string, string> = {
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

function f1CellClass(f1: number): string {
  if (f1 >= 0.8) return "text-success font-medium";
  if (f1 >= 0.5) return "text-llm font-medium";
  return "text-error font-medium";
}

/** Abbreviate a long run ID to something readable. */
function abbreviateRunId(runId: string): string {
  // Remove common prefix and date suffix
  let s = runId.replace(/^gan2026_/, "").replace(/_2026-\d{2}-\d{2}$/, "");
  // If still very long, truncate middle
  if (s.length > 28) {
    return s.slice(0, 13) + "…" + s.slice(-12);
  }
  return s;
}

function RunLegend({ summaries }: { summaries: RunSummary[] }) {
  if (summaries.length === 0) return null;
  return (
    <div className="rounded-md border border-border bg-surface-raised px-3 py-2 space-y-1">
      <p className="text-[10px] font-semibold uppercase tracking-wider text-muted">Run Legend</p>
      <div className="flex flex-wrap gap-x-4 gap-y-1">
        {summaries.map((s, i) => (
          <div key={s.runId} className="flex items-center gap-1.5 text-[10px]">
            <span className="rounded bg-surface px-1 py-0 border border-border font-mono text-[9px] text-muted">
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

function computeEvidenceMetrics(summary: RunSummary) {
  const rows = summary.rows;
  const total = rows.length;
  if (total === 0) return { exact: 0, valid: 0, repair: 0, unknownRate: 0, avgEvidenceLen: 0 };

  // exact evidence = evidence is a verbatim substring of note text
  // We don't have note text in RunSummary, so we approximate with evidence_valid heuristic
  // For now, valid evidence rate is what we can compute from RowScore
  // We'll use a placeholder for exact evidence based on pragmatic correctness proxy
  const validEvidence = rows.filter((r) => r.evidence && r.evidence.length > 3).length;
  const unknownRate = rows.filter((r) => r.predictedCategory === "seizure_freq_unknown").length;

  return {
    exact: validEvidence / total,
    valid: validEvidence / total,
    repair: 0, // repair_changes not available in RunSummary rows
    unknownRate: unknownRate / total,
    avgEvidenceLen: total > 0
      ? rows.reduce((sum, r) => sum + (r.evidence?.length ?? 0), 0) / total
      : 0,
  };
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
          ? "border-success text-foreground"
          : "border-transparent text-muted hover:text-foreground"
      }`}
    >
      {icon}
      {label}
      {badge && (
        <span className="ml-0.5 rounded bg-surface-raised px-1 py-0 text-[9px] text-muted border border-border">
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

  const [activeTab, setActiveTab] = useState<ReviewTab>("assembly");

  // Sort summaries by purist F1 descending
  const sortedSummaries = useMemo(
    () => [...selectedSummaries].sort((a, b) => b.puristF1 - a.puristF1),
    [selectedSummaries]
  );

  // ── Run Comparison data ──
  const comparisonRows = useMemo(() => {
    return sortedSummaries.map((s) => {
      const ev = computeEvidenceMetrics(s);
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
        ev.valid,
        gap,
      ];
    });
  }, [sortedSummaries]);

    const comparisonHeaders = useMemo(() => [
    "Run ID",
    "Family",
    "Split",
    "Rows",
    "Purist Acc",
    "Purist F1",
    "Pragmatic Acc",
    "Pragmatic F1",
    "Evidence Valid",
    "Val→Test Gap",
  ], []);
  const comparisonAlign = useMemo<("left" | "right" | "center")[]>(() => [
    "left", "left", "left", "right", "right", "right", "right", "right", "right", "right",
  ], []);

  // ── Per-Label Performance data ──
  const perLabelHeaders = useMemo(() => {
    const base = ["Category"];
    sortedSummaries.forEach((_s, i) => {
      base.push(`R${i + 1} P`);
      base.push(`R${i + 1} R`);
      base.push(`R${i + 1} F1`);
      base.push(`R${i + 1} Supp`);
    });
    return base;
  }, [sortedSummaries]);

  const perLabelRows = useMemo(() => {
    return PURIST_CATEGORIES.map((cat) => {
      const row: (string | number | null)[] = [CATEGORY_SHORT_NAMES[cat] ?? cat];
      const cellCls: string[] = [""];
      for (const s of sortedSummaries) {
        const m = s.perCategoryMetrics[cat];
        if (m) {
          row.push(m.precision, m.recall, m.f1, m.support);
          cellCls.push("", "", f1CellClass(m.f1), "text-muted");
        } else {
          row.push(null, null, null, null);
          cellCls.push("", "", "", "");
        }
      }
      return { row, cellCls };
    });
  }, [sortedSummaries]);

  const perLabelAlign: ("left" | "right")[] = useMemo(() => {
    const base: ("left" | "right")[] = ["left"];
    for (let i = 0; i < sortedSummaries.length; i++) {
      base.push("right", "right", "right", "right");
    }
    return base;
  }, [sortedSummaries]);

  // ── Error Taxonomy data ──
  const errorTypes = useMemo(() => ["false_negative", "false_positive", "over_estimate", "under_estimate", "near_miss"] as const, []);

  const errorRows = useMemo(() => {
    return errorTypes.map((et) => {
      const row: (string | number | null)[] = [ERROR_TYPE_LABELS[et]];
      for (const s of sortedSummaries) {
        const errors = s.rows.filter((r) => classifyError(r) === et);
        row.push(errors.length, errors.length / (s.rows.length || 1));
      }
      return row;
    });
  }, [sortedSummaries, errorTypes]);

  const errorHeaders = useMemo(() => {
    const base = ["Error Type"];
    sortedSummaries.forEach((_s, i) => {
      base.push(`R${i + 1} #`);
      base.push(`R${i + 1} %`);
    });
    return base;
  }, [sortedSummaries]);

  const errorAlign: ("left" | "right")[] = useMemo(() => {
    const base: ("left" | "right")[] = ["left"];
    for (let i = 0; i < sortedSummaries.length; i++) {
      base.push("right", "right");
    }
    return base;
  }, [sortedSummaries]);

  // ── Evidence Audit data ──
  const evidenceRows = useMemo(() => {
    return sortedSummaries.map((s) => {
      const ev = computeEvidenceMetrics(s);
      return [
        s.runId,
        s.pipelineFamily,
        ev.exact,
        ev.valid,
        ev.repair,
        ev.unknownRate,
        Math.round(ev.avgEvidenceLen),
        s.rowCount,
      ];
    });
  }, [sortedSummaries]);

  // Cell truncation classes for tables with long run IDs
  const comparisonCellClasses = useMemo(() => {
    return comparisonRows.map(() => [
      "max-w-[200px] truncate", // Run ID
      "max-w-[160px] truncate", // Family
      "", // Split
      "", // Rows
      "", "", "", "", "", "", // metrics
    ]);
  }, [comparisonRows]);

  const evidenceCellClasses = useMemo(() => {
    return evidenceRows.map(() => [
      "max-w-[200px] truncate", // Run ID
      "max-w-[160px] truncate", // Family
      "", "", "", "", "", "", // metrics
    ]);
  }, [evidenceRows]);

  const evidenceHeaders = useMemo(() => [
    "Run ID",
    "Family",
    "Exact Evid",
    "Valid Evid",
    "Repair Rate",
    "Unknown Rate",
    "Avg Evid Len",
    "Rows",
  ], []);
  const evidenceAlign = useMemo<("left" | "right")[]>(() => [
    "left", "left", "right", "right", "right", "right", "right", "right",
  ], []);

  // ── Report sections for export panel ──
  const reportSections = useMemo(
    () => [
      { title: "Run Comparison", headers: comparisonHeaders, rows: comparisonRows, align: comparisonAlign },
      { title: "Per-Label Performance", headers: perLabelHeaders, rows: perLabelRows.map((r) => r.row), align: perLabelAlign },
      { title: "Error Taxonomy", headers: errorHeaders, rows: errorRows, align: errorAlign },
      { title: "Evidence Audit", headers: evidenceHeaders, rows: evidenceRows, align: evidenceAlign },
    ],
    [
      comparisonHeaders, comparisonRows, comparisonAlign,
      perLabelHeaders, perLabelRows, perLabelAlign,
      errorHeaders, errorRows, errorAlign,
      evidenceHeaders, evidenceRows, evidenceAlign,
    ]
  );

  if (registryLoading) {
    return (
      <div className="flex h-full items-center justify-center text-muted">
        <p className="text-sm font-medium">Loading registry…</p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col bg-background">
      {/* Tab bar */}
      <div className="flex items-center gap-1 border-b border-border px-5">
        <TabButton
          active={activeTab === "assembly"}
          onClick={() => setActiveTab("assembly")}
          icon={<FileText className="h-3.5 w-3.5" />}
          label="Report Assembly"
        />
        <TabButton
          active={activeTab === "comparison"}
          onClick={() => setActiveTab("comparison")}
          icon={<BarChart3 className="h-3.5 w-3.5" />}
          label="Run Comparison"
          badge={selectedSummaries.length > 0 ? `${selectedSummaries.length}` : undefined}
        />
        <TabButton
          active={activeTab === "perlabel"}
          onClick={() => setActiveTab("perlabel")}
          icon={<Grid3X3 className="h-3.5 w-3.5" />}
          label="Per-Label Performance"
        />
        <TabButton
          active={activeTab === "errors"}
          onClick={() => setActiveTab("errors")}
          icon={<AlertTriangle className="h-3.5 w-3.5" />}
          label="Error Taxonomy"
        />
        <TabButton
          active={activeTab === "evidence"}
          onClick={() => setActiveTab("evidence")}
          icon={<ShieldCheck className="h-3.5 w-3.5" />}
          label="Evidence Audit"
        />
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === "assembly" && (
          <div className="h-full overflow-y-auto p-5 max-w-[1400px] mx-auto space-y-5">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              <div className="lg:col-span-2 space-y-5">
                <ExportPanel
                  sections={reportSections}
                  runIds={Array.from(selectedRunIds)}
                  metadata={{
                    generatedAt: new Date().toISOString(),
                    url: typeof window !== "undefined" ? window.location.href : undefined,
                  }}
                />
                {selectedSummaries.length === 0 && (
                  <div className="rounded-lg border border-border bg-surface p-8 text-center">
                    <CheckCircle className="h-6 w-6 text-muted mx-auto mb-2" />
                    <p className="text-sm text-muted font-medium">No runs selected</p>
                    <p className="text-[11px] text-muted mt-1">
                      Select runs from the registry below to populate the report.
                    </p>
                  </div>
                )}
                {selectedSummaries.length > 0 && (
                  <>
                    <PaperTable
                      title="Run Comparison"
                      caption="Sorted by Purist F1 descending. Saturation warning: validation surfaces ≥250 rows with pragmatic accuracy ≥95% are low-information."
                      headers={comparisonHeaders}
                      rows={comparisonRows}
                      align={comparisonAlign}
                      cellClasses={comparisonCellClasses}
                      footer={`Selected runs: ${Array.from(selectedRunIds).join(", ")}. Total rows evaluated: ${selectedSummaries.reduce((s, r) => s + r.rowCount, 0)}.`}
                    />
                    <RunLegend summaries={sortedSummaries} />
                    <PaperTable
                      title="Error Taxonomy"
                      caption="Error classification uses purist category magnitude. Near miss = off by exactly one category bucket."
                      headers={errorHeaders}
                      rows={errorRows}
                      align={errorAlign}
                    />
                  </>
                )}
              </div>
              <div className="space-y-5">
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

        {activeTab === "comparison" && (
          <div className="h-full overflow-y-auto p-5 max-w-[1400px] mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              <div className="lg:col-span-2 space-y-5">
                <PaperTable
                  title="Run Comparison"
                  caption="Component ablation table. Generalisation gap shown when both validation and test metrics are available."
                  headers={comparisonHeaders}
                  rows={comparisonRows}
                  align={comparisonAlign}
                  cellClasses={comparisonCellClasses}
                  footer={`Runs: ${Array.from(selectedRunIds).join(", ") || "none selected"}`}
                />
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

        {activeTab === "perlabel" && (
          <div className="h-full overflow-y-auto p-5 max-w-[1400px] mx-auto space-y-5">
            <RunLegend summaries={sortedSummaries} />
            <PaperTable
              title="Per-Label Performance"
              caption="Purist categories. Precision, Recall, F1, Support per run. F1 colour: green ≥0.8, amber 0.5–0.8, red <0.5."
              headers={perLabelHeaders}
              rows={perLabelRows.map((r) => r.row)}
              align={perLabelAlign}
              cellClasses={perLabelRows.map((r) => r.cellCls)}
              footer={`Gold categories are derived from monthly frequency mapping. Support counts may differ across runs if splits differ.`}
            />
          </div>
        )}

        {activeTab === "errors" && (
          <div className="h-full overflow-y-auto p-5 max-w-[1400px] mx-auto space-y-5">
            <RunLegend summaries={sortedSummaries} />
            <PaperTable
              title="Error Taxonomy"
              caption="False negatives and false positives are the most clinically severe errors. Near misses are the easiest to fix."
              headers={errorHeaders}
              rows={errorRows}
              align={errorAlign}
              footer={`Error counts are computed from purist category comparisons.`}
            />
          </div>
        )}

        {activeTab === "evidence" && (
          <div className="h-full overflow-y-auto p-5 max-w-[1400px] mx-auto space-y-5">
            <PaperTable
              title="Evidence Audit"
              caption="Evidence metrics are approximations based on artifact row fields. Exact evidence requires source-note substring verification."
              headers={evidenceHeaders}
              rows={evidenceRows}
              align={evidenceAlign}
              cellClasses={evidenceCellClasses}
              footer={`Repair rate requires repair_changes field in artifact rows; shown as 0 when unavailable.`}
            />
          </div>
        )}
      </div>
    </div>
  );
}
