"use client";

import { BarChart3, LockKeyhole, Tag } from "lucide-react";
import TraceControls from "@/components/architect/TraceControls";
import { useArchitectStore } from "@/lib/stores";
import { useArchitectUrlSync } from "@/lib/hooks";
import StageStrip from "@/components/architect/StageStrip";
import StageInspector from "@/components/architect/StageInspector";
import ArchitectNoteRenderer from "@/components/architect/ArchitectNoteRenderer";
import { SurfaceLayout, ExplorerBody } from "@/components/surface";
import { isGanAggregateRunId } from "@/lib/ganPipelineOptions";

function PatientNoteMeta({ aggregateOnly }: { aggregateOnly: boolean }) {
  const trace = useArchitectStore((s) => s.trace);
  const split = useArchitectStore((s) => s.split);
  const sourceRowIndex = useArchitectStore((s) => s.sourceRowIndex);

  if (aggregateOnly) {
    return <span className="text-[11px] text-muted">test450 · letters sealed</span>;
  }

  if (!trace) {
    return (
      <span className="text-[11px] text-muted">
        No letter loaded
      </span>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {split && (
        <span className="text-[11px] text-muted uppercase tracking-wide">
          {split}
        </span>
      )}
      {sourceRowIndex !== null && (
        <span className="rounded bg-surface-raised px-1 py-0 font-mono text-[11px] text-muted border border-border">
          letter {sourceRowIndex}
        </span>
      )}
      {trace.goldLabel && (
        <span className="flex items-center gap-1 text-[11px] text-gold-ghost">
          <Tag className="h-3 w-3" />
          {trace.goldLabel}
        </span>
      )}
      <span className="text-[11px] text-muted font-mono">
        {trace.noteText.length.toLocaleString()} chars
      </span>
    </div>
  );
}

function AggregateInspector() {
  return (
    <div className="flex h-full items-center justify-center p-6">
      <div className="max-w-sm rounded-lg border border-hybrid/20 bg-hybrid/5 p-5">
        <div className="mb-3 flex items-center gap-2 text-hybrid">
          <BarChart3 className="h-4 w-4" />
          <h3 className="text-sm font-semibold">Aggregate evidence</h3>
        </div>
        <p className="text-sm leading-6 text-foreground">
          This gan_llm_extract_raw condition retains Purist and Pragmatic totals across 450 test rows.
        </p>
        <div className="mt-3 flex items-start gap-2 text-xs leading-5 text-muted">
          <LockKeyhole className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <p>
            Letter identifiers, notes, predictions, and traces remain sealed. Choose
            Deterministic rules for an inspectable validation trace.
          </p>
        </div>
      </div>
    </div>
  );
}

export function GanExampleExplorer() {
  useArchitectUrlSync();
  const selectedRunId = useArchitectStore((state) => state.selectedRunId);
  const aggregateOnly = isGanAggregateRunId(selectedRunId);
  return (
    <SurfaceLayout variant="fill">
      <TraceControls />
      <StageStrip />
      <ExplorerBody
        sourceLabel="Letter"
        sourceMeta={<PatientNoteMeta aggregateOnly={aggregateOnly} />}
        source={
          <ArchitectNoteRenderer
            emptyState={
              aggregateOnly
                ? {
                    title: "Letter-level evidence is sealed",
                    description:
                      "This condition supports aggregate comparison only. Choose Deterministic rules to inspect a validation letter.",
                  }
                : undefined
            }
          />
        }
        inspector={aggregateOnly ? <AggregateInspector /> : <StageInspector />}
      />
    </SurfaceLayout>
  );
}
