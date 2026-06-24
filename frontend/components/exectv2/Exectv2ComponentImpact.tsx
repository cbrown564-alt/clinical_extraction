"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  fetchExectv2ComponentAblation,
  fetchExectv2ComponentTransitions,
} from "@/lib/api";
import { exectv2Dataset } from "@/lib/datasets";
import { adaptExectv2Ladder } from "@/lib/componentLadder";
import { SurfaceLoading, SurfaceError, SurfaceLink } from "@/components/surface";
import ComponentLadderSurface, {
  type WorkedExampleConfig,
} from "@/components/laboratory/ComponentLadderSurface";
import Exectv2TransitionSidebar from "./Exectv2TransitionSidebar";
import { useExectv2UrlState } from "./useExectv2";

export default function Exectv2ComponentImpact() {
  const query = useQuery({
    queryKey: ["exectv2-component-ablation"],
    queryFn: fetchExectv2ComponentAblation,
    staleTime: 5 * 60 * 1000,
  });
  const transitionsQuery = useQuery({
    queryKey: ["exectv2-component-transitions"],
    queryFn: fetchExectv2ComponentTransitions,
    staleTime: 5 * 60 * 1000,
  });
  const { get, set } = useExectv2UrlState();
  const activeRunId = get("run");

  const ladder = useMemo(
    () => (query.data ? adaptExectv2Ladder(query.data) : null),
    [query.data]
  );

  const transitions = transitionsQuery.data;
  const workedExample = useMemo<WorkedExampleConfig | undefined>(() => {
    if (!transitions) return undefined;
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
  }, [transitions]);

  const selectedId = useMemo(() => {
    if (!ladder) return undefined;
    const fromUrl = ladder.architectures.find((a) => a.id === activeRunId);
    const control = ladder.architectures.find((a) => a.decision === "control");
    return (fromUrl ?? control ?? ladder.architectures[0])?.id;
  }, [ladder, activeRunId]);

  if (query.isLoading) return <SurfaceLoading message="Loading component impact..." />;
  if (query.error)
    return <SurfaceError title="ExECTv2 component data failed to load" detail={String(query.error)} />;
  if (!ladder)
    return <SurfaceError title="No ExECTv2 component-impact payload available." detail="" />;

  return (
    <ComponentLadderSurface
      ladder={ladder}
      dataset={exectv2Dataset}
      description="How clinical F1 builds up across each architecture's pipeline stages."
      selectedArchitectureId={selectedId}
      onSelectArchitecture={(id) => set({ run: id })}
      workedExample={workedExample}
      headerRight={
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
      }
    />
  );
}
