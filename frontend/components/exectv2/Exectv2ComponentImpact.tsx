"use client";

import {
  fetchExectv2ComponentAblation,
  fetchExectv2ComponentTransitions,
} from "@/lib/api";
import { exectv2Dataset } from "@/lib/datasets";
import { adaptExectv2Ladder } from "@/lib/componentLadder";
import { SurfaceLink } from "@/components/surface";
import { createComponentImpactSurface } from "@/components/laboratory/createComponentImpactSurface";
import Exectv2TransitionSidebar from "./Exectv2TransitionSidebar";
import { useExectv2UrlState } from "./useExectv2";
import type {
  Exectv2ComponentAblationResponse,
  Exectv2ComponentTransitionsResponse,
} from "@/lib/types";

const Exectv2ComponentImpactSurface = createComponentImpactSurface<
  Exectv2ComponentAblationResponse,
  Exectv2ComponentTransitionsResponse
>({
  ablationQueryKey: ["exectv2-component-ablation"],
  transitionsQueryKey: ["exectv2-component-transitions"],
  fetchAblation: fetchExectv2ComponentAblation,
  fetchTransitions: fetchExectv2ComponentTransitions,
  adaptLadder: adaptExectv2Ladder,
  dataset: exectv2Dataset,
  description: "How clinical F1 builds up across each architecture's pipeline stages.",
  errorTitle: "ExECTv2 component data failed to load",
  resolveSelectedId: (ladder, activeId) => {
    const fromUrl = ladder.architectures.find((a) => a.id === activeId);
    const control = ladder.architectures.find((a) => a.decision === "control");
    return (fromUrl ?? control ?? ladder.architectures[0])?.id;
  },
  buildWorkedExample: (transitions) => {
    const exampleCounts: Record<string, number> = {};
    for (const arch of transitions.architectures) {
      exampleCounts[arch.run_id] = arch.examples.length;
    }
    return {
      exampleCounts,
      renderSidebar: (ctx) => {
        const archTransitions = transitions.architectures.find(
          (a) => a.run_id === ctx.architectureId
        );
        if (!archTransitions) return null;
        return (
          <Exectv2TransitionSidebar
            archTransitions={archTransitions}
            ladderStages={ctx.stages}
            exampleIndex={ctx.exampleIndex}
            onSelectExample={ctx.onSelectExample}
            selectedStageId={ctx.stageId}
          />
        );
      },
    };
  },
  headerRight: (selectedId) => (
    <>
      {selectedId && (
        <SurfaceLink
          surface="workbench"
          datasetId="exectv2"
          params={{ run: selectedId }}
          label="Explore"
        />
      )}
      <SurfaceLink surface="reliability" datasetId="exectv2" label="Reliability" />
    </>
  ),
});

export default function Exectv2ComponentImpact() {
  const { get, set } = useExectv2UrlState();
  return (
    <Exectv2ComponentImpactSurface
      activeArchitectureId={get("run")}
      onArchitectureChange={(id) => set({ run: id })}
    />
  );
}
