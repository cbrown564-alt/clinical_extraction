"use client";

import { useMemo } from "react";
import Link from "next/link";
import { Boxes, ExternalLink, ShieldAlert, Wrench } from "lucide-react";
import {
  exectv2Dataset,
  EXECTV2_FAMILIES,
  surfaceHref,
  TONE_CLASSES,
} from "@/lib/datasets";
import type { ComponentTypeDescriptor } from "@/lib/datasets";
import {
  familyDeltas,
  summarizeComponents,
  type Exectv2ComponentSummary,
  type Exectv2ComponentTypeId,
} from "@/lib/datasets/adapters/exectv2Components";
import type { Exectv2RunSummary } from "@/lib/types";
import { compactRunLabel, formatMetric, useExectv2Runs, useExectv2UrlState } from "./useExectv2";

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
        <span>evidence exact {formatMetric(component.evidenceValidRate, 2)}</span>
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
          {compactRunLabel(base)} → {compactRunLabel(variant)} · family F1 delta
        </h3>
        <p className="mt-1 text-[10px] text-muted">
          Where the partial-hybrid simplification trades headroom against the performance control.
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
                <td className="px-3 py-1.5 text-right font-mono text-muted">{formatMetric(d.baseF1, 3)}</td>
                <td className="px-3 py-1.5 text-right font-mono text-muted">{formatMetric(d.variantF1, 3)}</td>
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

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center bg-background text-muted">
        <p className="text-sm font-medium">Loading component impact…</p>
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

  if (!selectedRun) {
    return (
      <div className="flex h-full items-center justify-center bg-background text-muted">
        <p className="text-sm font-medium">No ExECTv2 runs available.</p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col overflow-y-auto bg-background">
      <header className="border-b border-border bg-surface px-5 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <Boxes className="h-4 w-4 text-deterministic-alt" />
              <h1 className="text-sm font-semibold text-foreground">ExECTv2 · Component Impact</h1>
            </div>
            <p className="mt-1 text-[11px] text-muted">
              Prediction-bearing components by provenance: producer lanes, dictionaries, lenses,
              assembly, and evidence validation. Deterministic formatting is flagged separately from
              semantic add/drop/replace.
            </p>
          </div>
          <div className="flex items-center gap-2">
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
            <Link
              href={surfaceHref("workbench", "exectv2", { run: selectedRun.run_id })}
              className="inline-flex items-center gap-1 rounded border border-deterministic/20 bg-deterministic/5 px-2 py-1 text-[10px] font-medium text-deterministic hover:bg-deterministic/10"
            >
              <ExternalLink className="h-3 w-3" /> Explore
            </Link>
          </div>
        </div>
      </header>

      <div className="mx-auto w-full max-w-[1200px] space-y-6 p-5">
        {baseRun && variantRun && <DeltaTable base={baseRun} variant={variantRun} />}

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
    </div>
  );
}
