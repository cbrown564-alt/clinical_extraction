"use client";

import { useMemo } from "react";
import { AlertTriangle, Info, Wrench } from "lucide-react";
import { exectv2Dataset, EXECTV2_FAMILIES, TONE_CLASSES } from "@/lib/datasets";
import type { ComponentTypeDescriptor } from "@/lib/datasets";
import type { Exectv2Entity } from "@/lib/types";
import {
  familyDeltas,
  summarizeComponents,
  type Exectv2ComponentSummary,
  type Exectv2ComponentTypeId,
} from "@/lib/datasets/adapters/exectv2Components";
import type { Exectv2RunSummary } from "@/lib/types";
import {
  SurfaceHeader,
  SurfaceLayout,
  SurfaceLoading,
  SurfaceError,
  SurfaceEmpty,
  SurfaceLink,
  F1Cell,
  formatMetricValue,
} from "@/components/surface";
import { compactRunLabel, useExectv2Runs, useExectv2UrlState } from "./useExectv2";

const FAMILY_IDS = EXECTV2_FAMILIES.map((f) => f.id);
const COMPONENT_TYPES = exectv2Dataset.componentTypes;

function typeDescriptor(typeId: Exectv2ComponentTypeId): ComponentTypeDescriptor | undefined {
  return COMPONENT_TYPES.find((t) => t.id === typeId);
}

function ComponentCard({ component }: { component: Exectv2ComponentSummary }) {
  const descriptor = typeDescriptor(component.typeId);
  const tone = descriptor?.tone ?? "muted";
  return (
    <div className="rounded-md border border-border bg-surface p-3">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="truncate font-mono text-[11px] font-semibold text-foreground" title={component.owner}>
            {component.owner}
          </p>
          <p className="mt-0.5 text-[10px] text-muted">{descriptor?.label ?? component.typeId}</p>
        </div>
        <div className="flex shrink-0 items-center gap-1">
          {component.deterministic && (
            <span
              className="inline-flex items-center gap-1 rounded border border-deterministic/25 bg-deterministic/10 px-1.5 py-0.5 text-[9px] font-medium text-deterministic"
              title="Deterministic formatting / repair action"
            >
              <Wrench className="h-2.5 w-2.5" /> det
            </span>
          )}
          <span className={`rounded border px-1.5 py-0.5 text-[9px] font-medium ${TONE_CLASSES[tone]}`}>
            {component.mentionCount}
          </span>
        </div>
      </div>

      <div className="mt-2 flex flex-wrap gap-1 font-mono text-[9px] text-muted">
        {FAMILY_IDS.map((family) => {
          const count = component.byFamily[family] ?? 0;
          if (count === 0) return null;
          return (
            <span key={family} className="rounded border border-border bg-surface-raised px-1.5 py-0.5">
              {EXECTV2_FAMILIES.find((f) => f.id === family)?.shortLabel} {count}
            </span>
          );
        })}
      </div>

      <div className="mt-2 flex items-center justify-between text-[9px] text-muted">
        <span>evidence exact {formatMetricValue(component.evidenceValidRate, "rate")}</span>
        <span className="truncate" title={component.lanes.join(", ")}>
          {component.lanes.length} lane{component.lanes.length === 1 ? "" : "s"}
        </span>
      </div>
    </div>
  );
}

function DeltaTable({ base, variant }: { base: Exectv2RunSummary; variant: Exectv2RunSummary }) {
  const deltas = familyDeltas(base, variant, FAMILY_IDS);
  return (
    <section className="rounded-md border border-border bg-surface">
      <div className="border-b border-border px-3 py-2">
        <h3 className="text-[11px] font-semibold uppercase tracking-wider text-muted">
          {compactRunLabel(base)} → {compactRunLabel(variant)}
        </h3>
        <p className="mt-1 text-[10px] text-muted">
          Family F1 delta where the partial-hybrid simplification trades headroom against the control.
        </p>
      </div>
      <table className="w-full border-collapse text-[11px]">
        <thead>
          <tr className="border-b border-border bg-surface-raised/60 text-[10px] uppercase tracking-wider text-muted">
            <th className="px-3 py-1.5 text-left font-semibold">Family</th>
            <th className="px-3 py-1.5 text-right font-semibold">{compactRunLabel(base)}</th>
            <th className="px-3 py-1.5 text-right font-semibold">{compactRunLabel(variant)}</th>
            <th className="px-3 py-1.5 text-right font-semibold">Δ</th>
          </tr>
        </thead>
        <tbody>
          {deltas.map((d) => {
            const tone =
              d.delta === null ? "text-muted" : d.delta < -0.001 ? "text-error" : d.delta > 0.001 ? "text-success" : "text-muted";
            return (
              <tr key={d.family} className="border-b border-border/60 last:border-b-0">
                <td className="px-3 py-1.5 text-foreground">{d.family}</td>
                <td className="px-3 py-1.5 text-right font-mono text-muted">{formatMetricValue(d.baseF1, "f1")}</td>
                <td className="px-3 py-1.5 text-right font-mono text-muted">{formatMetricValue(d.variantF1, "f1")}</td>
                <td className={`px-3 py-1.5 text-right font-mono ${tone}`}>
                  {d.delta === null ? "—" : `${d.delta >= 0 ? "+" : ""}${d.delta.toFixed(3)}`}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}

/**
 * The right pane, parallel to Gan's live SimulationPanel. ExECTv2 architectures
 * are checkpointed rather than re-runnable here, so instead of a live ablation we
 * report the *observed* family F1 of the focused run and the v08→v09 delta — with
 * an explicit note about why there's no Simulate button.
 */
function ObservedImpactPanel({
  run,
  base,
  variant,
}: {
  run: Exectv2RunSummary;
  base?: Exectv2RunSummary;
  variant?: Exectv2RunSummary;
}) {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xs font-semibold uppercase tracking-wider text-foreground">Ablation status</h2>
        <div className="mt-2 flex items-start gap-2 rounded-md border border-error/25 bg-error/[0.04] px-2.5 py-2 text-[10px] leading-snug text-muted">
          <AlertTriangle className="mt-0.5 h-3 w-3 shrink-0 text-error" />
          <span>
            ExECTv2 does not yet have replayable component ablations wired into
            the frontend. This panel shows observed architecture deltas and
            provenance only; causal component-impact readouts need the next
            consolidation phase.
          </span>
        </div>
      </div>

      <section className="rounded-md border border-border bg-surface p-3">
        <div className="flex items-start gap-2">
          <Info className="mt-0.5 h-3.5 w-3.5 shrink-0 text-deterministic-alt" />
          <div>
            <h3 className="text-[11px] font-semibold uppercase tracking-wider text-muted">
              Ablation contract
            </h3>
            <p className="mt-1 text-[10px] leading-relaxed text-muted">
              True one-component-off deltas remain gated on dev140 replay
              configs, family deltas, transition counts, and
              projection-vs-semantic provenance tags. Until then this surface stays
              provenance-only.
            </p>
          </div>
        </div>
      </section>

      <section className="rounded-md border border-border bg-surface">
        <div className="border-b border-border px-3 py-2">
          <h3 className="text-[11px] font-semibold uppercase tracking-wider text-muted">
            {compactRunLabel(run)} · family F1
          </h3>
        </div>
        <table className="w-full border-collapse text-[11px]">
          <tbody>
            <tr className="border-b border-border/60">
              <td className="px-3 py-1.5 font-semibold text-foreground">Overall</td>
              <F1Cell value={run.metrics.overall_f1} lead />
            </tr>
            {EXECTV2_FAMILIES.map((family) => (
              <tr key={family.id} className="border-b border-border/60 last:border-b-0">
                <td className="px-3 py-1.5 text-foreground">{family.label}</td>
                <F1Cell value={run.metrics.families[family.id as Exectv2Entity]?.f1} />
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {base && variant && <DeltaTable base={base} variant={variant} />}
    </div>
  );
}

export default function Exectv2ComponentImpact() {
  const { runs, isLoading, error } = useExectv2Runs();
  const { get, set } = useExectv2UrlState();
  const activeRunId = get("run");

  const selectedRun = useMemo(
    () => runs.find((r) => r.run_id === activeRunId) ?? runs.find((r) => r.decision === "control") ?? runs[0],
    [runs, activeRunId]
  );

  const components = useMemo(() => (selectedRun ? summarizeComponents(selectedRun) : []), [selectedRun]);

  const grouped = useMemo(() => {
    const map = new Map<Exectv2ComponentTypeId, Exectv2ComponentSummary[]>();
    for (const c of components) {
      const list = map.get(c.typeId) ?? [];
      list.push(c);
      map.set(c.typeId, list);
    }
    return map;
  }, [components]);

  const baseRun = useMemo(() => runs.find((r) => r.run_id.includes("v08")), [runs]);
  const variantRun = useMemo(() => runs.find((r) => r.run_id.includes("v09_partial_hybrid")), [runs]);

  if (isLoading) return <SurfaceLoading message="Loading component impact…" />;
  if (error) return <SurfaceError title="ExECTv2 data failed to load" detail={String(error)} />;

  const header = (
    <SurfaceHeader
      surface="laboratory"
          dataset={exectv2Dataset}
          description="Component provenance for the selected architecture. True one-component-off ablation deltas are not built yet and are tracked as the next consolidation phase."
          right={
            selectedRun && (
              <>
            <select
              value={selectedRun.run_id}
              onChange={(e) => set({ run: e.target.value })}
              className="rounded-md border border-border bg-surface px-2 py-1 text-[11px] text-foreground focus:outline-none"
            >
              {runs.map((run) => (
                <option key={run.run_id} value={run.run_id}>
                  {compactRunLabel(run)} ({run.decision})
                </option>
              ))}
            </select>
            <SurfaceLink surface="workbench" datasetId="exectv2" params={{ run: selectedRun.run_id }} label="Explore" />
            <SurfaceLink surface="reliability" datasetId="exectv2" label="Reliability" />
          </>
        )
      }
    />
  );

  if (!selectedRun) {
    return (
      <SurfaceLayout variant="fill" header={header}>
        <div className="p-5">
          <SurfaceEmpty message="No ExECTv2 architectures available." />
        </div>
      </SurfaceLayout>
    );
  }

  return (
    <SurfaceLayout variant="fill" header={header}>
      <div className="flex min-h-0 flex-1">
        {/* Left: component inventory */}
        <div className="min-h-0 flex-1 space-y-6 overflow-y-auto p-5">
          {COMPONENT_TYPES.map((type) => {
            const list = grouped.get(type.id as Exectv2ComponentTypeId) ?? [];
            if (list.length === 0) return null;
            return (
              <section key={type.id} className="space-y-2">
                <div className="flex items-baseline gap-2">
                  <span className={`rounded border px-1.5 py-0.5 text-[10px] font-medium ${TONE_CLASSES[type.tone]}`}>
                    {type.label}
                  </span>
                  <span className="text-[10px] text-muted">{type.description}</span>
                </div>
                <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
                  {list.map((component) => (
                    <ComponentCard key={component.owner} component={component} />
                  ))}
                </div>
              </section>
            );
          })}
        </div>

        {/* Right: observed impact (parallel to Gan's live simulation panel) */}
        <div className="w-[380px] shrink-0 overflow-y-auto border-l border-border bg-surface p-5">
          <ObservedImpactPanel run={selectedRun} base={baseRun} variant={variantRun} />
        </div>
      </div>
    </SurfaceLayout>
  );
}
