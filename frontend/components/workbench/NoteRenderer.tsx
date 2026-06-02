"use client";

import { useMemo } from "react";
import type { CandidateEvent, FinalSelection, HighlightSpan } from "@/lib/types";

interface NoteRendererProps {
  text: string;
  candidates: CandidateEvent[];
  finalSelection: FinalSelection;
  activeStage: string;
  goldOverlay?: boolean;
  goldLabel?: string;
}

function buildSegments(
  text: string,
  spans: HighlightSpan[]
): Array<{ start: number; end: number; spans: HighlightSpan[] }> {
  const points = new Set<number>([0, text.length]);
  for (const span of spans) {
    points.add(Math.max(0, span.start));
    points.add(Math.min(text.length, span.end));
  }
  const sorted = Array.from(points).sort((a, b) => a - b);
  const segments: Array<{ start: number; end: number; spans: HighlightSpan[] }> = [];
  for (let i = 0; i < sorted.length - 1; i++) {
    const start = sorted[i];
    const end = sorted[i + 1];
    const activeSpans = spans.filter(
      (s) => s.start < end && s.end > start
    );
    if (activeSpans.length > 0 || end - start > 0) {
      segments.push({ start, end, spans: activeSpans });
    }
  }
  return segments;
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

  if (activeStage === "extract" || activeStage === "normalise") {
    for (const c of candidates) {
      if (c.start_char != null && c.end_char != null) {
        spans.push({
          start: c.start_char,
          end: c.end_char,
          kind: "deterministic",
          label: c.raw_value ?? c.evidence,
          ruleId: c.rule_id,
          ruleGroup: c.rule_group,
          tooltip: `${c.rule_id} (${c.rule_group ?? "unknown"})`,
        });
      }
    }
  }

  if (activeStage === "select" || activeStage === "score") {
    // Highlight the final selection. Fallback to text search if start_char/end_char missing.
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
      spans.push({
        start,
        end,
        kind: "deterministic",
        label: fs.final_label,
        tooltip: `Selected: ${fs.final_label}`,
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
}: NoteRendererProps) {
  const spans = useMemo(
    () => getSpansForStage(text, candidates, finalSelection, activeStage),
    [text, candidates, finalSelection, activeStage]
  );

  const segments = useMemo(() => buildSegments(text, spans), [text, spans]);

  if (!text) {
    return (
      <div className="rounded-lg border border-border bg-surface p-8 text-muted">
        No note loaded. Enter text and run the pipeline.
      </div>
    );
  }

  return (
    <div className="relative rounded-lg border border-border bg-surface p-6 shadow-sm">
      <div className="note-text whitespace-pre-wrap">
        {segments.map((seg, i) => {
          const content = text.slice(seg.start, seg.end);
          if (seg.spans.length === 0) {
            return <span key={i}>{content}</span>;
          }

          const primary = seg.spans[0];
          const kindClass =
            primary.kind === "deterministic"
              ? "span-highlight--deterministic"
              : primary.kind === "llm"
              ? "span-highlight--llm"
              : primary.kind === "repair"
              ? "span-highlight--repair"
              : "";

          return (
            <mark
              key={i}
              className={`span-highlight ${kindClass} rounded-sm`}
              title={primary.tooltip}
            >
              {content}
            </mark>
          );
        })}
      </div>

      {goldOverlay && goldLabel && (
        <div className="mt-6 rounded-md border border-gold-ghost/30 bg-gold-ghost/5 p-3">
          <p className="text-sm font-mono text-gold-ghost/80">
            <span className="font-semibold">Gold label:</span> {goldLabel}
          </p>
        </div>
      )}
    </div>
  );
}
