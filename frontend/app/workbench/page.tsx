"use client";

import NoteRenderer from "@/components/workbench/NoteRenderer";
import StageNavigator from "@/components/workbench/StageNavigator";
import PipelineConfigPanel from "@/components/workbench/PipelineConfigPanel";
import { useUiStore, useConfigStore } from "@/lib/stores";
import { useLastRun } from "@/lib/hooks";
import { Microscope } from "lucide-react";

export default function WorkbenchPage() {
  const { activeStage, goldOverlay } = useUiStore();
  const { noteText } = useConfigStore();
  const lastRun = useLastRun();

  const result = lastRun.data;
  const diagnostics = result?.result.diagnostics;
  const goldLabel = result?.gold_label;

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border bg-surface px-4 py-2">
        <div className="flex items-center gap-2">
          <Microscope className="h-5 w-5 text-deterministic" />
          <h1 className="text-sm font-semibold text-foreground">
            Clinical Extraction Observatory
          </h1>
          <span className="rounded bg-surface-raised px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-muted">
            Workbench
          </span>
        </div>
        <div className="flex items-center gap-3 text-xs text-muted">
          <span>
            Stage:{" "}
            <span className="font-medium text-foreground">{activeStage}</span>
          </span>
          {result && (
            <span>
              Result:{" "}
              <span className="font-medium text-deterministic">
                {result.result.output.final_value}
              </span>
            </span>
          )}
        </div>
      </header>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left 60% - Note */}
        <div className="flex w-[60%] flex-col border-r border-border">
          <div className="flex items-center justify-between border-b border-border bg-surface-raised px-4 py-1.5">
            <span className="text-[11px] font-semibold uppercase tracking-wide text-muted">
              Specimen
            </span>
            <span className="text-[11px] text-muted">
              {noteText.length > 0
                ? `${noteText.length} chars`
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
            />
          </div>
        </div>

        {/* Right 40% - Stage Navigator + Config */}
        <div className="flex w-[40%] flex-col">
          <div className="flex-1 overflow-y-auto p-4">
            <div className="mb-4">
              <PipelineConfigPanel />
            </div>
            <div className="border-t border-border pt-4">
              <StageNavigator diagnostics={diagnostics} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
