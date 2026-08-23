"use client";

import { useEffect } from "react";
import LetterRenderer from "@/components/surface/LetterRenderer";
import {
  ExplorerBody,
  SurfaceEmpty,
  SurfaceError,
  SurfaceLayout,
  SurfaceLoading,
} from "@/components/surface";
import { clickableFacts, factById, highlightToneForFact } from "@/lib/assemblyLine";
import {
  getActiveAssemblyCase,
  getActiveAssemblyRun,
  useAssemblyLineStore,
} from "@/lib/assemblyLineStore";
import FiveCellGridTable from "@/components/paper/FiveCellGridTable";
import AssemblyLineControls, { AssemblyLineStory } from "./AssemblyLineControls";
import AssemblyLineSidebar from "./AssemblyLineSidebar";

export default function AssemblyLineWorkspace() {
  const loadData = useAssemblyLineStore((state) => state.loadData);
  const isLoading = useAssemblyLineStore((state) => state.isLoading);
  const error = useAssemblyLineStore((state) => state.error);
  const selectedFactId = useAssemblyLineStore((state) => state.selectedFactId);
  const setSelectedFactId = useAssemblyLineStore((state) => state.setSelectedFactId);
  const activeCase = useAssemblyLineStore(getActiveAssemblyCase);
  const activeRun = useAssemblyLineStore(getActiveAssemblyRun);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  if (isLoading && !activeCase) {
    return <SurfaceLoading message="Loading teaching letters." />;
  }
  if (error) {
    return <SurfaceError title="Teaching letters failed to load" detail={error} />;
  }
  if (!activeCase || !activeRun) {
    return <SurfaceEmpty message="No teaching letter is available." />;
  }

  const facts = clickableFacts(activeRun.facts ?? []);
  const selectedFact = factById(activeRun.facts ?? [], selectedFactId);
  const highlights = facts
    .filter((fact) => fact.span)
    .map((fact) => ({
      start: fact.span!.start,
      end: fact.span!.end,
      kind: highlightToneForFact(fact),
      label: fact.label,
      id: fact.fact_id,
      selected: fact.fact_id === selectedFactId,
    }));

  return (
    <SurfaceLayout variant="fill">
      <FiveCellGridTable />
      <AssemblyLineControls />
      <AssemblyLineStory />
      <ExplorerBody
        sourceLabel="Letter"
        sourceMeta={
          <span className="text-[11px] text-muted">
            {facts.length === 0
              ? `No predicted span to click · ${activeCase.letter_id}`
              : `Click a highlight · ${facts.length} predicted fact${facts.length === 1 ? "" : "s"}`}
          </span>
        }
        source={
          <LetterRenderer
            text={activeCase.note_text}
            highlights={highlights.map((span) => ({
              ...span,
              dim: Boolean(selectedFactId && !span.selected),
            }))}
            onHighlightSelect={setSelectedFactId}
          />
        }
        inspector={
          <AssemblyLineSidebar fact={selectedFact} fallbackGold={activeRun.gold_unit} />
        }
      />
    </SurfaceLayout>
  );
}
