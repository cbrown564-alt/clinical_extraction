"use client";

import { Suspense } from "react";
import NoteRenderer from "@/components/workbench/NoteRenderer";
import StageNavigator from "@/components/workbench/StageNavigator";
import PipelineConfigPanel from "@/components/workbench/PipelineConfigPanel";
import { useUiStore, useConfigStore } from "@/lib/stores";
import { useLastRun, useRecord, useWorkbenchUrlSync } from "@/lib/hooks";
import { Activity, GitCompare } from "lucide-react";

function WorkbenchInner() {
  useWorkbenchUrlSync();

  const { activeStage, goldOverlay, showDiff } = useUiStore();
  const { noteText, split, sourceRowIndex } = useConfigStore();
  const lastRun = useLastRun();
  const recordQuery = useRecord(split, sourceRowIndex);

  const result = lastRun;
  const diagnostics = result?.result.diagnostics;
  // Gold label from dataset record (if loaded) or from last pipeline run
  const goldLabel = recordQuery.data?.gold_label ?? result?.gold_label;

  return (
    <div className="flex h-full flex-col bg-background">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border bg-surface px-5 py-2.5 shadow-sm z-10">
        <div className="flex items-center gap-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="rounded bg-surface-raised px-1.5 py-0 text-[10px] font-medium uppercase tracking-wider text-muted border border-border">
                Workbench
              </span>
              <span className="text-[10px] text-muted">
                Phase 1 — Single-note inspector
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4 text-xs">
          {showDiff && (
            <div className="flex items-center gap-1.5 rounded-md bg-hybrid/10 px-2 py-0.5 border border-hybrid/20">
              <GitCompare className="h-3.5 w-3.5 text-hybrid" />
              <span className="font-medium text-hybrid">Compare mode</span>
            </div>
          )}
          <div className="flex items-center gap-1.5">
            <Activity className="h-3.5 w-3.5 text-muted" />
            <span className="text-muted">Stage:</span>
            <span className="rounded-md bg-surface-raised px-2 py-0.5 font-mono text-[11px] font-medium text-foreground border border-border">
              {activeStage}
            </span>
          </div>
          {result && (
            <div className="flex items-center gap-1.5">
              <span className="text-muted">Result:</span>
              <span className="rounded-md bg-deterministic/10 px-2 py-0.5 font-mono text-[11px] font-medium text-deterministic border border-deterministic/20">
                {result.result.output.final_value}
              </span>
            </div>
          )}
        </div>
      </header>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left — Note */}
        <div className="flex w-[60%] flex-col border-r border-border">
          <div className="flex items-center justify-between border-b border-border bg-surface-raised/50 px-5 py-2">
            <span className="text-[11px] font-semibold uppercase tracking-widest text-muted">
              Specimen
            </span>
            <span className="text-[11px] text-muted font-mono">
              {noteText.length > 0
                ? `${noteText.length.toLocaleString()} chars`
                : "No note loaded"}
            </span>
          </div>
          <div className="flex-1 overflow-y-auto p-6">
            <NoteRenderer
              text={noteText}
              candidates={diagnostics?.candidate_events ?? []}
              finalSelection={diagnostics?.final_selection ?? { final_label: "—", rationale: "—", evidence: "—" }}
              activeStage={activeStage}
              goldOverlay={goldOverlay}
              goldLabel={goldLabel}
              predictedLabel={result?.result.output.final_value}
            />
          </div>
        </div>

        {/* Right — Config + Navigator */}
        <div className="flex w-[40%] flex-col bg-surface">
          <div className="flex-1 overflow-y-auto p-5">
            <div className="mb-6">
              <PipelineConfigPanel />
            </div>
            <div className="border-t border-border pt-5">
              <StageNavigator diagnostics={diagnostics} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function WorkbenchPage() {
  return (
    <Suspense fallback={
      <div className="flex h-full items-center justify-center bg-background text-muted">
        <div className="text-center">
          <p className="text-lg font-medium">Loading workbench…</p>
        </div>
      </div>
    }>
      <WorkbenchInner />
    </Suspense>
  );
}
