"use client";

import { useState } from "react";
import StageCard from "./StageCard";
import { useUiStore } from "@/lib/stores";
import type { PipelineDiagnostics } from "@/lib/types";
import AttributionWaterfall from "./AttributionWaterfall";

interface StageNavigatorProps {
  diagnostics?: PipelineDiagnostics;
}

const STAGES: Array<{
  id: import("@/lib/types").ActiveStage;
  label: string;
  description: string;
}> = [
  { id: "raw", label: "Raw", description: "Unmounted slide — no highlights" },
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
    final_label: "—",
    rationale: "—",
    evidence: "—",
  };

  return (
    <div className="flex h-full flex-col gap-3 overflow-y-auto pr-1">
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
              ? `${candidates.length} candidates`
              : stage.id === "normalise"
              ? `${normalized.length} events`
              : stage.id === "select"
              ? finalSelection.final_label
              : undefined
          }
          badgeColor={
            stage.id === "select"
              ? "bg-deterministic/10 text-deterministic"
              : undefined
          }
        >
          {stage.id === "extract" && (
            <div className="space-y-2">
              {candidates.length === 0 ? (
                <p className="text-xs text-muted">No candidates extracted.</p>
              ) : (
                candidates.map((c) => (
                  <div
                    key={c.event_id}
                    className="rounded border border-border bg-surface-raised p-2 text-xs"
                  >
                    <div className="flex items-center gap-2">
                      <span className="rounded bg-deterministic/10 px-1.5 py-0.5 font-mono text-deterministic">
                        {c.rule_id}
                      </span>
                      <span className="text-muted">{c.rule_group}</span>
                    </div>
                    <p className="mt-1 font-medium text-foreground">
                      {c.raw_value ?? c.evidence}
                    </p>
                    <p className="text-muted">“{c.evidence}”</p>
                  </div>
                ))
              )}
            </div>
          )}

          {stage.id === "normalise" && (
            <div className="space-y-2">
              {normalized.length === 0 ? (
                <p className="text-xs text-muted">No normalized events.</p>
              ) : (
                normalized.map((n) => (
                  <div
                    key={n.event_id}
                    className="rounded border border-border bg-surface-raised p-2 text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-foreground">
                        {n.normalized_label}
                      </span>
                      <span className="rounded bg-surface px-1.5 py-0.5 font-mono text-muted">
                        {n.semantic_kind}
                      </span>
                    </div>
                    {n.validation_errors.length > 0 && (
                      <p className="mt-1 text-error">
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
              <div className="rounded border border-deterministic/20 bg-deterministic/5 p-2">
                <p className="font-semibold text-deterministic">
                  {finalSelection.final_label}
                </p>
                <p className="mt-1 text-muted">{finalSelection.rationale}</p>
              </div>
              <AttributionWaterfall diagnostics={diagnostics} />
            </div>
          )}

          {stage.id === "score" && (
            <div className="text-xs text-muted">
              <p>
                Evidence valid:{" "}
                <span
                  className={
                    diagnostics?.evidence_valid
                      ? "text-success"
                      : "text-error"
                  }
                >
                  {diagnostics?.evidence_valid ? "Yes" : "No"}
                </span>
              </p>
            </div>
          )}
        </StageCard>
      ))}
    </div>
  );
}
