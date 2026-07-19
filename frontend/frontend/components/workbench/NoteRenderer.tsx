"use client";

import { useMemo } from "react";
import { SourceDocument, type RenderSpan } from "@/components/surface";
import type { CandidateEvent, FinalSelection, HighlightSpan } from "@/lib/types";

interface NoteRendererProps {
  text: string;
  candidates: CandidateEvent[];
  finalSelection: FinalSelection;
  activeStage: string;
  goldOverlay?: boolean;
  goldLabel?: string;
  predictedLabel?: string;
}

function unescapeText(text: string): string {
  return text.replace(/\\n/g, "\n").replace(/\\t/g, "\t").replace(/\\r/g, "\r");
}

function getSpansForStage(
  text: string,
  candidates: CandidateEvent[],
  finalSelection: FinalSelection,
  activeStage: string
): HighlightSpan[] {
  const spans: HighlightSpan[] = [];

  if (activeStage === "raw") {
    return spans;
  }

  if (activeStage === "extract") {
    for (const c of candidates) {
      let start = c.start_char ?? -1;
      let end = c.end_char ?? -1;

      // Fallback: search for evidence text when char spans are missing
      if ((start < 0 || end <= start) && c.evidence && text) {
        const exactPos = text.indexOf(c.evidence);
        if (exactPos >= 0) {
          start = exactPos;
          end = exactPos + c.evidence.length;
        } else {
          const lowerText = text.toLowerCase();
          const lowerEvidence = c.evidence.toLowerCase();
          const ciPos = lowerText.indexOf(lowerEvidence);
          if (ciPos >= 0) {
            start = ciPos;
            end = ciPos + c.evidence.length;
          }
        }
      }

      if (start >= 0 && end > start) {
        const isNoReference = c.kind === "no_reference";
        spans.push({
          start,
          end,
          kind: isNoReference ? "no-reference" : "deterministic",
          label: c.raw_value ?? c.evidence,
          ruleId: c.rule_id,
          ruleGroup: c.rule_group,
          portability: c.portability,
          tooltip: isNoReference
            ? `No reference · ${c.rule_id}`
            : `${c.rule_id} (${c.rule_group ?? "unknown"})`,
        });
      }
    }
  }

  if (activeStage === "normalise") {
    for (const c of candidates) {
      if (c.start_char != null && c.end_char != null) {
        spans.push({
          start: c.start_char,
          end: c.end_char,
          kind: "deterministic-alt",
          label: c.raw_value ?? c.evidence,
          ruleId: c.rule_id,
          ruleGroup: c.rule_group,
          portability: c.portability,
          tooltip: `Normalised: ${c.raw_value ?? c.evidence}`,
        });
      }
    }
  }

  if (activeStage === "select" || activeStage === "score") {
    const fs = finalSelection;
    let start = fs.start_char ?? -1;
    let end = fs.end_char ?? -1;
    if (start < 0 || end <= start) {
      const idx = text.indexOf(fs.evidence);
      if (idx >= 0) {
        start = idx;
        end = idx + fs.evidence.length;
      }
    }
    if (start >= 0 && end > start) {
      const isSelect = activeStage === "select";
      spans.push({
        start,
        end,
        kind: isSelect ? "hybrid" : "success",
        label: fs.final_label,
        tooltip: `${isSelect ? "Selected" : "Scored"}: ${fs.final_label}`,
      });
    }
  }

  return spans;
}

export default function NoteRenderer({
  text,
  candidates,
  finalSelection,
  activeStage,
  goldOverlay,
  goldLabel,
  predictedLabel,
}: NoteRendererProps) {
  const cleanText = useMemo(() => unescapeText(text), [text]);

  const spans = useMemo<RenderSpan[]>(
    () =>
      getSpansForStage(cleanText, candidates, finalSelection, activeStage).map((s) => ({
        start: s.start,
        end: s.end,
        tone: s.kind,
        label: s.label,
        tooltip: s.tooltip,
        ruleId: s.ruleId,
        ruleGroup: s.ruleGroup,
        portability: s.portability,
      })),
    [cleanText, candidates, finalSelection, activeStage]
  );

  const goldMatch = useMemo(() => {
    if (!goldLabel || !predictedLabel) return undefined;
    return goldLabel.trim().toLowerCase() === predictedLabel.trim().toLowerCase();
  }, [goldLabel, predictedLabel]);

  if (!cleanText) {
    return (
      <div className="flex h-full items-center justify-center rounded-xl border border-dashed border-border bg-surface p-12 text-muted">
        <div className="text-center">
          <p className="text-lg font-medium">No specimen loaded</p>
          <p className="mt-1 text-sm">Select a dataset row or paste a clinical note to begin.</p>
        </div>
      </div>
    );
  }

  const goldOverlayClasses =
    goldMatch === true
      ? "border-success/30 bg-success/5 text-success/80"
      : goldMatch === false
      ? "border-error/30 bg-error/5 text-error/80"
      : "border-gold-ghost/30 bg-gold-ghost/5 text-gold-ghost/80";
  const goldIcon = goldMatch === true ? "✓" : goldMatch === false ? "✗" : "◆";

  return (
    <SourceDocument text={cleanText} spans={spans}>
      {goldOverlay && goldLabel && (
        <div className={`mt-6 rounded-lg border ${goldOverlayClasses} p-3`}>
          <p className="text-sm font-mono">
            <span className="font-semibold">{goldIcon} Gold label:</span> {goldLabel}
          </p>
          {goldMatch === false && predictedLabel && (
            <p className="mt-1 text-xs font-mono opacity-80">Predicted: {predictedLabel}</p>
          )}
        </div>
      )}
    </SourceDocument>
  );
}
