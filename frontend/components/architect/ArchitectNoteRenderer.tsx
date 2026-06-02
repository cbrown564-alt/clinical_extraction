"use client";

import NoteRenderer from "@/components/workbench/NoteRenderer";
import { useArchitectStore } from "@/lib/stores";
import type { CandidateEvent, FinalSelection } from "@/lib/types";

function traceItemsToCandidates(items: { id: string; kind: string; rawValue: string; evidence: string; startChar: number | null; endChar: number | null; ruleId?: string; ruleGroup?: string | null; portability?: string | null }[]): CandidateEvent[] {
  return items.map((item) => ({
    event_id: item.id,
    kind: item.kind,
    raw_value: item.rawValue,
    evidence: item.evidence,
    start_char: item.startChar,
    end_char: item.endChar,
    rule_id: item.ruleId ?? "unknown",
    rule_group: item.ruleGroup ?? null,
    portability: item.portability ?? null,
    match_groups: {},
  }));
}

export default function ArchitectNoteRenderer() {
  const trace = useArchitectStore((s) => s.trace);
  const activeStage = useArchitectStore((s) => s.activeStage);

  if (!trace) {
    return (
      <div className="flex h-full items-center justify-center rounded-xl border border-dashed border-border bg-surface p-12 text-muted">
        <div className="text-center">
          <p className="text-lg font-medium">No specimen loaded</p>
          <p className="mt-1 text-sm">Select a row and run the pipeline to see the note.</p>
        </div>
      </div>
    );
  }

  // Build candidates and finalSelection from trace data for the current stage
  let candidates: CandidateEvent[] = [];
  let finalSelection: FinalSelection = {
    final_label: trace.select.finalLabel,
    rationale: trace.select.rationale,
    evidence: trace.select.evidence,
    start_char: null,
    end_char: null,
    monthly_frequency: trace.select.monthlyFrequency,
  };

  if (activeStage === "extract") {
    candidates = traceItemsToCandidates(trace.extract.items);
  } else if (activeStage === "normalise") {
    candidates = traceItemsToCandidates(trace.normalise.items);
  } else if (activeStage === "select" || activeStage === "repair" || activeStage === "score") {
    // For select/score, use the select stage's evidence
    // Find the evidence span in the note text
    const evidence = trace.select.evidence;
    if (evidence && trace.noteText) {
      const idx = trace.noteText.indexOf(evidence);
      if (idx >= 0) {
        finalSelection = {
          ...finalSelection,
          start_char: idx,
          end_char: idx + evidence.length,
        };
      }
    }
  }

  return (
    <NoteRenderer
      text={trace.noteText}
      candidates={candidates}
      finalSelection={finalSelection}
      activeStage={activeStage}
      goldLabel={trace.goldLabel}
      predictedLabel={trace.score.predictedLabel}
    />
  );
}
