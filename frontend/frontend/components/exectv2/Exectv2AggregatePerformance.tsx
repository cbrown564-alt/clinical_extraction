"use client";

import { useMemo } from "react";
import { Check } from "lucide-react";
import { exectv2Dataset, EXECTV2_FAMILIES } from "@/lib/datasets";
import type { Exectv2Entity, Exectv2RunSummary } from "@/lib/types";
import {
  SurfaceHeader,
  SurfaceLayout,
  SurfaceLoading,
  SurfaceError,
  F1Cell,
  SurfaceLink,
  formatMetricValue,
} from "@/components/surface";
import { groupExectv2Runs } from "@/lib/exectv2RunOptions";
import {
  compactRunLabel,
  useExectv2Runs,
  useExectv2Selection,
} from "./useExectv2";
import { splitLabel as plainSplitLabel } from "@/lib/plainLanguageLabels";
import { Exectv2ModeBadge } from "./Exectv2ModeBadge";

const FAMILY_IDS = EXECTV2_FAMILIES.map((f) => f.id as Exectv2Entity);

/** Distinct split(s) present in a group, rendered with plain split names. */
function groupSplitLabel(runs: Exectv2RunSummary[]): string {
  const splits = Array.from(new Set(runs.map((r) => r.split))).sort();
  return splits.map((s) => plainSplitLabel(s)).join(" + ");
}

function SelectBox({ selected, indeterminate = false }: { selected: boolean; indeterminate?: boolean }) {
  return (
    <div
      className={`flex h-3.5 w-3.5 items-center justify-center rounded border transition-colors ${
        selected
          ? "border-deterministic bg-deterministic"
          : indeterminate
          ? "border-deterministic bg-surface"
          : "border-border bg-surface"
      }`}
    >
      {selected && <Check className="h-2.5 w-2.5 text-surface" strokeWidth={3} />}
      {!selected && indeterminate && <div className="h-1.5 w-1.5 rounded-sm bg-deterministic" />}
    </div>
  );
}

function RunGroup({
  title,
  caption,
  runs,
  selectedIds,
  onToggle,
  onToggleGroup,
}: {
  title: string;
  caption: string;
  runs: Exectv2RunSummary[];
  selectedIds: Set<string>;
  onToggle: (runId: string) => void;
  onToggleGroup: (runIds: string[], select: boolean) => void;
}) {
  if (runs.length === 0) return null;
  const allSelected = runs.every((r) => selectedIds.has(r.run_id));
  const someSelected = runs.some((r) => selectedIds.has(r.run_id));
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => onToggleGroup(runs.map((r) => r.run_id), !allSelected)}
          className="flex items-center"
          aria-label={`${allSelected ? "Deselect" : "Select"} ${title}`}
          aria-pressed={allSelected}
        >
          <SelectBox selected={allSelected} indeterminate={!allSelected && someSelected} />
        </button>
        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">{title}</h3>
        <span className="text-[11px] text-muted">{caption}</span>
      </div>
      <div className="overflow-x-auto rounded-md border border-border bg-surface">
        <table className="w-full border-collapse text-xs">
          <thead>
            <tr className="border-b border-border bg-surface-raised/60 text-[11px] uppercase tracking-wider text-muted">
              <th className="w-8 px-3 py-2" />
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
              const selected = selectedIds.has(run.run_id);
              return (
                <tr
                  key={run.run_id}
                  onClick={() => onToggle(run.run_id)}
                  className={`cursor-pointer border-b border-border/60 transition-colors last:border-b-0 ${
                    selected ? "bg-deterministic/8" : "hover:bg-surface-raised/50"
                  }`}
                >
                  <td className="px-3 py-2">
                    <button
                      type="button"
                      onClick={(event) => {
                        event.stopPropagation();
                        onToggle(run.run_id);
                      }}
                      className="flex items-center justify-center"
                      aria-label={`${selected ? "Deselect" : "Select"} ${compactRunLabel(run)}`}
                      aria-pressed={selected}
                    >
                      <SelectBox selected={selected} />
                    </button>
                  </td>
                  <td className="px-3 py-2">
                    <div className="flex items-center gap-2">
                      <Exectv2ModeBadge mode={run.comparison_mode} />
                      <div className="min-w-0">
                        <p className="truncate font-semibold text-foreground">{compactRunLabel(run)}</p>
                        <p className="truncate font-mono text-[11px] text-muted">{run.model}</p>
                      </div>
                    </div>
                  </td>
                  <F1Cell value={run.metrics.overall_f1} lead />
                  {FAMILY_IDS.map((family) => (
                    <F1Cell key={family} value={run.metrics.families[family]?.f1} />
                  ))}
                  <td className="px-2 py-2 text-right font-mono text-xs text-muted">
                    {formatMetricValue(run.operational.exact_evidence_rate, "rate")}
                  </td>
                  <td className={`px-2 py-2 text-right font-mono text-xs ${run.operational.call_failures > 0 ? "text-error" : "text-muted"}`}>
                    {run.operational.call_failures}
                  </td>
                  <td className={`px-2 py-2 text-right font-mono text-xs ${run.operational.parse_schema_failures > 0 ? "text-error" : "text-muted"}`}>
                    {run.operational.parse_schema_failures}
                  </td>
                  <td className="px-2 py-2 text-right font-mono text-xs text-muted">{run.row_count}</td>
                  <td className="px-3 py-2">
                    <div className="flex items-center gap-1.5" onClick={(e) => e.stopPropagation()}>
                      <SurfaceLink surface="workbench" datasetId="exectv2" params={{ run: run.run_id }} label="Explore" />
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
  const { selectedIds, selectedRunIds, toggle, setSelection } = useExectv2Selection(runs);

  const runGroups = useMemo(() => groupExectv2Runs(runs), [runs]);

  // The primary run drives the claim-boundary detail panel: first selected, in display order.
  const primaryRun = useMemo(
    () => runs.find((r) => selectedIds.has(r.run_id)) ?? runs[0],
    [runs, selectedIds]
  );

  const toggleGroup = (runIds: string[], select: boolean) => {
    const next = new Set(selectedIds);
    for (const id of runIds) {
      if (select) next.add(id);
      else next.delete(id);
    }
    setSelection([...next]);
  };

  if (isLoading) return <SurfaceLoading message="Loading aggregate performance…" />;
  if (error) return <SurfaceError title="ExECTv2 data failed to load" detail={String(error)} />;

  return (
    <SurfaceLayout
      variant="report"
      contentClassName="space-y-6"
      header={
        <SurfaceHeader
          surface="observatory"
          dataset={exectv2Dataset}
          description="Clinical mention F1 by family across the selected architecture set. Select architectures to compare; the set flows into the Error Gallery."
          right={
            <>
              <span className="rounded border border-border bg-surface-raised px-2 py-0.5 text-[11px] text-muted">
                {selectedRunIds.length} selected
              </span>
              <button
                type="button"
                onClick={() => setSelection(runs.map((r) => r.run_id))}
                className="text-[11px] font-medium text-muted transition-colors hover:text-foreground"
              >
                Select all
              </button>
              <button
                type="button"
                onClick={() => setSelection([])}
                className="text-[11px] font-medium text-muted transition-colors hover:text-foreground"
              >
                Clear
              </button>
              <SurfaceLink
                surface="gallery"
                datasetId="exectv2"
                params={{ runs: selectedRunIds.join(",") || undefined }}
                label={`Errors (${selectedRunIds.length})`}
              />
            </>
          }
        />
      }
    >
      {runGroups.map((group) => (
        <RunGroup
          key={group.mode}
          title={`${group.label} · ${groupSplitLabel(group.runs)}`}
          caption={group.caption}
          runs={group.runs}
          selectedIds={selectedIds}
          onToggle={toggle}
          onToggleGroup={toggleGroup}
        />
      ))}

      {primaryRun && (
        <section className="rounded-md border border-border bg-surface p-4">
          <div className="flex items-center gap-2">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">
              {compactRunLabel(primaryRun)} · claim boundary
            </h3>
            <SurfaceLink surface="workbench" datasetId="exectv2" params={{ run: primaryRun.run_id }} label="Explore" />
          </div>
          <p className="mt-2 text-xs leading-relaxed text-foreground">{primaryRun.claim_boundary}</p>
          <div className="mt-3 flex flex-wrap gap-2 text-[11px] text-muted">
            <span className="rounded border border-border bg-surface-raised px-2 py-1 font-mono">{primaryRun.architecture_family}</span>
            <span className="rounded border border-border bg-surface-raised px-2 py-1 font-mono">{primaryRun.scorer_view}</span>
            <span className="rounded border border-border bg-surface-raised px-2 py-1 font-mono">promotion: {primaryRun.promotion_decision}</span>
          </div>
        </section>
      )}
    </SurfaceLayout>
  );
}
