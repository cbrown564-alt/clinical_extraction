"use client";

import { useMemo, useState } from "react";
import { Loader2, Play, SlidersHorizontal } from "lucide-react";
import { runAblation } from "@/lib/api";
import { useRules } from "@/lib/hooks";
import { gan2026Dataset } from "@/lib/datasets";
import type { RunAblationResponse } from "@/lib/types";
import {
  SurfaceHeader,
  SurfaceLayout,
  SurfaceLoading,
  SurfaceError,
  SurfaceLink,
  formatMetricValue,
} from "@/components/surface";

interface AblationPreset {
  id: string;
  label: string;
  group: string;
  description: string;
}

function presetLabel(group: string): string {
  if (group.includes("rate")) return "Rate extraction";
  if (group.includes("temporal")) return "Temporal selection";
  if (group.includes("seizure_free")) return "Seizure-free handling";
  if (group.includes("cluster")) return "Cluster interpretation";
  if (group.includes("diary")) return "Diary/shorthand parsing";
  if (group.includes("repair")) return "Benchmark repair";
  return group.replace(/_/g, " ");
}

function presetDescription(group: string): string {
  if (group.includes("rate")) return "Removes direct count/rate expression rules.";
  if (group.includes("temporal")) return "Removes recency and current-state selection rules.";
  if (group.includes("seizure_free")) return "Removes seizure-free and no-current-seizure handling.";
  if (group.includes("cluster")) return "Removes cluster/episode interpretation rules.";
  if (group.includes("diary")) return "Removes diary and shorthand frequency parsing.";
  if (group.includes("repair")) return "Removes post-processing benchmark repair rules.";
  return "Removes this deterministic rule group from the rules-only pipeline.";
}

function sortPriority(group: string): number {
  if (group.includes("rate")) return 0;
  if (group.includes("temporal")) return 1;
  if (group.includes("seizure_free")) return 2;
  if (group.includes("cluster")) return 3;
  if (group.includes("diary")) return 4;
  if (group.includes("repair")) return 5;
  return 10;
}

function buildPresets(groups: string[]): AblationPreset[] {
  return groups
    .map((group) => ({
      id: group,
      group,
      label: presetLabel(group),
      description: presetDescription(group),
    }))
    .sort((a, b) => sortPriority(a.group) - sortPriority(b.group) || a.label.localeCompare(b.label));
}

function deltaLabel(value: number | null): string {
  if (value === null || Number.isNaN(value)) return "-";
  return `${value >= 0 ? "+" : ""}${value.toFixed(3)}`;
}

function metricDelta(
  baseline: RunAblationResponse | null,
  ablated: RunAblationResponse | null,
  metric: "accuracy" | "f1"
): number | null {
  if (!baseline || !ablated) return null;
  return ablated.summary.purist[metric] - baseline.summary.purist[metric];
}

function ImpactSummary({
  baseline,
  ablated,
}: {
  baseline: RunAblationResponse | null;
  ablated: RunAblationResponse | null;
}) {
  const f1Delta = metricDelta(baseline, ablated, "f1");
  const accDelta = metricDelta(baseline, ablated, "accuracy");
  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
      <div className="rounded-md border border-border bg-surface p-4">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">Baseline F1</div>
        <div className="mt-2 font-mono text-2xl font-semibold text-foreground">
          {formatMetricValue(baseline?.summary.purist.f1, "f1")}
        </div>
      </div>
      <div className="rounded-md border border-border bg-surface p-4">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">Ablated F1</div>
        <div className="mt-2 font-mono text-2xl font-semibold text-foreground">
          {formatMetricValue(ablated?.summary.purist.f1, "f1")}
        </div>
      </div>
      <div className="rounded-md border border-border bg-surface p-4">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">F1 delta</div>
        <div className={`mt-2 font-mono text-2xl font-semibold ${f1Delta !== null && f1Delta < 0 ? "text-error" : "text-success"}`}>
          {deltaLabel(f1Delta)}
        </div>
      </div>
      <div className="rounded-md border border-border bg-surface p-4">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">Accuracy delta</div>
        <div className={`mt-2 font-mono text-2xl font-semibold ${accDelta !== null && accDelta < 0 ? "text-error" : "text-success"}`}>
          {deltaLabel(accDelta)}
        </div>
      </div>
    </div>
  );
}

export default function GanComponentImpact() {
  const rulesQuery = useRules();
  const groups = useMemo(() => rulesQuery.data?.groups ?? [], [rulesQuery.data?.groups]);
  const presets = useMemo(() => buildPresets(groups), [groups]);
  const [selectedGroup, setSelectedGroup] = useState<string>("");
  const [split, setSplit] = useState("validation");
  const [limit, setLimit] = useState("250");
  const [baseline, setBaseline] = useState<RunAblationResponse | null>(null);
  const [ablated, setAblated] = useState<RunAblationResponse | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const activePreset = presets.find((preset) => preset.group === selectedGroup) ?? presets[0];
  const rowLimit = limit.trim() ? Number(limit) : undefined;

  async function runSelectedAblation() {
    if (!activePreset) return;
    setIsRunning(true);
    setError(null);
    try {
      const enabled_groups = groups.filter((group) => group !== activePreset.group);
      const [base, withoutGroup] = await Promise.all([
        runAblation({ split, limit: rowLimit, ablation_config: {} }),
        runAblation({ split, limit: rowLimit, ablation_config: { enabled_groups } }),
      ]);
      setBaseline(base);
      setAblated(withoutGroup);
    } catch (err) {
      setError(String(err));
    } finally {
      setIsRunning(false);
    }
  }

  if (rulesQuery.isLoading) return <SurfaceLoading message="Loading Gan ablation components..." />;
  if (rulesQuery.error) {
    return <SurfaceError title="Gan component data failed to load" detail={String(rulesQuery.error)} />;
  }

  return (
    <SurfaceLayout
      variant="report"
      maxWidth={1120}
      contentClassName="space-y-5"
      header={
        <SurfaceHeader
          surface="laboratory"
          dataset={gan2026Dataset}
          description="Focused rules-only ablations: compare the default pipeline against one removed component family."
          right={
            <>
              <SurfaceLink surface="reliability" datasetId="gan2026" label="Reliability" />
              <SurfaceLink surface="observatory" datasetId="gan2026" label="Runs" />
            </>
          }
        />
      }
    >
      <section className="rounded-md border border-border bg-surface p-4">
        <div className="flex flex-wrap items-end gap-3">
          <label className="space-y-1">
            <span className="block text-[10px] font-semibold uppercase tracking-wider text-muted">Split</span>
            <select
              value={split}
              onChange={(event) => setSplit(event.target.value)}
              className="rounded-md border border-border bg-surface px-2 py-1.5 text-[11px] text-foreground"
            >
              <option value="validation">validation</option>
              <option value="validation25">validation25</option>
              <option value="validation50">validation50</option>
              <option value="validation250">validation250</option>
            </select>
          </label>
          <label className="space-y-1">
            <span className="block text-[10px] font-semibold uppercase tracking-wider text-muted">Rows</span>
            <input
              value={limit}
              onChange={(event) => setLimit(event.target.value)}
              className="w-24 rounded-md border border-border bg-surface px-2 py-1.5 font-mono text-[11px] text-foreground"
              inputMode="numeric"
            />
          </label>
          <button
            onClick={runSelectedAblation}
            disabled={isRunning || !activePreset}
            className="inline-flex items-center gap-2 rounded-md bg-deterministic px-3 py-1.5 text-[11px] font-semibold text-white transition-colors hover:bg-deterministic/90 disabled:opacity-50"
          >
            {isRunning ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
            Run ablation
          </button>
          {error && <span className="text-[11px] text-error">{error}</span>}
        </div>
      </section>

      <section className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
        {presets.map((preset) => {
          const active = preset.group === activePreset?.group;
          return (
            <button
              key={preset.id}
              onClick={() => setSelectedGroup(preset.group)}
              className={`rounded-md border p-3 text-left transition-colors ${
                active
                  ? "border-deterministic/30 bg-deterministic/8"
                  : "border-border bg-surface hover:bg-surface-raised"
              }`}
            >
              <div className="flex items-center gap-2">
                <SlidersHorizontal className="h-3.5 w-3.5 text-muted" />
                <span className="text-[12px] font-semibold text-foreground">{preset.label}</span>
              </div>
              <p className="mt-2 text-[11px] leading-relaxed text-muted">{preset.description}</p>
              <p className="mt-2 font-mono text-[9px] text-muted">{preset.group}</p>
            </button>
          );
        })}
      </section>

      <ImpactSummary baseline={baseline} ablated={ablated} />

      {baseline && ablated && activePreset && (
        <section className="rounded-md border border-border bg-surface p-4">
          <h2 className="text-[11px] font-semibold uppercase tracking-wider text-muted">
            Component readout
          </h2>
          <p className="mt-2 text-[12px] leading-relaxed text-foreground">
            Removing <span className="font-semibold">{activePreset.label}</span> changed Purist F1 by{" "}
            <span className="font-mono">{deltaLabel(metricDelta(baseline, ablated, "f1"))}</span>{" "}
            on {ablated.row_count} {ablated.split} rows. This is the first-order
            component impact; use the reliability scorecard for trust dimensions
            and the error gallery for row-level residuals.
          </p>
        </section>
      )}
    </SurfaceLayout>
  );
}
