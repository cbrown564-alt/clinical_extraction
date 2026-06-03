"use client";

import { Highlighter, Scale, Target, Wrench, Trophy, CheckCircle, XCircle } from "lucide-react";
import { useArchitectStore } from "@/lib/stores";
import type { TraceStage } from "@/lib/types";

const stages: { id: TraceStage; label: string; icon: React.ReactNode }[] = [
  { id: "extract", label: "Extract", icon: <Highlighter className="h-3 w-3" /> },
  { id: "normalise", label: "Normalise", icon: <Scale className="h-3 w-3" /> },
  { id: "select", label: "Select", icon: <Target className="h-3 w-3" /> },
  { id: "repair", label: "Repair", icon: <Wrench className="h-3 w-3" /> },
  { id: "score", label: "Score", icon: <Trophy className="h-3 w-3" /> },
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

function stageSummary(stage: TraceStage, trace: NonNullable<ReturnType<typeof useArchitectStore.getState>["trace"]>): React.ReactNode {
  switch (stage) {
    case "extract": {
      const count = trace.extract.items.length;
      if (count === 0) return <span className="opacity-70">No candidates</span>;
      const groups = Array.from(new Set(trace.extract.items.map((i) => i.ruleGroup).filter(Boolean)));
      return (
        <span className="truncate">
          {count} candidate{count !== 1 ? "s" : ""}
          {groups.length > 0 && (
            <span className="opacity-70"> · {groups.length} group{groups.length !== 1 ? "s" : ""}</span>
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

  return (
    <div className="shrink-0 border-b border-border bg-surface px-4 py-2">
      <div className="flex items-stretch gap-1.5">
        {stages.map((stage) => {
          const isActive = stage.id === activeStage;
          const hasTrace = !!trace;
          const count = getCount(stage.id);

          return (
            <button
              key={stage.id}
              onClick={() => hasTrace && setActiveStage(stage.id)}
              disabled={!hasTrace}
              className={`flex flex-col justify-center gap-0.5 rounded-md border px-3 py-1.5 text-left transition-all min-w-[120px] flex-1 ${
                isActive
                  ? activeColor(stage.id)
                  : inactiveColor(hasTrace)
              }`}
            >
              <div className="flex items-center gap-1.5">
                {stage.icon}
                <span className="text-[11px] font-semibold">{stage.label}</span>
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
                <div className={`text-[10px] leading-tight ${isActive ? "text-white/90" : "text-muted"}`}>
                  {stageSummary(stage.id, trace)}
                </div>
              )}
              {!hasTrace && (
                <div className={`text-[10px] leading-tight ${isActive ? "text-white/70" : "text-muted"}`}>
                  Awaiting trace
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
