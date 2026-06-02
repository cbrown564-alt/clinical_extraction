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

function unescapeText(text: string): string {
  return text
    .replace(/\\n/g, "\n")
    .replace(/\\t/g, "\t")
    .replace(/\\r/g, "\r");
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
    const activeSpans = spans.filter((s) => s.start < end && s.end > start);
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

function formatNoteAsLetter(text: string): React.ReactNode {
  const paragraphs = text.split(/\n{2,}/).filter((p) => p.trim().length > 0);

  return paragraphs.map((para, i) => {
    const lines = para.split("\n").filter((l) => l.trim().length > 0);
    const isHeader =
      i === 0 &&
      (lines[0]?.includes("Department") ||
        lines[0]?.includes("Hospital") ||
        lines[0]?.includes("Clinic Date"));
    const isClosing =
      lines.some((l) => /^yours\s+sincerely/i.test(l.trim())) ||
      lines.some((l) => /^best\s+wishes/i.test(l.trim())) ||
      lines.some((l) => /^regards/i.test(l.trim()));

    if (isHeader) {
      return (
        <div
          key={i}
          className="mb-6 border-b border-border pb-4 text-sm leading-relaxed text-muted"
        >
          {lines.map((line, j) => (
            <div key={j}>{line.trim()}</div>
          ))}
        </div>
      );
    }

    if (isClosing) {
      return (
        <div key={i} className="mt-8 text-sm text-muted">
          {lines.map((line, j) => (
            <div key={j}>{line.trim()}</div>
          ))}
        </div>
      );
    }

    return (
      <p key={i} className="mb-4">
        {lines.map((line, j) => (
          <span key={j}>
            {line.trim()}
            {j < lines.length - 1 && <br />}
          </span>
        ))}
      </p>
    );
  });
}

export default function NoteRenderer({
  text,
  candidates,
  finalSelection,
  activeStage,
  goldOverlay,
  goldLabel,
}: NoteRendererProps) {
  const cleanText = useMemo(() => unescapeText(text), [text]);

  const spans = useMemo(
    () => getSpansForStage(cleanText, candidates, finalSelection, activeStage),
    [cleanText, candidates, finalSelection, activeStage]
  );

  const segments = useMemo(() => buildSegments(cleanText, spans), [cleanText, spans]);

  if (!cleanText) {
    return (
      <div className="flex h-full items-center justify-center rounded-xl border border-dashed border-border bg-surface p-12 text-muted">
        <div className="text-center">
          <p className="text-lg font-medium">No specimen loaded</p>
          <p className="mt-1 text-sm">
            Select a dataset row or paste a clinical note to begin.
          </p>
        </div>
      </div>
    );
  }

  // When no highlights, render formatted letter
  if (spans.length === 0) {
    return (
      <div className="relative rounded-xl border border-border bg-surface p-8 shadow-sm">
        <div className="note-text text-foreground">
          {formatNoteAsLetter(cleanText)}
        </div>
        {goldOverlay && goldLabel && (
          <div className="mt-8 rounded-lg border border-gold-ghost/30 bg-gold-ghost/5 p-4">
            <p className="text-sm font-mono text-gold-ghost/80">
              <span className="font-semibold">Gold label:</span> {goldLabel}
            </p>
          </div>
        )}
      </div>
    );
  }

  // With highlights: split into segments and wrap highlighted portions
  return (
    <div className="relative rounded-xl border border-border bg-surface p-8 shadow-sm">
      <div className="note-text text-foreground">
        {segments.map((seg, i) => {
          const content = cleanText.slice(seg.start, seg.end);
          if (seg.spans.length === 0) {
            // Preserve line breaks within non-highlighted segments
            return (
              <span key={i}>
                {content.split("\n").map((line, j, arr) => (
                  <span key={j}>
                    {line}
                    {j < arr.length - 1 && <br />}
                  </span>
                ))}
              </span>
            );
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
              {content.split("\n").map((line, j, arr) => (
                <span key={j}>
                  {line}
                  {j < arr.length - 1 && <br />}
                </span>
              ))}
            </mark>
          );
        })}
      </div>

      {goldOverlay && goldLabel && (
        <div className="mt-8 rounded-lg border border-gold-ghost/30 bg-gold-ghost/5 p-4">
          <p className="text-sm font-mono text-gold-ghost/80">
            <span className="font-semibold">Gold label:</span> {goldLabel}
          </p>
        </div>
      )}
    </div>
  );
}
