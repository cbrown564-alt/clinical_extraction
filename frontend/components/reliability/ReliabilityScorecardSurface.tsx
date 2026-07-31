"use client";

import { useMemo, useState } from "react";
import { AlertTriangle } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { fetchReliabilityScorecard } from "@/lib/api";
import {
  EXECTV2_FAMILIES,
  TONE_CLASSES,
  useActiveDataset,
  getDataset,
  type DatasetTone,
} from "@/lib/datasets";
import type {
  Exectv2ComputedReliability,
  ReliabilityScorecardDimension,
} from "@/lib/types";
import {
  SurfaceHeader,
  SurfaceLayout,
  SurfaceLoading,
  SurfaceError,
  SurfaceLink,
  formatMetricValue,
} from "@/components/surface";

type DimensionFilter = "all" | "weak" | "strong";

const STRENGTH_CLASSES: Record<string, string> = {
  strong: "border-success/25 bg-success/10 text-success",
  medium: "border-deterministic-alt/25 bg-deterministic-alt/10 text-deterministic-alt",
  weak: "border-error/25 bg-error/10 text-error",
  unknown: "border-muted/20 bg-muted/10 text-muted",
};

function coverageLabel(dimension: ReliabilityScorecardDimension): string {
  if (typeof dimension.coverage !== "number" || typeof dimension.coverage_max !== "number") {
    return "not scored";
  }
  return `${dimension.coverage}/${dimension.coverage_max}`;
}

function FilterButton({
  active,
  label,
  onClick,
}: {
  active: boolean;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-md border px-2 py-1 text-[11px] font-medium transition-colors ${
        active
          ? "border-foreground/25 bg-surface-raised text-foreground"
          : "border-border text-muted hover:bg-surface-raised"
      }`}
    >
      {label}
    </button>
  );
}

function DimensionRows({ dimensions }: { dimensions: ReliabilityScorecardDimension[] }) {
  return (
    <div className="overflow-x-auto rounded-md border border-border bg-surface">
      <table className="w-full border-collapse text-xs">
        <thead>
          <tr className="border-b border-border bg-surface-raised/60 text-[11px] uppercase tracking-wider text-muted">
            <th className="w-14 px-3 py-2 text-left font-semibold">Score</th>
            <th className="w-52 px-3 py-2 text-left font-semibold">Dimension</th>
            <th className="px-3 py-2 text-left font-semibold">Current evidence</th>
            <th className="px-3 py-2 text-left font-semibold">Gap to close</th>
          </tr>
        </thead>
        <tbody>
          {dimensions.map((dimension) => {
            const strength = dimension.strength ?? "unknown";
            return (
              <tr key={dimension.id} className="border-b border-border/60 last:border-b-0">
                <td className="px-3 py-3 align-top">
                  <span className={`rounded border px-1.5 py-0.5 font-mono text-[11px] ${STRENGTH_CLASSES[strength]}`}>
                    {coverageLabel(dimension)}
                  </span>
                </td>
                <td className="px-3 py-3 align-top">
                  <div className="font-semibold text-foreground">{dimension.dimension}</div>
                  <div className="mt-1 font-mono text-[11px] text-muted">{dimension.id}</div>
                </td>
                <td className="px-3 py-3 align-top leading-relaxed text-foreground">
                  {dimension.current_evidence}
                </td>
                <td className="px-3 py-3 align-top leading-relaxed text-muted">
                  {dimension.gap_to_close}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function familyTone(family: string): DatasetTone {
  if (family === "SeizureFrequency") return "llm";
  return EXECTV2_FAMILIES.find((item) => item.id === family)?.tone ?? "muted";
}

function ComputedReliabilityPanel({
  computed,
}: {
  computed?: Exectv2ComputedReliability;
}) {
  if (!computed) return null;

  const agreement = computed.cross_model_agreement.overall;
  const calibration = computed.calibration_proxy;
  const routing = computed.review_routing;
  const operatingPoints = routing.operating_points;

  // Derive the set of non-GPT comparison models from the registry/catalog-driven
  // latest_run_check surfaces rather than hardcoding model names. The active
  // LLM-only transfer rows are filtered to exactly those surfaced models.
  const surfacedModels = new Set(
    computed.latest_run_check.surfaces.flatMap((surface) =>
      surface.latest_runs.map((run) => run.model_label)
    )
  );
  const activeRows = computed.active_llm_only_readout.filter((row) =>
    surfacedModels.has(row.model_label)
  );

  // Stable column order: distinct model_labels in order of first appearance
  // across all surfaces.
  const modelColumns = computed.latest_run_check.surfaces.flatMap((surface) =>
    surface.latest_runs.map((run) => run.model_label)
  );
  const seenModels = new Set<string>();
  const orderedModels: string[] = [];
  for (const label of modelColumns) {
    if (!seenModels.has(label)) {
      seenModels.add(label);
      orderedModels.push(label);
    }
  }

  return (
    <section className="space-y-3">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        <div className="rounded-md border border-border bg-surface p-4">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-muted">
            Agreement
          </p>
          <p className="mt-2 font-mono text-xl font-semibold text-foreground">
            {formatMetricValue(agreement.mean_pairwise_jaccard, "rate", {
              asPercent: true,
              digits: 0,
            })}
          </p>
          <p className="mt-1 text-[11px] text-muted">{agreement.cell_count} cells</p>
        </div>
        <div className="rounded-md border border-border bg-surface p-4">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-muted">
            Exact Cells
          </p>
          <p className="mt-2 font-mono text-xl font-semibold text-foreground">
            {formatMetricValue(agreement.exact_cell_agreement_rate, "rate", {
              asPercent: true,
              digits: 0,
            })}
          </p>
          <p className="mt-1 text-[11px] text-muted">{agreement.pair_count} pairs</p>
        </div>
        <div className="rounded-md border border-border bg-surface p-4">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-muted">
            Review Catch
          </p>
          <p className="mt-2 font-mono text-xl font-semibold text-foreground">
            {formatMetricValue(routing.catch_rate, "rate", { asPercent: true, digits: 0 })}
          </p>
          <p className="mt-1 text-[11px] text-muted">
            {routing.caught_error_cells}/{routing.total_error_cells} error cells
          </p>
        </div>
        <div className="rounded-md border border-border bg-surface p-4">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-muted">
            Calibration ECE
          </p>
          <p className="mt-2 font-mono text-xl font-semibold text-foreground">
            {formatMetricValue(calibration.expected_calibration_error, "f1")}
          </p>
          <p className="mt-1 text-[11px] text-muted">
            {calibration.bin_count} bins / {calibration.cell_count} cells
          </p>
        </div>
        <div className="rounded-md border border-border bg-surface p-4">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-muted">
            Brier Score
          </p>
          <p className="mt-2 font-mono text-xl font-semibold text-foreground">
            {formatMetricValue(calibration.brier_score ?? null, "f1")}
          </p>
          <p className="mt-1 text-[11px] text-muted">
            base {formatMetricValue(calibration.constant_base_rate_brier_score ?? null, "f1")}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
        <div className="overflow-x-auto rounded-md border border-border bg-surface">
          <div className="border-b border-border px-4 py-3">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">
              Calibration Reliability Bins
            </h2>
          </div>
          <table className="w-full border-collapse text-xs">
            <thead>
              <tr className="border-b border-border bg-surface-raised/60 text-[11px] uppercase tracking-wider text-muted">
                <th className="px-3 py-2 text-left font-semibold">Bin</th>
                <th className="px-3 py-2 text-right font-semibold">Cells</th>
                <th className="px-3 py-2 text-right font-semibold">Confidence</th>
                <th className="px-3 py-2 text-right font-semibold">Accuracy</th>
                <th className="px-3 py-2 text-right font-semibold">Gap</th>
              </tr>
            </thead>
            <tbody>
              {calibration.bins.map((bin) => (
                <tr key={bin.bin} className="border-b border-border/60 last:border-b-0">
                  <td className="px-3 py-2 font-mono text-foreground">{bin.bin}</td>
                  <td className="px-3 py-2 text-right font-mono text-muted">{bin.cells}</td>
                  <td className="px-3 py-2 text-right font-mono text-foreground">
                    {formatMetricValue(
                      bin.avg_calibrated_confidence ?? bin.avg_confidence_proxy,
                      "f1"
                    )}
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-foreground">
                    {formatMetricValue(bin.accuracy, "f1")}
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-muted">
                    {formatMetricValue(bin.calibration_gap ?? null, "f1")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="overflow-x-auto rounded-md border border-border bg-surface">
          <div className="border-b border-border px-4 py-3">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">
              Per-Family Calibration
            </h2>
          </div>
          <table className="w-full border-collapse text-xs">
            <thead>
              <tr className="border-b border-border bg-surface-raised/60 text-[11px] uppercase tracking-wider text-muted">
                <th className="px-3 py-2 text-left font-semibold">Family</th>
                <th className="px-3 py-2 text-right font-semibold">ECE</th>
                <th className="px-3 py-2 text-right font-semibold">Brier</th>
                <th className="px-3 py-2 text-right font-semibold">Accuracy</th>
                <th className="px-3 py-2 text-right font-semibold">Cells</th>
              </tr>
            </thead>
            <tbody>
              {(calibration.per_family ?? []).map((row) => (
                <tr key={row.family} className="border-b border-border/60 last:border-b-0">
                  <td className="px-3 py-2 font-medium text-foreground">{row.family}</td>
                  <td className="px-3 py-2 text-right font-mono text-foreground">
                    {formatMetricValue(row.expected_calibration_error, "f1")}
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-foreground">
                    {formatMetricValue(row.brier_score, "f1")}
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-muted">
                    {formatMetricValue(row.accuracy, "rate", { asPercent: true, digits: 1 })}
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-muted">{row.cells}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="overflow-x-auto rounded-md border border-border bg-surface">
        <div className="border-b border-border px-4 py-3">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">
            Review Routing Operating Points
          </h2>
        </div>
        <table className="w-full border-collapse text-xs">
          <thead>
            <tr className="border-b border-border bg-surface-raised/60 text-[11px] uppercase tracking-wider text-muted">
              <th className="px-3 py-2 text-left font-semibold">Route</th>
              <th className="px-3 py-2 text-right font-semibold">Burden</th>
              <th className="px-3 py-2 text-right font-semibold">Catch</th>
              <th className="px-3 py-2 text-right font-semibold">False alarm</th>
              <th className="px-3 py-2 text-right font-semibold">Burden delta</th>
              <th className="px-3 py-2 text-left font-semibold">Status</th>
            </tr>
          </thead>
          <tbody>
            {operatingPoints.map((point) => (
              <tr key={point.id} className="border-b border-border/60 last:border-b-0">
                <td className="max-w-[18rem] px-3 py-2 align-top">
                  <div className="font-medium text-foreground">{point.label}</div>
                  <div className="mt-1 font-mono text-[11px] leading-snug text-muted">
                    {point.rules.join(" + ")}
                  </div>
                </td>
                <td className="px-3 py-2 text-right align-top font-mono text-foreground">
                  {formatMetricValue(point.review_burden, "rate", {
                    asPercent: true,
                    digits: 1,
                  })}
                </td>
                <td className="px-3 py-2 text-right align-top font-mono text-foreground">
                  {formatMetricValue(point.catch_rate, "rate", {
                    asPercent: true,
                    digits: 1,
                  })}
                </td>
                <td className="px-3 py-2 text-right align-top font-mono text-muted">
                  {formatMetricValue(point.false_alarm_rate, "rate", {
                    asPercent: true,
                    digits: 1,
                  })}
                </td>
                <td className="px-3 py-2 text-right align-top font-mono text-muted">
                  {formatMetricValue(point.review_burden_delta_vs_high_recall, "rate", {
                    asPercent: true,
                    digits: 1,
                  })}
                </td>
                <td className="max-w-[14rem] px-3 py-2 align-top text-muted">
                  {point.validation_status}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="overflow-x-auto rounded-md border border-border bg-surface">
        <div className="border-b border-border px-4 py-3">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">
            Latest Model Check
          </h2>
        </div>
        <table className="w-full border-collapse text-xs">
          <thead>
            <tr className="border-b border-border bg-surface-raised/60 text-[11px] uppercase tracking-wider text-muted">
              <th className="px-3 py-2 text-left font-semibold">Surface</th>
              {orderedModels.map((label) => (
                <th key={label} className="px-3 py-2 text-left font-semibold">
                  {label}
                </th>
              ))}
              <th className="px-3 py-2 text-left font-semibold">Policy</th>
            </tr>
          </thead>
          <tbody>
            {computed.latest_run_check.surfaces.map((surface) => (
              <tr key={surface.surface_id} className="border-b border-border/60 last:border-b-0">
                <td className="px-3 py-2 font-medium text-foreground">
                  {surface.surface_label}
                </td>
                {orderedModels.map((label) => {
                  const run = surface.latest_runs.find((r) => r.model_label === label);
                  return (
                    <td key={label} className="px-3 py-2 font-mono text-muted">
                      {run ? run.candidate : "–"}
                    </td>
                  );
                })}
                <td className="px-3 py-2 text-muted">{surface.replacement_policy}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="overflow-x-auto rounded-md border border-border bg-surface">
        <div className="border-b border-border px-4 py-3">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">
            Active LLM-Only Transfer Rows
          </h2>
        </div>
        <table className="w-full border-collapse text-xs">
          <thead>
            <tr className="border-b border-border bg-surface-raised/60 text-[11px] uppercase tracking-wider text-muted">
              <th className="px-3 py-2 text-left font-semibold">Model</th>
              <th className="px-3 py-2 text-right font-semibold">Clinical F1</th>
              <th className="px-3 py-2 text-right font-semibold">Strict F1</th>
              <th className="px-3 py-2 text-right font-semibold">Evidence</th>
              <th className="px-3 py-2 text-left font-semibold">Artifact</th>
            </tr>
          </thead>
          <tbody>
            {activeRows.map((row) => (
              <tr key={row.candidate} className="border-b border-border/60 last:border-b-0">
                <td className="px-3 py-2 font-medium text-foreground">{row.model_label}</td>
                <td className="px-3 py-2 text-right font-mono text-foreground">
                  {formatMetricValue(row.clinical_headline_f1, "f1")}
                </td>
                <td className="px-3 py-2 text-right font-mono text-muted">
                  {formatMetricValue(row.strict_benchmark_f1, "f1")}
                </td>
                <td className="px-3 py-2 text-right font-mono text-muted">
                  {formatMetricValue(row.evidence_validity, "rate", {
                    asPercent: true,
                    digits: 1,
                  })}
                </td>
                <td className="max-w-[24rem] px-3 py-2 font-mono text-[11px] text-muted">
                  {row.rows_path}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default function ReliabilityScorecardSurface() {
  const datasetId = useActiveDataset();
  const dataset = getDataset(datasetId);
  const [filter, setFilter] = useState<DimensionFilter>("all");
  const query = useQuery({
    queryKey: ["reliability-scorecard", datasetId],
    queryFn: () => fetchReliabilityScorecard(datasetId),
    staleTime: 5 * 60 * 1000,
  });

  const payload = query.data;
  const dimensions = useMemo(() => {
    const list = payload?.dimensions ?? [];
    if (filter === "weak") return list.filter((d) => d.strength === "weak");
    if (filter === "strong") return list.filter((d) => d.strength === "strong");
    return list;
  }, [filter, payload?.dimensions]);

  const meanCoverage = useMemo(() => {
    const scored = (payload?.dimensions ?? []).filter(
      (d) => typeof d.coverage === "number" && typeof d.coverage_max === "number"
    );
    if (scored.length === 0) return null;
    const total = scored.reduce((sum, d) => sum + (d.coverage ?? 0) / (d.coverage_max || 1), 0);
    return total / scored.length;
  }, [payload?.dimensions]);

  if (query.isLoading) return <SurfaceLoading message="Loading reliability scorecard..." />;
  if (query.error) {
    return <SurfaceError title="Reliability scorecard failed to load" detail={String(query.error)} />;
  }

  return (
    <SurfaceLayout
      variant="report"
      maxWidth={1180}
      contentClassName="space-y-5"
      header={
        <SurfaceHeader
          surface="reliability"
          dataset={dataset}
          description="Reliability dimensions, evidence strength, and missing metrics for the selected dataset."
          right={
            <>
              <SurfaceLink surface="observatory" datasetId={datasetId} label="Runs" />
              <SurfaceLink surface="laboratory" datasetId={datasetId} label="Component Impact" />
            </>
          }
        />
      }
    >
      {payload && (
        <>
          <section aria-label="Reliability summary" className="grid overflow-hidden rounded-md border border-border bg-surface md:grid-cols-[0.7fr_0.7fr_1.6fr] md:divide-x md:divide-border">
            <div className="border-b border-border p-3 md:border-b-0">
              <div className="text-[11px] font-semibold uppercase tracking-wider text-muted">
                Mean coverage
              </div>
              <div className="mt-1 text-lg font-semibold text-foreground">
                {formatMetricValue(meanCoverage, "rate", { asPercent: true, digits: 0 })}
              </div>
            </div>
            <div className="border-b border-border bg-error/[0.03] p-3 md:border-b-0">
              <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-wider text-muted">
                <AlertTriangle className="h-3.5 w-3.5 text-error" />
                Weak dimensions
              </div>
              <div className="mt-1 text-lg font-semibold text-error">
                {payload.weak_dimensions.length}
              </div>
            </div>
            <div className="p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wider text-muted">Source</div>
              <div className="mt-1 space-y-1 font-mono text-[11px] leading-snug text-muted">
                <p>{payload.source_scorecard}</p>
                {payload.source_cross_model_report && <p>{payload.source_cross_model_report}</p>}
              </div>
            </div>
          </section>

          <section className="overflow-x-auto rounded-md border border-border bg-surface">
            <div className="border-b border-border px-4 py-3">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">
                Evidence Set
              </h2>
            </div>
            <table className="w-full border-collapse text-xs">
              <tbody>
                {payload.evidence_set.map((row) => (
                  <tr key={`${row.role}:${row.candidate}`} className="border-b border-border/60 last:border-b-0">
                    <td className="px-3 py-2 font-medium text-foreground">{row.role}</td>
                    <td className="px-3 py-2 font-mono text-muted">{row.candidate}</td>
                    <td className="px-3 py-2 text-muted">{row.surface}</td>
                    <td className="px-3 py-2 text-right font-mono text-success">
                      {formatMetricValue(row.overall_f1, "f1")}
                    </td>
                    <td className="px-3 py-2 text-muted">{row.decision}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          <ComputedReliabilityPanel computed={payload.computed_reliability} />

          <div className="flex flex-wrap items-center gap-2">
            <FilterButton active={filter === "all"} label="All dimensions" onClick={() => setFilter("all")} />
            <FilterButton active={filter === "weak"} label="Weak only" onClick={() => setFilter("weak")} />
            <FilterButton active={filter === "strong"} label="Strong only" onClick={() => setFilter("strong")} />
          </div>

          <DimensionRows dimensions={dimensions} />

          <section className="grid grid-cols-1 gap-4 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="rounded-md border border-border bg-surface p-4">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">
                Residual Risks
              </h2>
              <div className="mt-3 space-y-3">
                {payload.residual_risks.map((risk) => (
                  <div key={risk.family} className="border-b border-border/60 pb-3 last:border-b-0 last:pb-0">
                    <span className={`rounded border px-1.5 py-0.5 text-[11px] font-medium ${TONE_CLASSES[familyTone(risk.family)]}`}>
                      {risk.family}
                    </span>
                    <p className="mt-2 text-xs leading-relaxed text-foreground">{risk.current_strength}</p>
                    <p className="mt-1 text-xs leading-relaxed text-muted">{risk.residual_risk}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-md border border-border bg-surface p-4">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">
                Upgrade Metrics
              </h2>
              <div className="mt-3 space-y-3">
                {payload.upgrade_plan.map((item) => (
                  <div key={`${item.dimension}:${item.next_metric_needed}`} className="border-b border-border/60 pb-3 last:border-b-0 last:pb-0">
                    <p className="text-xs font-semibold text-foreground">{item.dimension}</p>
                    <p className="mt-1 text-xs leading-relaxed text-muted">{item.next_metric_needed}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </>
      )}
    </SurfaceLayout>
  );
}
