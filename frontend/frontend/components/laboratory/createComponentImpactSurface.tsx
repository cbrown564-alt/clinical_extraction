"use client";

import { useMemo, useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import type { DatasetDescriptor } from "@/lib/datasets";
import type { ComponentLadder } from "@/lib/componentLadder";
import { SurfaceLoading, SurfaceError } from "@/components/surface";
import ComponentLadderSurface, {
  type WorkedExampleConfig,
} from "@/components/laboratory/ComponentLadderSurface";

export interface ComponentImpactSurfaceConfig<TAblation, TTransitions> {
  ablationQueryKey: string[];
  transitionsQueryKey: string[];
  fetchAblation: () => Promise<TAblation>;
  fetchTransitions: () => Promise<TTransitions>;
  adaptLadder: (data: TAblation) => ComponentLadder;
  dataset: DatasetDescriptor;
  description: string;
  errorTitle: string;
  resolveSelectedId: (
    ladder: ComponentLadder,
    activeId: string | undefined
  ) => string | undefined;
  buildWorkedExample?: (
    transitions: TTransitions,
    ladder: ComponentLadder
  ) => WorkedExampleConfig | undefined;
  headerRight?: (selectedId: string | undefined) => ReactNode;
}

export interface ComponentImpactSurfaceProps {
  activeArchitectureId?: string;
  onArchitectureChange?: (id: string) => void;
}

export function createComponentImpactSurface<TAblation, TTransitions>(
  config: ComponentImpactSurfaceConfig<TAblation, TTransitions>
) {
  return function ComponentImpactSurface({
    activeArchitectureId,
    onArchitectureChange,
  }: ComponentImpactSurfaceProps = {}) {
    const query = useQuery({
      queryKey: config.ablationQueryKey,
      queryFn: config.fetchAblation,
      staleTime: 5 * 60 * 1000,
    });
    const transitionsQuery = useQuery({
      queryKey: config.transitionsQueryKey,
      queryFn: config.fetchTransitions,
      staleTime: 5 * 60 * 1000,
    });

    const [localActiveId, setLocalActiveId] = useState<string | undefined>(undefined);
    const activeId = activeArchitectureId ?? localActiveId;

    const ladder = useMemo(
      () => (query.data ? config.adaptLadder(query.data) : null),
      [query.data]
    );

    const transitions = transitionsQuery.data;
    const workedExample = useMemo(() => {
      if (!transitions || !ladder || !config.buildWorkedExample) return undefined;
      return config.buildWorkedExample(transitions, ladder);
    }, [transitions, ladder]);

    const selectedId = useMemo(() => {
      if (!ladder) return undefined;
      return config.resolveSelectedId(ladder, activeId);
    }, [ladder, activeId]);

    if (query.isLoading) return <SurfaceLoading message="Loading component impact..." />;
    if (query.error)
      return (
        <SurfaceError title={config.errorTitle} detail={String(query.error)} />
      );
    if (!ladder)
      return (
        <SurfaceError
          title={`No ${config.dataset.label} component-impact payload available.`}
          detail=""
        />
      );

    return (
      <ComponentLadderSurface
        ladder={ladder}
        dataset={config.dataset}
        description={config.description}
        selectedArchitectureId={selectedId}
        onSelectArchitecture={(id) => {
          if (onArchitectureChange) {
            onArchitectureChange(id);
          } else {
            setLocalActiveId(id);
          }
        }}
        workedExample={workedExample}
        headerRight={config.headerRight?.(selectedId)}
      />
    );
  };
}
