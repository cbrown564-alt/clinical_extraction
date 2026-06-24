"use client";

import { useMemo } from "react";
import { Activity, FileText, Layers3 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { fetchExectv2ComponentAblation } from "@/lib/api";
import { exectv2Dataset, EXECTV2_FAMILIES, TONE_CLASSES } from "@/lib/datasets";
import type {
  Exectv2ArchitectureLadder,
  Exectv2ComponentAblationResponse,
  Exectv2Entity,
  Exectv2LayerImpact,
} from "@/lib/types";
import {
  SurfaceHeader,
  SurfaceLayout,
  SurfaceLoading,
  SurfaceError,
  SurfaceEmpty,
  SurfaceLink,
  formatMetricValue,
} from "@/components/surface";
import { useExectv2UrlState } from "./useExectv2";

const FAMILY_IDS = EXECTV2_FAMILIES.map((family) => family.id as Exectv2Entity);

const COMPONENT_TONE: Record<string, keyof typeof TONE_CLASSES> = {
  llm_producer: "llm",
  evidence_validation: "success",
  dictionary: "deterministic",
  semantic_lens: "hybrid",
  assembler: "deterministic-alt",
  deterministic_projection: "deterministic",
};

function shortArchitectureLabel(runId: string): string {
  if (runId.includes("v09_partial_hybrid")) return "v09 partial";
  if (runId.includes("v0916_deepseek")) return "DeepSeek";
  if (runId.includes("v0922_qwen")) return "Qwen";
  if (runId.includes("v08")) return "v08 control";
  return runId.replace("exectv2_holistic_finding_assembly_", "");
}

function deltaText(value: number | null | undefined): string {
  if (typeof value !== "number" || Number.isNaN(value)) return "-";
  return `${value >= 0 ? "+" : ""}${value.toFixed(3)}`;
}

function deltaClass(value: number | null | undefined): string {
  if (typeof value !== "number" || Math.abs(value) < 0.0005) return "text-muted";
  return value > 0 ? "text-success" : "text-error";
}

function componentTone(componentType: string): string {
  return TONE_CLASSES[COMPONENT_TONE[componentType] ?? "muted"];
}

function layerById(architecture: Exectv2ArchitectureLadder, layerId: string) {
  return architecture.layers.find((layer) => layer.layer_id === layerId);
}

function impactByLayer(architecture: Exectv2ArchitectureLadder, layerId: string) {
  return architecture.layer_impacts.find((impact) => impact.layer_id === layerId);
}

function ArchitectureMatrix({
  payload,
  selectedRunId,
  onSelect,
}: {
  payload: Exectv2ComponentAblationResponse;
  selectedRunId: string;
  onSelect: (runId: string) => void;
}) {
  return (
    <section className="overflow-hidden rounded-md border border-border bg-surface">
      <div className="border-b border-border px-4 py-3">
        <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-wider text-muted">
          <Layers3 className="h-3.5 w-3.5" />
          Architecture Layer Ladder
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[1080px] border-collapse text-[11px]">
          <thead>
            <tr className="border-b border-border bg-surface-raised/60 text-[10px] uppercase tracking-wider text-muted">
              <th className="w-56 px-3 py-2 text-left font-semibold">Architecture</th>
              {payload.layers.map((layer) => (
                <th key={layer.layer_id} className="px-3 py-2 text-right font-semibold">
                  {layer.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {payload.architectures.map((architecture) => {
              const active = architecture.run_id === selectedRunId;
              return (
                <tr
                  key={architecture.run_id}
                  className={`border-b border-border/60 last:border-b-0 ${
                    active ? "bg-deterministic/8" : "hover:bg-surface-raised/70"
                  }`}
                >
                  <td className="px-3 py-2 align-top">
                    <button
                      onClick={() => onSelect(architecture.run_id)}
                      className="text-left"
                    >
                      <span className="block text-[12px] font-semibold text-foreground">
                        {shortArchitectureLabel(architecture.run_id)}
                      </span>
                      <span className="mt-0.5 block font-mono text-[9px] text-muted">
                        {architecture.decision} · {architecture.model}
                      </span>
                    </button>
                  </td>
                  {payload.layers.map((definition) => {
                    const layer = layerById(architecture, definition.layer_id);
                    const impact = impactByLayer(architecture, definition.layer_id);
                    return (
                      <td key={definition.layer_id} className="px-3 py-2 text-right align-top">
                        <span className="block font-mono text-[12px] text-foreground">
                          {formatMetricValue(layer?.scores.overall.f1, "f1")}
                        </span>
                        <span className={`block font-mono text-[10px] ${deltaClass(impact?.overall_delta_from_previous)}`}>
                          {deltaText(impact?.overall_delta_from_previous)}
                        </span>
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function LayerImpactMatrix({
  payload,
  selectedRunId,
}: {
  payload: Exectv2ComponentAblationResponse;
  selectedRunId: string;
}) {
  const layers = payload.layers.filter((layer) => layer.layer_id !== "raw_lane_candidates");
  return (
    <section className="overflow-hidden rounded-md border border-border bg-surface">
      <div className="border-b border-border px-4 py-3">
        <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-wider text-muted">
          <Activity className="h-3.5 w-3.5" />
          Layer Impact Matrix
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[900px] border-collapse text-[11px]">
          <thead>
            <tr className="border-b border-border bg-surface-raised/60 text-[10px] uppercase tracking-wider text-muted">
              <th className="w-56 px-3 py-2 text-left font-semibold">Layer</th>
              {payload.architectures.map((architecture) => (
                <th key={architecture.run_id} className="px-3 py-2 text-right font-semibold">
                  {shortArchitectureLabel(architecture.run_id)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {layers.map((definition) => (
              <tr key={definition.layer_id} className="border-b border-border/60 last:border-b-0">
                <td className="px-3 py-2 align-top">
                  <span className={`rounded border px-1.5 py-0.5 text-[10px] font-medium ${componentTone(definition.component_type)}`}>
                    {definition.label}
                  </span>
                  <p className="mt-1 max-w-[42ch] text-[10px] leading-relaxed text-muted">
                    {definition.interpretation}
                  </p>
                </td>
                {payload.architectures.map((architecture) => {
                  const impact = impactByLayer(architecture, definition.layer_id);
                  const active = architecture.run_id === selectedRunId;
                  return (
                    <td
                      key={architecture.run_id}
                      className={`px-3 py-2 text-right align-top ${active ? "bg-deterministic/8" : ""}`}
                    >
                      <span className={`block font-mono text-[13px] font-semibold ${deltaClass(impact?.overall_delta_from_previous)}`}>
                        {deltaText(impact?.overall_delta_from_previous)}
                      </span>
                      <span className="mt-1 block font-mono text-[9px] text-muted">
                        Dx {deltaText(impact?.family_deltas.Diagnosis)} · SF{" "}
                        {deltaText(impact?.family_deltas.SeizureFrequency)}
                      </span>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function FamilyDeltaGrid({ impact }: { impact: Exectv2LayerImpact }) {
  return (
    <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
      {FAMILY_IDS.map((family) => (
        <div key={family} className="rounded-md border border-border bg-surface-raised/40 px-2 py-2">
          <div className="text-[9px] uppercase tracking-wider text-muted">
            {EXECTV2_FAMILIES.find((item) => item.id === family)?.shortLabel}
          </div>
          <div className={`mt-1 font-mono text-[12px] font-semibold ${deltaClass(impact.family_deltas[family])}`}>
            {deltaText(impact.family_deltas[family])}
          </div>
        </div>
      ))}
    </div>
  );
}

function SelectedArchitectureDetail({ architecture }: { architecture: Exectv2ArchitectureLadder }) {
  return (
    <section className="grid grid-cols-1 gap-4 xl:grid-cols-[1fr_420px]">
      <div className="overflow-hidden rounded-md border border-border bg-surface">
        <div className="border-b border-border px-4 py-3">
          <h2 className="text-[11px] font-semibold uppercase tracking-wider text-muted">
            {shortArchitectureLabel(architecture.run_id)} Layer Detail
          </h2>
        </div>
        <table className="w-full border-collapse text-[11px]">
          <thead>
            <tr className="border-b border-border bg-surface-raised/60 text-[10px] uppercase tracking-wider text-muted">
              <th className="px-3 py-2 text-left font-semibold">Layer</th>
              <th className="px-3 py-2 text-right font-semibold">F1</th>
              <th className="px-3 py-2 text-right font-semibold">Delta</th>
              <th className="px-3 py-2 text-right font-semibold">P / R</th>
            </tr>
          </thead>
          <tbody>
            {architecture.layers.map((layer) => {
              const impact = impactByLayer(architecture, layer.layer_id);
              return (
                <tr key={layer.layer_id} className="border-b border-border/60 last:border-b-0">
                  <td className="px-3 py-2">
                    <span className={`rounded border px-1.5 py-0.5 text-[10px] font-medium ${componentTone(layer.component_type)}`}>
                      {layer.label}
                    </span>
                    <p className="mt-1 text-[10px] leading-relaxed text-muted">
                      {layer.interpretation}
                    </p>
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-foreground">
                    {formatMetricValue(layer.scores.overall.f1, "f1")}
                  </td>
                  <td className={`px-3 py-2 text-right font-mono ${deltaClass(impact?.overall_delta_from_previous)}`}>
                    {deltaText(impact?.overall_delta_from_previous)}
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-muted">
                    {formatMetricValue(layer.scores.overall.precision, "f1")} /{" "}
                    {formatMetricValue(layer.scores.overall.recall, "f1")}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="space-y-3">
        {architecture.layer_impacts
          .filter((impact) => impact.layer_id !== "raw_lane_candidates")
          .map((impact) => (
            <div key={impact.layer_id} className="rounded-md border border-border bg-surface p-3">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="text-[11px] font-semibold text-foreground">
                    {impact.layer_label}
                  </div>
                  <div className="mt-0.5 font-mono text-[9px] text-muted">
                    {impact.previous_layer_label || "start"} to {impact.layer_label}
                  </div>
                </div>
                <div className={`font-mono text-[15px] font-semibold ${deltaClass(impact.overall_delta_from_previous)}`}>
                  {deltaText(impact.overall_delta_from_previous)}
                </div>
              </div>
              <div className="mt-3">
                <FamilyDeltaGrid impact={impact} />
              </div>
            </div>
          ))}
      </div>
    </section>
  );
}

export default function Exectv2ComponentImpact() {
  const query = useQuery({
    queryKey: ["exectv2-component-ablation"],
    queryFn: fetchExectv2ComponentAblation,
    staleTime: 5 * 60 * 1000,
  });
  const { get, set } = useExectv2UrlState();
  const activeRunId = get("run");

  const payload = query.data;
  const selectedArchitecture = useMemo(() => {
    const architectures = payload?.architectures ?? [];
    return (
      architectures.find((architecture) => architecture.run_id === activeRunId) ??
      architectures.find((architecture) => architecture.decision === "control") ??
      architectures[0]
    );
  }, [activeRunId, payload?.architectures]);

  if (query.isLoading) return <SurfaceLoading message="Loading component impact..." />;
  if (query.error) return <SurfaceError title="ExECTv2 component data failed to load" detail={String(query.error)} />;

  const header = (
    <SurfaceHeader
      surface="laboratory"
      dataset={exectv2Dataset}
      description="Layered aggregate replay across selected ExECTv2 architectures."
      right={
        payload && selectedArchitecture ? (
          <>
            <select
              value={selectedArchitecture.run_id}
              onChange={(event) => set({ run: event.target.value })}
              className="rounded-md border border-border bg-surface px-2 py-1 text-[11px] text-foreground focus:outline-none"
            >
              {payload.architectures.map((architecture) => (
                <option key={architecture.run_id} value={architecture.run_id}>
                  {shortArchitectureLabel(architecture.run_id)} ({architecture.decision})
                </option>
              ))}
            </select>
            <SurfaceLink
              surface="workbench"
              datasetId="exectv2"
              params={{ run: selectedArchitecture.run_id }}
              label="Explore"
            />
            <SurfaceLink surface="reliability" datasetId="exectv2" label="Reliability" />
          </>
        ) : null
      }
    />
  );

  if (!payload || !selectedArchitecture) {
    return (
      <SurfaceLayout variant="report" maxWidth={1320} header={header}>
        <SurfaceEmpty message="No ExECTv2 component-impact payload available." />
      </SurfaceLayout>
    );
  }

  return (
    <SurfaceLayout
      variant="report"
      maxWidth={1480}
      contentClassName="space-y-4"
      header={header}
    >
      <section className="grid grid-cols-1 gap-3 md:grid-cols-4">
        <div className="rounded-md border border-border bg-surface p-3">
          <div className="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-wider text-muted">
            <FileText className="h-3.5 w-3.5" />
            Replay set
          </div>
          <div className="mt-2 font-mono text-xl font-semibold text-foreground">
            {payload.architectures.length} x {payload.layers.length}
          </div>
        </div>
        <div className="rounded-md border border-border bg-surface p-3">
          <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
            Selected final F1
          </div>
          <div className="mt-2 font-mono text-xl font-semibold text-foreground">
            {formatMetricValue(selectedArchitecture.final_score.overall.f1, "f1")}
          </div>
        </div>
        <div className="rounded-md border border-border bg-surface p-3">
          <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
            Policy
          </div>
          <div className="mt-2 text-[11px] leading-snug text-foreground">
            Aggregate only, no model calls
          </div>
        </div>
        <div className="rounded-md border border-border bg-surface p-3">
          <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
            Source
          </div>
          <div className="mt-2 font-mono text-[10px] leading-snug text-muted">
            {payload.generated_on}
          </div>
        </div>
      </section>

      <ArchitectureMatrix
        payload={payload}
        selectedRunId={selectedArchitecture.run_id}
        onSelect={(runId) => set({ run: runId })}
      />
      <LayerImpactMatrix payload={payload} selectedRunId={selectedArchitecture.run_id} />
      <SelectedArchitectureDetail architecture={selectedArchitecture} />
    </SurfaceLayout>
  );
}
