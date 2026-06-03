"use client";

import { GitBranch, Layers, Settings2, Wrench, Award, CheckCircle, XCircle, Minus, Quote } from "lucide-react";
import { useArchitectStore } from "@/lib/stores";
import type { TraceStage } from "@/lib/types";

const stages: { id: TraceStage; label: string; icon: React.ReactNode }[] = [
  { id: "extract", label: "Extract", icon: <GitBranch className="h-3.5 w-3.5" /> },
  { id: "normalise", label: "Normalise", icon: <Layers className="h-3.5 w-3.5" /> },
  { id: "select", label: "Select", icon: <Settings2 className="h-3.5 w-3.5" /> },
  { id: "repair", label: "Repair", icon: <Wrench className="h-3.5 w-3.5" /> },
  { id: "score", label: "Score", icon: <Award className="h-3.5 w-3.5" /> },
];

function activeColor(stage: TraceStage): string {
  switch (stage) {
    case "extract":
      return "bg-deterministic text-white border-deterministic shadow-sm";
    case "normalise":
      return "bg-deterministic-alt text-white border-deterministic-alt shadow-sm";
    case "select":
      return "bg-hybrid text-white border-hybrid shadow-sm";
    case "repair":
      return "bg-llm text-white border-llm shadow-sm";
    case "score":
      return "bg-success text-white border-success shadow-sm";
  }
}

function inactiveColor(traceLoaded: boolean): string {
  if (!traceLoaded) {
    return "bg-surface-raised/50 text-muted border-border/60 cursor-default";
  }
  return "bg-surface text-foreground border-border hover:bg-surface-raised hover:border-border hover:shadow-sm";
}

function stageBorderColor(stage: TraceStage): string {
  switch (stage) {
    case "extract":
      return "border-l-deterministic";
    case "normalise":
      return "border-l-deterministic-alt";
    case "select":
      return "border-l-hybrid";
    case "repair":
      return "border-l-llm";
    case "score":
      return "border-l-success";
  }
}

function stageEvidence(stage: TraceStage, trace: NonNullable<ReturnType<typeof useArchitectStore.getState>["trace"]>): string | null {
  switch (stage) {
    case "extract": {
      const first = trace.extract.items[0];
      return first?.evidence ?? null;
    }
    case "normalise": {
      const first = trace.normalise.items[0];
      return first?.evidence ?? null;
    }
    case "select":
      return trace.select.evidence || null;
    case "repair": {
      const changes = trace.repair?.changes ?? [];
      if (changes.length === 0) return "No repair changes applied.";
      return changes[0];
    }
    case "score":
      return trace.select.evidence || null;
  }
}

function stageSummary(stage: TraceStage, trace: NonNullable<ReturnType<typeof useArchitectStore.getState>["trace"]>): React.ReactNode {
  switch (stage) {
    case "extract": {
      const count = trace.extract.items.length;
      if (count === 0) return <span className="opacity-70">No candidates</span>;
      const first = trace.extract.items[0];
      const groups = Array.from(new Set(trace.extract.items.map((i) => i.ruleGroup).filter(Boolean)));
      return (
        <span className="truncate">
          {count} candidate{count !== 1 ? "s" : ""}
          {groups.length > 0 && (
            <span className="opacity-70"> · {groups.length} rule group{groups.length !== 1 ? "s" : ""}</span>
          )}
        </span>
      );
    }
    case "normalise": {
      const count = trace.normalise.items.length;
      if (count === 0) return <span className="opacity-70">No events</span>;
      const firstLabel = trace.normalise.items[0]?.normalizedValue ?? trace.normalise.items[0]?.rawValue;
      return (
        <span className="truncate">
          {count} event{count !== 1 ? "s" : ""}
          {firstLabel && <span className="opacity-70"> · {firstLabel}</span>}
        </span>
      );
    }
    case "select": {
      const label = trace.select.finalLabel;
      const count = trace.select.selectedIds?.length ?? 0;
      return (
        <span className="truncate">
          {label}
          {count > 0 && <span className="opacity-70"> · {count} selected</span>}
        </span>
      );
    }
    case "repair": {
      const changes = trace.repair?.changes.length ?? 0;
      if (changes === 0) return <span className="opacity-70">No changes</span>;
      const before = trace.repair?.beforeLabel;
      const after = trace.repair?.afterLabel;
      return (
        <span className="truncate">
          {changes} change{changes !== 1 ? "s" : ""}
          {before && after && <span className="opacity-70"> · {before} → {after}</span>}
        </span>
      );
    }
    case "score": {
      const match = trace.score.match;
      const predicted = trace.score.predictedLabel;
      return (
        <span className="flex items-center gap-1 truncate">
          {match ? (
            <>
              <CheckCircle className="h-3 w-3 opacity-80" />
              <span>Match · {predicted}</span>
            </>
          ) : (
            <>
              <XCircle className="h-3 w-3 opacity-80" />
              <span>Mismatch · {predicted}</span>
            </>
          )}
        </span>
      );
    }
  }
}

export default function StageStrip() {
  const activeStage = useArchitectStore((s) => s.activeStage);
  const trace = useArchitectStore((s) => s.trace);
  const setActiveStage = useArchitectStore((s) => s.setActiveStage);

  const getCount = (stage: TraceStage): number | null => {
    if (!trace) return null;
    switch (stage) {
      case "extract":
        return trace.extract.items.length;
      case "normalise":
        return trace.normalise.items.length;
      case "select":
        return 1;
      case "repair":
        return trace.repair ? trace.repair.changes.length : 0;
      case "score":
        return trace.score.match ? 1 : 0;
    }
  };

  const evidenceQuote = trace ? stageEvidence(activeStage, trace) : null;

  return (
    <div className="shrink-0 border-b border-border bg-surface px-4 py-2.5 space-y-2">
      <div className="flex items-stretch gap-2">
        {stages.map((stage, idx) => {
          const isActive = stage.id === activeStage;
          const hasTrace = !!trace;
          const count = getCount(stage.id);

          return (
            <div key={stage.id} className="flex items-center gap-2">
              <button
                onClick={() => hasTrace && setActiveStage(stage.id)}
                disabled={!hasTrace}
                className={`flex flex-col justify-center gap-0.5 rounded-lg border px-4 py-2.5 text-left transition-all min-w-[140px] flex-1 ${
                  isActive
                    ? activeColor(stage.id)
                    : inactiveColor(hasTrace)
                }`}
              >
                <div className="flex items-center gap-1.5">
                  {stage.icon}
                  <span className="text-xs font-semibold">{stage.label}</span>
                  {hasTrace && count !== null && (
                    <span
                      className={`ml-0.5 rounded-full px-1.5 py-0 text-[10px] font-semibold ${
                        isActive
                          ? "bg-white/25 text-white"
                          : "bg-surface-raised text-muted"
                      }`}
                    >
                      {count}
                    </span>
                  )}
                </div>
                {hasTrace && trace && (
                  <div className={`text-[11px] leading-tight ${isActive ? "text-white/90" : "text-muted"}`}>
                    {stageSummary(stage.id, trace)}
                  </div>
                )}
                {!hasTrace && (
                  <div className={`text-[11px] leading-tight ${isActive ? "text-white/70" : "text-muted"}`}>
                    <span className="flex items-center gap-1">
                      <Minus className="h-3 w-3" />
                      Awaiting trace
                    </span>
                  </div>
                )}
              </button>
              {idx < stages.length - 1 && (
                <div
                  className={`h-px w-4 self-center ${
                    isActive ? "bg-border" : "bg-border/50"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Evidence callout — subtle but persistent */}
      {evidenceQuote && (
        <div className={`flex items-start gap-2 rounded-md border border-border bg-surface-raised/40 pl-3 pr-3 py-1.5 border-l-2 ${stageBorderColor(activeStage)}`}>
          <Quote className="mt-0.5 h-3 w-3 shrink-0 text-muted" />
          <span className="text-[11px] italic text-muted leading-snug truncate">
            {evidenceQuote}
          </span>
        </div>
      )}
    </div>
  );
}
