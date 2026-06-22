"use client";

import { useMemo } from "react";
import Link from "next/link";
import { BarChart3, ExternalLink, GalleryHorizontalEnd, ShieldAlert } from "lucide-react";
import { EXECTV2_FAMILIES, surfaceHref } from "@/lib/datasets";
import type { RunDecision } from "@/lib/datasets";
import type { Exectv2Entity, Exectv2RunSummary } from "@/lib/types";
import { compactRunLabel, formatMetric, useExectv2Runs, useExectv2UrlState } from "./useExectv2";

const FAMILY_IDS = EXECTV2_FAMILIES.map((f) => f.id as Exectv2Entity);

/** Distinct split prefix(es) present in a group, e.g. "dev140" or "dev25 + dev140". */
function splitLabel(runs: Exectv2RunSummary[]): string {
  return Array.from(new Set(runs.map((r) => r.split))).sort().join(" + ");
}

function decisionBadge(decision: string): string {
  switch (decision as RunDecision) {
    case "control":
      return "border-deterministic/25 bg-deterministic/10 text-deterministic";
    case "simplification":
      return "border-success/25 bg-success/10 text-success";
    case "diagnostic":
      return "border-llm/25 bg-llm/10 text-llm";
    default:
      return "border-muted/20 bg-muted/10 text-muted";
  }
}

/** F1 cell shaded by magnitude so weak families read at a glance. */
function F1Cell({ value, lead }: { value: number | null | undefined; lead?: boolean }) {
  const tone =
    typeof value !== "number"
      ? "text-muted"
      : value >= 0.9
      ? "text-success"
      : value >= 0.8
      ? "text-foreground"
      : "text-error";
  return (
    <td className={`px-2 py-2 text-right font-mono text-[11px] ${tone} ${lead ? "font-semibold" : ""}`}>
      {formatMetric(value, 3)}
    </td>
  );
}

function RunGroup({
  title,
  caption,
  runs,
  activeRunId,
  onSelect,
}: {
  title: string;
  caption: string;
  runs: Exectv2RunSummary[];
  activeRunId: string | undefined;
  onSelect: (runId: string) => void;
}) {
  if (runs.length === 0) return null;
  return (
    <div className="space-y-2">
      <div className="flex items-baseline gap-2">
        <h3 className="text-[11px] font-semibold uppercase tracking-wider text-muted">{title}</h3>
        <span className="text-[10px] text-muted">{caption}</span>
      </div>
      <div className="overflow-x-auto rounded-md border border-border bg-surface">
        <table className="w-full border-collapse text-[11px]">
          <thead>
            <tr className="border-b border-border bg-surface-raised/60 text-[10px] uppercase tracking-wider text-muted">
              <th className="px-3 py-2 text-left font-semibold">Architecture</th>
              <th className="px-2 py-2 text-right font-semibold">Overall</th>
              {FAMILY_IDS.map((family) => (
                <th key={family} className="px-2 py-2 text-right font-semibold">
                  {EXECTV2_FAMILIES.find((f) => f.id === family)?.shortLabel}
                </th>
              ))}
              <th className="px-2 py-2 text-right font-semibold">Evidence</th>
              <th className="px-2 py-2 text-right font-semibold">Calls</th>
              <th className="px-2 py-2 text-right font-semibold">Parse</th>
              <th className="px-2 py-2 text-right font-semibold">Rows</th>
              <th className="px-3 py-2 text-left font-semibold">Links</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => {
              const active = run.run_id === activeRunId;
              return (
                <tr
                  key={run.run_id}
                  onClick={() => onSelect(run.run_id)}
                  className={`cursor-pointer border-b border-border/60 transition-colors last:border-b-0 ${
                    active ? "bg-deterministic/8" : "hover:bg-surface-raised/50"
                  }`}
                >
                  <td className="px-3 py-2">
                    <div className="flex items-center gap-2">
                      <span className={`shrink-0 rounded border px-1.5 py-0.5 text-[9px] font-medium ${decisionBadge(run.decision)}`}>
                        {run.decision}
                      </span>
                      <div className="min-w-0">
                        <p className="truncate font-semibold text-foreground">{compactRunLabel(run)}</p>
                        <p className="truncate font-mono text-[9px] text-muted">{run.model}</p>
                      </div>
                    </div>
                  </td>
                  <F1Cell value={run.metrics.overall_f1} lead />
                  {FAMILY_IDS.map((family) => (
                    <F1Cell key={family} value={run.metrics.families[family]?.f1} />
                  ))}
                  <td className="px-2 py-2 text-right font-mono text-[11px] text-muted">
                    {formatMetric(run.operational.exact_evidence_rate, 2)}
                  </td>
                  <td className={`px-2 py-2 text-right font-mono text-[11px] ${run.operational.call_failures > 0 ? "text-error" : "text-muted"}`}>
                    {run.operational.call_failures}
                  </td>
                  <td className={`px-2 py-2 text-right font-mono text-[11px] ${run.operational.parse_schema_failures > 0 ? "text-error" : "text-muted"}`}>
                    {run.operational.parse_schema_failures}
                  </td>
                  <td className="px-2 py-2 text-right font-mono text-[11px] text-muted">{run.row_count}</td>
                  <td className="px-3 py-2">
                    <div className="flex items-center gap-1.5">
                      <Link
                        href={surfaceHref("workbench", "exectv2", { run: run.run_id })}
                        className="inline-flex items-center gap-1 rounded border border-deterministic/20 bg-deterministic/5 px-1.5 py-0.5 text-[9px] font-medium text-deterministic hover:bg-deterministic/10"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <ExternalLink className="h-2.5 w-2.5" /> Explore
                      </Link>
                      <Link
                        href={surfaceHref("gallery", "exectv2", { run: run.run_id })}
                        className="inline-flex items-center gap-1 rounded border border-error/20 bg-error/5 px-1.5 py-0.5 text-[9px] font-medium text-error hover:bg-error/10"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <GalleryHorizontalEnd className="h-2.5 w-2.5" /> Errors
                      </Link>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function Exectv2AggregatePerformance() {
  const { runs, isLoading, error } = useExectv2Runs();
  const { get, set } = useExectv2UrlState();
  const activeRunId = get("run");

  const { controls, diagnostics } = useMemo(() => {
    const controls = runs.filter((r) => r.decision === "control" || r.decision === "simplification");
    const diagnostics = runs.filter((r) => r.decision === "diagnostic" || r.decision === "pending" || r.decision === "superseded");
    return { controls, diagnostics };
  }, [runs]);

  const selectedRun = useMemo(() => runs.find((r) => r.run_id === activeRunId) ?? controls[0] ?? runs[0], [runs, activeRunId, controls]);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center bg-background text-muted">
        <p className="text-sm font-medium">Loading aggregate performance…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full items-center justify-center bg-background p-8">
        <div className="max-w-md rounded-md border border-error/25 bg-error/8 p-5">
          <div className="flex items-center gap-2 text-error">
            <ShieldAlert className="h-4 w-4" />
            <p className="text-sm font-semibold">ExECTv2 data failed to load</p>
          </div>
          <p className="mt-2 text-xs text-muted">{String(error)}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col overflow-y-auto bg-background">
      <header className="border-b border-border bg-surface px-5 py-3">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-4 w-4 text-llm" />
          <h1 className="text-sm font-semibold text-foreground">ExECTv2 · Aggregate Performance</h1>
        </div>
        <p className="mt-1 text-[11px] text-muted">
          Clinical mention F1 by family across the selected architecture set. Controls are
          separated from diagnostics; diagnostics are not promoted replacements.
        </p>
      </header>

      <div className="mx-auto w-full max-w-[1200px] space-y-6 p-5">
        <RunGroup
          title={`${splitLabel(controls)} controls`}
          caption="performance & simplicity controls (claimable boundary)"
          runs={controls}
          activeRunId={selectedRun?.run_id}
          onSelect={(runId) => set({ run: runId })}
        />
        <RunGroup
          title={`${splitLabel(diagnostics)} diagnostics`}
          caption="cross-model comparators — diagnostic only, not promoted"
          runs={diagnostics}
          activeRunId={selectedRun?.run_id}
          onSelect={(runId) => set({ run: runId })}
        />

        {selectedRun && (
          <section className="rounded-md border border-border bg-surface p-4">
            <h3 className="text-[11px] font-semibold uppercase tracking-wider text-muted">
              {compactRunLabel(selectedRun)} · claim boundary
            </h3>
            <p className="mt-2 text-[12px] leading-relaxed text-foreground">{selectedRun.claim_boundary}</p>
            <div className="mt-3 flex flex-wrap gap-2 text-[10px] text-muted">
              <span className="rounded border border-border bg-surface-raised px-2 py-1 font-mono">{selectedRun.architecture_family}</span>
              <span className="rounded border border-border bg-surface-raised px-2 py-1 font-mono">{selectedRun.scorer_view}</span>
              <span className="rounded border border-border bg-surface-raised px-2 py-1 font-mono">promotion: {selectedRun.promotion_decision}</span>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
