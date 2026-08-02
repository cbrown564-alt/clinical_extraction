"use client";

import {
  fetchGan2026ComponentAblation,
  fetchGan2026ComponentTransitions,
} from "@/lib/api";
import { gan2026Dataset } from "@/lib/datasets";
import { adaptGan2026Ladder } from "@/lib/componentLadder";
import { SurfaceLink } from "@/components/surface";
import GanTransitionSidebar from "@/components/laboratory/GanTransitionSidebar";
import { createComponentImpactSurface } from "@/components/laboratory/createComponentImpactSurface";
import type {
  Gan2026ComponentAblationResponse,
  Gan2026ComponentTransitionsResponse,
} from "@/lib/types";

export default createComponentImpactSurface<
  Gan2026ComponentAblationResponse,
  Gan2026ComponentTransitionsResponse
>({
  ablationQueryKey: ["gan2026-component-ablation"],
  transitionsQueryKey: ["gan2026-component-transitions"],
  fetchAblation: fetchGan2026ComponentAblation,
  fetchTransitions: fetchGan2026ComponentTransitions,
  adaptLadder: adaptGan2026Ladder,
  dataset: gan2026Dataset,
  description: "How strict label-match accuracy builds up across each architecture's pipeline stages.",
  errorTitle: "Gan component data failed to load",
  resolveSelectedId: (ladder, activeId) => {
    const fromState = ladder.architectures.find((a) => a.id === activeId);
    const rulesBaseline = ladder.architectures.find(
      (a) => a.id === "deterministic_canonical_pipeline"
    );
    return (fromState ?? rulesBaseline ?? ladder.architectures[0])?.id;
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
          <GanTransitionSidebar
            archTransitions={archTransitions}
            categories={transitions.categories}
            ladderStages={ctx.stages}
            exampleIndex={ctx.exampleIndex}
            onSelectExample={ctx.onSelectExample}
            selectedStageId={ctx.stageId}
          />
        );
      },
    };
  },
  headerRight: () => (
    <>
      <SurfaceLink surface="reliability" datasetId="gan2026" label="Reliability" />
      <SurfaceLink surface="observatory" datasetId="gan2026" label="Runs" />
    </>
  ),
});
