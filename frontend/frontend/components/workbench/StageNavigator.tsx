"use client";

import { useState } from "react";
import StageCard from "./StageCard";
import { useUiStore } from "@/lib/stores";
import type { PipelineDiagnostics } from "@/lib/types";

interface StageNavigatorProps {
  diagnostics?: PipelineDiagnostics;
}

const STAGES: Array<{
  id: import("@/lib/types").ActiveStage;
  label: string;
  description: string;
}> = [
  { id: "raw", label: "Raw", description: "Unmounted slide – no highlights" },
  { id: "extract", label: "Extract", description: "Candidate spans from rules" },
  { id: "normalise", label: "Normalise", description: "Normalized values per candidate" },
  { id: "select", label: "Select", description: "Final evidence selection" },
  { id: "score", label: "Score", description: "Gold comparison" },
];

export default function StageNavigator({ diagnostics }: StageNavigatorProps) {
  const { activeStage, setActiveStage } = useUiStore();
  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    raw: true,
    extract: true,
    normalise: true,
    select: true,
    score: true,
  });

  const toggleExpand = (id: string) =>
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));

  const candidates = diagnostics?.candidate_events ?? [];
  const normalized = diagnostics?.normalized_events ?? [];
  const finalSelection = diagnostics?.final_selection ?? {
    final_label: "–",
    rationale: "–",
    evidence: "–",
  };

  return (
    <div className="flex h-full flex-col gap-2.5 overflow-y-auto pr-1">
      <div className="flex items-center gap-2 border-b border-border pb-2">
        <div className="h-2 w-2 rounded-full bg-deterministic" />
        <h3 className="text-xs font-semibold uppercase tracking-widest text-muted">
          Stage Navigator
        </h3>
      </div>

      {STAGES.map((stage) => (
        <StageCard
          key={stage.id}
          stage={stage.id}
          label={stage.label}
          description={stage.description}
          isActive={activeStage === stage.id}
          isExpanded={expanded[stage.id] ?? false}
          onActivate={() => setActiveStage(stage.id)}
          onToggleExpand={() => toggleExpand(stage.id)}
          badge={
            stage.id === "extract"
              ? `${candidates.length} candidate${candidates.length !== 1 ? "s" : ""}`
              : stage.id === "normalise"
              ? `${normalized.length} event${normalized.length !== 1 ? "s" : ""}`
              : stage.id === "select"
              ? finalSelection.final_label
              : undefined
          }
          badgeColor={
            stage.id === "select"
              ? "bg-deterministic/10 text-deterministic border border-deterministic/20"
              : "bg-surface-raised text-muted border border-border"
          }
        >
          {stage.id === "extract" && (
            <div className="space-y-2">
              {candidates.length === 0 ? (
                <p className="text-xs text-muted italic">No candidates extracted.</p>
              ) : (
                candidates.map((c) => (
                  <div
                    key={c.event_id}
                    className="rounded-lg border border-border bg-surface-raised/60 p-2.5 text-xs transition-colors hover:bg-surface-raised"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="rounded-md bg-deterministic/10 px-1.5 py-0.5 font-mono text-[11px] font-medium text-deterministic">
                        {c.rule_id}
                      </span>
                      <span className="text-[11px] text-muted uppercase tracking-wide">
                        {c.rule_group}
                      </span>
                    </div>
                    <p className="font-medium text-foreground leading-relaxed">
                      {c.raw_value ?? c.evidence}
                    </p>
                    <p className="mt-0.5 text-muted italic">“{c.evidence}”</p>
                  </div>
                ))
              )}
            </div>
          )}

          {stage.id === "normalise" && (
            <div className="space-y-2">
              {normalized.length === 0 ? (
                <p className="text-xs text-muted italic">No normalized events.</p>
              ) : (
                normalized.map((n) => (
                  <div
                    key={n.event_id}
                    className="rounded-lg border border-border bg-surface-raised/60 p-2.5 text-xs transition-colors hover:bg-surface-raised"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-foreground">
                        {n.normalized_label}
                      </span>
                      <span className="rounded-md bg-surface px-2 py-0.5 font-mono text-[11px] text-muted border border-border">
                        {n.semantic_kind}
                      </span>
                    </div>
                    {n.validation_errors.length > 0 && (
                      <p className="mt-1.5 text-error text-xs">
                        {n.validation_errors.join("; ")}
                      </p>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {stage.id === "select" && (
            <div className="space-y-3 text-xs">
              <div className="rounded-lg border border-deterministic/20 bg-deterministic/5 p-3">
                <p className="font-semibold text-deterministic text-sm">
                  {finalSelection.final_label}
                </p>
                <p className="mt-1 text-muted leading-relaxed">{finalSelection.rationale}</p>
              </div>
            </div>
          )}

          {stage.id === "score" && (
            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between rounded-lg border border-border bg-surface-raised/60 p-2.5">
                <span className="text-muted">Evidence valid</span>
                <span
                  className={`rounded-md px-2 py-0.5 font-medium ${
                    diagnostics?.evidence_valid
                      ? "bg-success/10 text-success"
                      : "bg-error/10 text-error"
                  }`}
                >
                  {diagnostics?.evidence_valid ? "Yes" : "No"}
                </span>
              </div>
            </div>
          )}
        </StageCard>
      ))}
    </div>
  );
}
