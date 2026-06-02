"use client";

import { Suspense } from "react";
import { Telescope } from "lucide-react";
import { useObservatoryData } from "@/components/observatory/useObservatoryData";
import RunSelector from "@/components/observatory/RunSelector";
import RunLadder from "@/components/observatory/RunLadder";
import GeneralisationGap from "@/components/observatory/GeneralisationGap";
import ConfusionMatrix from "@/components/observatory/ConfusionMatrix";

function ObservatoryInner() {
  const {
    registry,
    registryLoading,
    selectedRunIds,
    selectedSummaries,
    loadingRuns,
    runErrors,
    toggleRun,
  } = useObservatoryData();

  const runs = registry?.runs ?? [];

  return (
    <div className="flex h-full flex-col bg-background">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border bg-surface px-5 py-2.5 shadow-sm z-10">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-llm-alt/10">
            <Telescope className="h-4 w-4 text-llm" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="rounded bg-surface-raised px-1.5 py-0 text-[10px] font-medium uppercase tracking-wider text-muted border border-border">
                Observatory
              </span>
              <span className="text-[10px] text-muted">
                Phase 3 — Corpus &amp; Ladder
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {registryLoading ? (
          <div className="flex h-full items-center justify-center text-muted">
            <div className="text-center">
              <p className="text-sm font-medium">Loading registry…</p>
            </div>
          </div>
        ) : (
          <div className="space-y-6 p-5">
            {/* Run Selector */}
            <RunSelector
              runs={runs}
              selectedIds={selectedRunIds}
              loadingIds={loadingRuns}
              errors={runErrors}
              onToggle={toggleRun}
            />

            {/* Run Ladder */}
            <RunLadder summaries={selectedSummaries} />

            {/* Generalisation Gap */}
            <GeneralisationGap summaries={selectedSummaries} />

            {/* Confusion Matrix */}
            <ConfusionMatrix summaries={selectedSummaries} />
          </div>
        )}
      </div>
    </div>
  );
}

export default function ObservatoryPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center bg-background text-muted">
          <div className="text-center">
            <p className="text-lg font-medium">Loading observatory…</p>
          </div>
        </div>
      }
    >
      <ObservatoryInner />
    </Suspense>
  );
}
