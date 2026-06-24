"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchGan2026ComponentAblation } from "@/lib/api";
import { gan2026Dataset } from "@/lib/datasets";
import { adaptGan2026Ladder } from "@/lib/componentLadder";
import { SurfaceLoading, SurfaceError, SurfaceLink } from "@/components/surface";
import ComponentLadderSurface from "@/components/laboratory/ComponentLadderSurface";

export default function GanComponentImpact() {
  const query = useQuery({
    queryKey: ["gan2026-component-ablation"],
    queryFn: fetchGan2026ComponentAblation,
    staleTime: 5 * 60 * 1000,
  });
  const [activeRunId, setActiveRunId] = useState<string | undefined>(undefined);

  const ladder = useMemo(
    () => (query.data ? adaptGan2026Ladder(query.data) : null),
    [query.data]
  );

  const selectedId = useMemo(() => {
    if (!ladder) return undefined;
    const fromState = ladder.architectures.find((a) => a.id === activeRunId);
    const control = ladder.architectures.find((a) => a.decision === "control");
    return (fromState ?? control ?? ladder.architectures[0])?.id;
  }, [ladder, activeRunId]);

  if (query.isLoading) return <SurfaceLoading message="Loading component impact..." />;
  if (query.error)
    return <SurfaceError title="Gan component data failed to load" detail={String(query.error)} />;
  if (!ladder)
    return <SurfaceError title="No Gan component-impact payload available." detail="" />;

  return (
    <ComponentLadderSurface
      ladder={ladder}
      dataset={gan2026Dataset}
      description="How purist accuracy builds up across each architecture's pipeline stages."
      selectedArchitectureId={selectedId}
      onSelectArchitecture={setActiveRunId}
      headerRight={
        <>
          <SurfaceLink surface="reliability" datasetId="gan2026" label="Reliability" />
          <SurfaceLink surface="observatory" datasetId="gan2026" label="Runs" />
        </>
      }
    />
  );
}
