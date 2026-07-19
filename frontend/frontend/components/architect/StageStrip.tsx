"use client";

import { Highlighter, Scale, Target, Wrench, Trophy, CheckCircle, XCircle } from "lucide-react";
import { useArchitectStore } from "@/lib/stores";
import { LensStrip, type LensItem } from "@/components/surface";
import type { DatasetTone } from "@/lib/datasets";
import type { TraceStage } from "@/lib/types";

const stages: { id: TraceStage; label: string; tone: DatasetTone; icon: React.ReactNode }[] = [
  { id: "extract", label: "Extract", tone: "deterministic", icon: <Highlighter className="h-3 w-3" /> },
  { id: "normalise", label: "Normalise", tone: "deterministic-alt", icon: <Scale className="h-3 w-3" /> },
  { id: "select", label: "Select", tone: "hybrid", icon: <Target className="h-3 w-3" /> },
  { id: "repair", label: "Repair", tone: "llm", icon: <Wrench className="h-3 w-3" /> },
  { id: "score", label: "Score", tone: "success", icon: <Trophy className="h-3 w-3" /> },
];

type Trace = NonNullable<ReturnType<typeof useArchitectStore.getState>["trace"]>;

function stageSummary(stage: TraceStage, trace: Trace): React.ReactNode {
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

function stageCount(stage: TraceStage, trace: Trace): number {
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
}

export default function StageStrip() {
  const activeStage = useArchitectStore((s) => s.activeStage);
  const trace = useArchitectStore((s) => s.trace);
  const setActiveStage = useArchitectStore((s) => s.setActiveStage);

  const items: LensItem[] = stages.map((stage) => ({
    id: stage.id,
    label: stage.label,
    tone: stage.tone,
    icon: stage.icon,
    count: trace ? stageCount(stage.id, trace) : undefined,
    sublabel: trace ? stageSummary(stage.id, trace) : "Awaiting trace",
  }));

  return (
    <LensStrip
      items={items}
      activeId={activeStage}
      onSelect={(id) => setActiveStage(id as TraceStage)}
      enabled={!!trace}
    />
  );
}
