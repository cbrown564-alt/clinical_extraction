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

  const getColor = (stage: TraceStage): string => {
    if (stage === activeStage) {
      if (stage === "extract") return "bg-deterministic text-white border-deterministic";
      if (stage === "normalise") return "bg-deterministic-alt text-white border-deterministic-alt";
      if (stage === "select") return "bg-hybrid text-white border-hybrid";
      if (stage === "repair") return "bg-llm text-white border-llm";
      return "bg-success text-white border-success";
    }
    if (!trace) return "bg-surface-raised text-muted border-border";
    return "bg-surface text-foreground border-border hover:bg-surface-raised";
  };

  return (
    <div className="shrink-0 border-b border-border bg-surface px-4 py-2">
      <div className="flex items-center gap-1">
        {stages.map((stage, idx) => (
          <div key={stage.id} className="flex items-center gap-1">
            <button
              onClick={() => setActiveStage(stage.id)}
              className={`flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium transition-all ${getColor(stage.id)}`}
            >
              {stage.icon}
              <span>{stage.label}</span>
              {trace && getCount(stage.id) !== null && (
                <span className="ml-0.5 rounded-full bg-white/20 px-1.5 py-0 text-[10px] font-semibold">
                  {getCount(stage.id)}
                </span>
              )}
            </button>
            {idx < stages.length - 1 && (
              <div className="mx-1 h-px w-4 bg-border" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
