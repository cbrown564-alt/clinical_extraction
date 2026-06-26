"use client";

import { Suspense } from "react";
import { Tag } from "lucide-react";
import TraceControls from "@/components/architect/TraceControls";
import { useArchitectStore } from "@/lib/stores";
import { useArchitectUrlSync } from "@/lib/hooks";
import StageStrip from "@/components/architect/StageStrip";
import StageInspector from "@/components/architect/StageInspector";
import ArchitectNoteRenderer from "@/components/architect/ArchitectNoteRenderer";
import { useActiveDataset, getRuntimeAdapter } from "@/lib/datasets";
import { gan2026Dataset } from "@/lib/datasets/gan2026";
import { SurfaceHeader, SurfaceLayout, SurfaceLink, ExplorerBody } from "@/components/surface";

function PatientNoteMeta() {
  const trace = useArchitectStore((s) => s.trace);
  const split = useArchitectStore((s) => s.split);
  const sourceRowIndex = useArchitectStore((s) => s.sourceRowIndex);

  if (!trace) {
    return (
      <span className="text-[10px] text-muted">
        No patient note loaded
      </span>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {split && (
        <span className="text-[10px] text-muted uppercase tracking-wide">
          {split}
        </span>
      )}
      {sourceRowIndex !== null && (
        <span className="rounded bg-surface-raised px-1 py-0 font-mono text-[10px] text-muted border border-border">
          row {sourceRowIndex}
        </span>
      )}
      {trace.goldLabel && (
        <span className="flex items-center gap-1 text-[10px] text-gold-ghost">
          <Tag className="h-3 w-3" />
          {trace.goldLabel}
        </span>
      )}
      <span className="text-[10px] text-muted font-mono">
        {trace.noteText.length.toLocaleString()} chars
      </span>
    </div>
  );
}

function WorkbenchInner() {
  useArchitectUrlSync();
  return (
    <SurfaceLayout
      variant="fill"
      header={
        <SurfaceHeader
          surface="workbench"
          dataset={gan2026Dataset}
          description="Trace one note through the pipeline stage by stage: candidates, normalisation, selection, repair, and scoring."
          right={
            <>
              <SurfaceLink surface="observatory" datasetId="gan2026" label="Aggregate" />
              <SurfaceLink surface="gallery" datasetId="gan2026" label="Errors" />
            </>
          }
        />
      }
    >
      {/* Controls */}
      <TraceControls />

      {/* Stage strip */}
      <StageStrip />

      {/* Main content: Note + Inspector */}
      <ExplorerBody
        sourceLabel="Patient Note"
        sourceMeta={<PatientNoteMeta />}
        source={<ArchitectNoteRenderer />}
        inspector={<StageInspector />}
      />
    </SurfaceLayout>
  );
}

function WorkbenchRoute() {
  const dataset = useActiveDataset();
  const ExampleExplorer = getRuntimeAdapter(dataset).surfaces.ExampleExplorer;
  return <ExampleExplorer />;
}

export { WorkbenchInner as GanExampleExplorer };

export default function WorkbenchPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center bg-background text-muted">
          <div className="text-center">
            <p className="text-lg font-medium">Loading example explorer…</p>
          </div>
        </div>
      }
    >
      <WorkbenchRoute />
    </Suspense>
  );
}
