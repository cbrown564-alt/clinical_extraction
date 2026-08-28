"use client";

import { useEffect } from "react";
import { Highlighter, Scale, Target, Trophy, CheckCircle, XCircle } from "lucide-react";
import { useArchitectStore } from "@/lib/stores";
import { LensStrip, type LensItem } from "@/components/surface";
import type { DatasetTone } from "@/lib/datasets";
import type { TraceStage } from "@/lib/types";

const stages: { id: TraceStage; label: string; tone: DatasetTone; icon: React.ReactNode }[] = [
  { id: "extract", label: "Recognise", tone: "deterministic", icon: <Highlighter className="h-3 w-3" /> },
  { id: "normalise", label: "Encode", tone: "deterministic-alt", icon: <Scale className="h-3 w-3" /> },
  { id: "select", label: "Select", tone: "hybrid", icon: <Target className="h-3 w-3" /> },
  { id: "score", label: "Score", tone: "success", icon: <Trophy className="h-3 w-3" /> },
];

type Trace = NonNullable<ReturnType<typeof useArchitectStore.getState>["trace"]>;

function stageSummary(stage: TraceStage, trace: Trace): React.ReactNode {
  switch (stage) {
    case "extract": {
      const count = trace.extract.items.length;
      if (count === 0) return <span className="opacity-70">No candidates</span>;
      if (trace.extract.items.every((item) => item.kind === "llm_decision")) {
        return <span className="truncate">Model decision · {trace.extract.items[0].rawValue}</span>;
      }
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
      if (trace.select.isDistinctStage === false) {
        return <span className="opacity-70">Combined with Recognise</span>;
      }
      const label = trace.select.finalLabel;
      const count = trace.select.selectedIds?.length ?? 0;
      return (
        <span className="truncate">
          {label}
          {count > 0 && <span className="opacity-70"> · {count} selected</span>}
        </span>
      );
    }
    case "repair":
      return null;
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

function stageSummaryText(stage: TraceStage, trace: Trace): string {
  switch (stage) {
    case "extract": {
      const count = trace.extract.items.length;
      if (count === 0) return "No candidates";
      if (trace.extract.items.every((item) => item.kind === "llm_decision")) {
        return `Model decision · ${trace.extract.items[0].rawValue ?? ""}`.trim();
      }
      const groups = Array.from(new Set(trace.extract.items.map((i) => i.ruleGroup).filter(Boolean)));
      return groups.length > 0
        ? `${count} candidate${count !== 1 ? "s" : ""} · ${groups.length} group${groups.length !== 1 ? "s" : ""}`
        : `${count} candidate${count !== 1 ? "s" : ""}`;
    }
    case "normalise": {
      const count = trace.normalise.items.length;
      if (count === 0) return "No events";
      const firstLabel = trace.normalise.items[0]?.normalizedValue ?? trace.normalise.items[0]?.rawValue;
      return firstLabel ? `${count} event${count !== 1 ? "s" : ""} · ${firstLabel}` : `${count} event${count !== 1 ? "s" : ""}`;
    }
    case "select": {
      if (trace.select.isDistinctStage === false) return "Combined with Recognise";
      const label = trace.select.finalLabel ?? "";
      const count = trace.select.selectedIds?.length ?? 0;
      return count > 0 ? `${label} · ${count} selected` : label;
    }
    case "repair":
      return "";
    case "score": {
      const predicted = trace.score.predictedLabel ?? "";
      return trace.score.match ? `Match · ${predicted}` : `Mismatch · ${predicted}`;
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
      return trace.select.isDistinctStage === false ? 0 : 1;
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

  useEffect(() => {
    if (activeStage === "repair") {
      setActiveStage("select");
    }
  }, [activeStage, setActiveStage]);

  const items: LensItem[] = stages.map((stage) => ({
    id: stage.id,
    label: stage.label,
    tone: stage.tone,
    icon: stage.icon,
    count: trace ? stageCount(stage.id, trace) : undefined,
    sublabel: trace ? stageSummary(stage.id, trace) : "Awaiting trace",
    title: trace ? stageSummaryText(stage.id, trace) : undefined,
    disabled: stage.id === "select" && trace?.select.isDistinctStage === false,
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
