"use client";

import { Suspense } from "react";
import { Microscope } from "lucide-react";
import TraceControls from "@/components/architect/TraceControls";
import StageStrip from "@/components/architect/StageStrip";
import StageInspector from "@/components/architect/StageInspector";
import ArchitectNoteRenderer from "@/components/architect/ArchitectNoteRenderer";

function WorkbenchInner() {
  return (
    <div className="flex h-full flex-col bg-background">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border bg-surface px-5 py-2.5 shadow-sm z-10">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-deterministic/10">
            <Microscope className="h-4 w-4 text-deterministic" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="rounded bg-surface-raised px-1.5 py-0 text-[10px] font-medium uppercase tracking-wider text-muted border border-border">
                Workbench
              </span>
              <span className="text-[10px] text-muted">
                Single-note inspector &amp; pipeline trace
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Controls */}
      <TraceControls />

      {/* Stage strip */}
      <StageStrip />

      {/* Main content: Note + Inspector */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left — Note */}
        <div className="flex w-[55%] flex-col border-r border-border">
          <div className="flex items-center justify-between border-b border-border bg-surface-raised/50 px-5 py-2">
            <span className="text-[11px] font-semibold uppercase tracking-widest text-muted">
              Specimen
            </span>
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
