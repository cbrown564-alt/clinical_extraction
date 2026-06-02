"use client";

import { GitBranch, Layers, Settings2, Wrench, Award } from "lucide-react";
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
    <div className="shrink-0 border-b border-border bg-surface px-4 py-2.5">
      <div className="flex items-center gap-2">
        {stages.map((stage, idx) => {
          const isActive = stage.id === activeStage;
          const hasTrace = !!trace;
          const count = getCount(stage.id);

          return (
            <div key={stage.id} className="flex items-center gap-2">
              <button
                onClick={() => hasTrace && setActiveStage(stage.id)}
                disabled={!hasTrace}
                className={`flex items-center gap-1.5 rounded-lg border px-3.5 py-2 text-xs font-medium transition-all ${
                  isActive
                    ? activeColor(stage.id)
                    : inactiveColor(hasTrace)
                }`}
              >
                {stage.icon}
                <span>{stage.label}</span>
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
              </button>
              {idx < stages.length - 1 && (
                <div
                  className={`h-px w-5 ${
                    isActive ? "bg-border" : "bg-border/50"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
