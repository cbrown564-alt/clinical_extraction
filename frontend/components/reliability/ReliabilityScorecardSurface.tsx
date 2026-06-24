"use client";

import { useMemo, useState } from "react";
import { AlertTriangle, FileText, ShieldCheck } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { fetchReliabilityScorecard } from "@/lib/api";
import {
  EXECTV2_FAMILIES,
  TONE_CLASSES,
  useActiveDataset,
  getDataset,
  type DatasetTone,
} from "@/lib/datasets";
import type { ReliabilityScorecardDimension } from "@/lib/types";
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
      className={`rounded-md border px-2 py-1 text-[10px] font-medium transition-colors ${
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
    <div className="overflow-hidden rounded-md border border-border bg-surface">
      <table className="w-full border-collapse text-[11px]">
        <thead>
          <tr className="border-b border-border bg-surface-raised/60 text-[10px] uppercase tracking-wider text-muted">
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
                  <span className={`rounded border px-1.5 py-0.5 font-mono text-[10px] ${STRENGTH_CLASSES[strength]}`}>
                    {coverageLabel(dimension)}
                  </span>
                </td>
                <td className="px-3 py-3 align-top">
                  <div className="font-semibold text-foreground">{dimension.dimension}</div>
                  <div className="mt-1 font-mono text-[9px] text-muted">{dimension.id}</div>
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
          <section className="grid grid-cols-1 gap-3 md:grid-cols-3">
            <div className="rounded-md border border-border bg-surface p-4">
              <div className="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-wider text-muted">
                <ShieldCheck className="h-3.5 w-3.5" />
                Mean coverage
              </div>
              <div className="mt-2 text-2xl font-semibold text-foreground">
                {formatMetricValue(meanCoverage, "rate", { asPercent: true, digits: 0 })}
              </div>
            </div>
            <div className="rounded-md border border-error/25 bg-error/[0.03] p-4">
              <div className="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-wider text-muted">
                <AlertTriangle className="h-3.5 w-3.5 text-error" />
                Weak dimensions
              </div>
              <div className="mt-2 text-2xl font-semibold text-error">
                {payload.weak_dimensions.length}
              </div>
            </div>
            <div className="rounded-md border border-border bg-surface p-4">
              <div className="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-wider text-muted">
                <FileText className="h-3.5 w-3.5" />
                Source
              </div>
              <div className="mt-2 space-y-1 font-mono text-[10px] leading-snug text-muted">
                <p>{payload.source_scorecard}</p>
                {payload.source_cross_model_report && <p>{payload.source_cross_model_report}</p>}
              </div>
            </div>
          </section>

          <section className="overflow-hidden rounded-md border border-border bg-surface">
            <div className="border-b border-border px-4 py-3">
              <h2 className="text-[11px] font-semibold uppercase tracking-wider text-muted">
                Evidence Set
              </h2>
            </div>
            <table className="w-full border-collapse text-[11px]">
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

          <div className="flex flex-wrap items-center gap-2">
            <FilterButton active={filter === "all"} label="All dimensions" onClick={() => setFilter("all")} />
            <FilterButton active={filter === "weak"} label="Weak only" onClick={() => setFilter("weak")} />
            <FilterButton active={filter === "strong"} label="Strong only" onClick={() => setFilter("strong")} />
          </div>

          <DimensionRows dimensions={dimensions} />

          <section className="grid grid-cols-1 gap-4 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="rounded-md border border-border bg-surface p-4">
              <h2 className="text-[11px] font-semibold uppercase tracking-wider text-muted">
                Residual Risks
              </h2>
              <div className="mt-3 space-y-3">
                {payload.residual_risks.map((risk) => (
                  <div key={risk.family} className="border-b border-border/60 pb-3 last:border-b-0 last:pb-0">
                    <span className={`rounded border px-1.5 py-0.5 text-[10px] font-medium ${TONE_CLASSES[familyTone(risk.family)]}`}>
                      {risk.family}
                    </span>
                    <p className="mt-2 text-[11px] leading-relaxed text-foreground">{risk.current_strength}</p>
                    <p className="mt-1 text-[11px] leading-relaxed text-muted">{risk.residual_risk}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-md border border-border bg-surface p-4">
              <h2 className="text-[11px] font-semibold uppercase tracking-wider text-muted">
                Upgrade Metrics
              </h2>
              <div className="mt-3 space-y-3">
                {payload.upgrade_plan.map((item) => (
                  <div key={`${item.dimension}:${item.next_metric_needed}`} className="border-b border-border/60 pb-3 last:border-b-0 last:pb-0">
                    <p className="text-[11px] font-semibold text-foreground">{item.dimension}</p>
                    <p className="mt-1 text-[11px] leading-relaxed text-muted">{item.next_metric_needed}</p>
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

