"use client";

import { useMemo } from "react";
import * as Tooltip from "@radix-ui/react-tooltip";
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

  if (activeStage === "select") {
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
        kind: "hybrid",
        label: fs.final_label,
        tooltip: `Selected: ${fs.final_label}`,
      });
    }
  }

  if (activeStage === "score") {
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
        kind: "success",
        label: fs.final_label,
        tooltip: `Scored: ${fs.final_label}`,
      });
    }
  }

  return spans;
}

function kindToClass(kind: HighlightSpan["kind"]): string {
  switch (kind) {
    case "deterministic":
      return "span-highlight--deterministic";
    case "deterministic-alt":
      return "span-highlight--deterministic-alt";
    case "llm":
      return "span-highlight--llm";
    case "repair":
      return "span-highlight--repair";
    case "hybrid":
      return "span-highlight--hybrid";
    case "success":
      return "span-highlight--success";
    case "gold":
      return "span-highlight--gold";
    case "no-reference":
      return "span-highlight--no-reference";
    default:
      return "";
  }
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

function SpanTooltip({
  span,
  children,
}: {
  span: HighlightSpan;
  children: React.ReactNode;
}) {
  return (
    <Tooltip.Provider delayDuration={150}>
      <Tooltip.Root>
        <Tooltip.Trigger asChild>{children}</Tooltip.Trigger>
        <Tooltip.Portal>
          <Tooltip.Content
            side="top"
            align="start"
            sideOffset={6}
            className="z-50 max-w-xs rounded-lg border border-border bg-surface px-3 py-2.5 shadow-lg"
          >
            <div className="space-y-1">
              {span.ruleId && (
                <div className="flex items-center gap-2">
                  <span className="rounded-md bg-deterministic/10 px-1.5 py-0.5 font-mono text-[10px] font-medium text-deterministic">
                    {span.ruleId}
                  </span>
                  {span.ruleGroup && (
                    <span className="text-[10px] text-muted uppercase tracking-wide">
                      {span.ruleGroup}
                    </span>
                  )}
                </div>
              )}
              <p className="text-xs font-medium text-foreground">{span.label}</p>
              {span.portability && (
                <p className="text-[10px] text-muted">
                  Portability: {" "}
                  <span className="font-medium text-foreground">
                    {span.portability}
                  </span>
                </p>
              )}
            </div>
            <Tooltip.Arrow className="fill-border" />
          </Tooltip.Content>
        </Tooltip.Portal>
      </Tooltip.Root>
    </Tooltip.Provider>
  );
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

  const spans = useMemo(
    () => getSpansForStage(cleanText, candidates, finalSelection, activeStage),
    [cleanText, candidates, finalSelection, activeStage]
  );

  const segments = useMemo(() => buildSegments(cleanText, spans), [cleanText, spans]);

  const goldMatch = useMemo(() => {
    if (!goldLabel || !predictedLabel) return undefined;
    return goldLabel.trim().toLowerCase() === predictedLabel.trim().toLowerCase();
  }, [goldLabel, predictedLabel]);

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

  // Ghost gold overlay styling
  const goldOverlayClasses =
    goldMatch === true
      ? "border-success/30 bg-success/5 text-success/80"
      : goldMatch === false
      ? "border-error/30 bg-error/5 text-error/80"
      : "border-gold-ghost/30 bg-gold-ghost/5 text-gold-ghost/80";

  const goldIcon =
    goldMatch === true ? "✓" : goldMatch === false ? "✗" : "◆";

  // When no highlights, render formatted letter
  if (spans.length === 0) {
    return (
      <div className="relative rounded-xl border border-border bg-surface p-8 shadow-sm">
        <div className="note-text text-foreground">
          {formatNoteAsLetter(cleanText)}
        </div>
        {goldOverlay && goldLabel && (
          <div className={`mt-8 rounded-lg border ${goldOverlayClasses} p-4`}>
            <p className="text-sm font-mono">
              <span className="font-semibold">{goldIcon} Gold label:</span>{" "}
              {goldLabel}
            </p>
            {goldMatch === false && predictedLabel && (
              <p className="mt-1 text-xs font-mono opacity-80">
                Predicted: {predictedLabel}
              </p>
            )}
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
          const kindClass = kindToClass(primary.kind);

          const highlighted = (
            <mark
              key={i}
              className={`span-highlight ${kindClass}`}
            >
              {content.split("\n").map((line, j, arr) => (
                <span key={j}>
                  {line}
                  {j < arr.length - 1 && <br />}
                </span>
              ))}
            </mark>
          );

          // Wrap in rich tooltip if we have rule metadata
          if (primary.ruleId || primary.tooltip) {
            return (
              <SpanTooltip key={i} span={primary}>
                {highlighted}
              </SpanTooltip>
            );
          }

          return highlighted;
        })}
      </div>

      {goldOverlay && goldLabel && (
        <div className={`mt-8 rounded-lg border ${goldOverlayClasses} p-4`}>
          <p className="text-sm font-mono">
            <span className="font-semibold">{goldIcon} Gold label:</span>{" "}
            {goldLabel}
          </p>
          {goldMatch === false && predictedLabel && (
            <p className="mt-1 text-xs font-mono opacity-80">
              Predicted: {predictedLabel}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
