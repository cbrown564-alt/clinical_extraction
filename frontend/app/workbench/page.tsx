"use client";

import { Suspense } from "react";
import { Tag } from "lucide-react";
import TraceControls from "@/components/architect/TraceControls";
import { useArchitectStore } from "@/lib/stores";
import StageStrip from "@/components/architect/StageStrip";
import StageInspector from "@/components/architect/StageInspector";
import ArchitectNoteRenderer from "@/components/architect/ArchitectNoteRenderer";

function SpecimenMeta() {
  const trace = useArchitectStore((s) => s.trace);
  const split = useArchitectStore((s) => s.split);
  const sourceRowIndex = useArchitectStore((s) => s.sourceRowIndex);

  if (!trace) {
    return (
      <span className="text-[10px] text-muted">
        No specimen loaded
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
  return (
    <div className="flex h-full flex-col bg-background">
      {/* Controls */}
      <TraceControls />

      {/* Stage strip */}
      <StageStrip />

      {/* Main content: Note + Inspector */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left — Note */}
        <div className="flex w-[55%] flex-col border-r border-border">
          <div className="flex items-center justify-between border-b border-border bg-surface-raised/50 px-4 py-1.5">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-muted">
              Specimen
            </span>
            <SpecimenMeta />
          </div>
          <div className="flex-1 overflow-y-auto p-6">
            <ArchitectNoteRenderer />
          </div>
        </div>

        {/* Right — Stage Inspector */}
        <div className="flex w-[45%] flex-col bg-surface">
          <StageInspector />
        </div>
      </div>
    </div>
  );
}

export default function WorkbenchPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center bg-background text-muted">
          <div className="text-center">
            <p className="text-lg font-medium">Loading workbench…</p>
          </div>
        </div>
      }
    >
      <WorkbenchInner />
    </Suspense>
  );
}
