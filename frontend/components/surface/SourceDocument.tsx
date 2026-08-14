"use client";

import { useMemo, type ReactNode } from "react";
import * as Tooltip from "@radix-ui/react-tooltip";

/**
 * The eight highlight hues both datasets draw on the source document. These map
 * one-to-one onto the `.span-highlight--*` classes in globals.css and onto the
 * dataset tone system, so a span's colour on the letter is the *same* colour the
 * lens strip uses for that concept (Gan stage / ExECTv2 family).
 */
export type HighlightTone =
  | "deterministic"
  | "deterministic-alt"
  | "llm"
  | "repair"
  | "hybrid"
  | "success"
  | "gold"
  | "no-reference";

export interface RenderSpan {
  start: number;
  end: number;
  tone: HighlightTone;
  /** Plain-text tooltip / aria label. */
  label?: string;
  /** Rich tooltip body (falls back to `label`). */
  tooltip?: string;
  ruleId?: string;
  ruleGroup?: string | null;
  portability?: string | null;
}

function unescapeText(text: string): string {
  return text.replace(/\\n/g, "\n").replace(/\\t/g, "\t").replace(/\\r/g, "\r");
}

const TONE_CLASS: Record<HighlightTone, string> = {
  deterministic: "span-highlight--deterministic",
  "deterministic-alt": "span-highlight--deterministic-alt",
  llm: "span-highlight--llm",
  repair: "span-highlight--repair",
  hybrid: "span-highlight--hybrid",
  success: "span-highlight--success",
  gold: "span-highlight--gold",
  "no-reference": "span-highlight--no-reference",
};

/** Render text with single line breaks preserved. */
function withBreaks(content: string): ReactNode {
  return content.split("\n").map((line, j, arr) => (
    <span key={j}>
      {line}
      {j < arr.length - 1 && <br />}
    </span>
  ));
}

/** Formal-letter formatting: header block, body paragraphs, sign-off. */
function formatAsLetter(text: string): ReactNode {
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
        <div key={i} className="mb-4 border-b border-border pb-3 text-sm leading-relaxed text-muted">
          {lines.map((line, j) => (
            <div key={j}>{line.trim()}</div>
          ))}
        </div>
      );
    }

    if (isClosing) {
      return (
        <div key={i} className="mt-6 text-sm text-muted">
          {lines.map((line, j) => (
            <div key={j}>{line.trim()}</div>
          ))}
        </div>
      );
    }

    return (
      <p key={i} className="mb-3">
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

function buildSegments(
  text: string,
  spans: RenderSpan[]
): Array<{ start: number; end: number; spans: RenderSpan[] }> {
  const points = new Set<number>([0, text.length]);
  for (const span of spans) {
    points.add(Math.max(0, span.start));
    points.add(Math.min(text.length, span.end));
  }
  const sorted = Array.from(points).sort((a, b) => a - b);
  const segments: Array<{ start: number; end: number; spans: RenderSpan[] }> = [];
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

function SpanTooltip({ span, children }: { span: RenderSpan; children: ReactNode }) {
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
                  <span className="rounded-md bg-deterministic/10 px-1.5 py-0.5 font-mono text-[11px] font-medium text-deterministic">
                    {span.ruleId}
                  </span>
                  {span.ruleGroup && (
                    <span className="text-[11px] uppercase tracking-wide text-muted">
                      {span.ruleGroup}
                    </span>
                  )}
                </div>
              )}
              {(span.label || span.tooltip) && (
                <p className="text-xs font-medium text-foreground">{span.tooltip ?? span.label}</p>
              )}
              {span.portability && (
                <p className="text-[11px] text-muted">
                  Portability:{" "}
                  <span className="font-medium text-foreground">{span.portability}</span>
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

/**
 * The single clinical-document renderer both datasets share.
 *
 * Owns the letter typography, `\n` unescaping, formal-letter formatting, and
 * evidence-span overlays so Gan's note and ExECTv2's letter read identically.
 * Callers derive their own {@link RenderSpan}s – Gan by pipeline stage, ExECTv2
 * by family – but the colour of a span is always the tone shared with the lens
 * strip, so the highlight on the page matches the lens that produced it.
 */
export default function SourceDocument({
  text,
  spans = [],
  children,
}: {
  text: string;
  spans?: RenderSpan[];
  children?: ReactNode;
}) {
  const cleanText = useMemo(() => unescapeText(text), [text]);
  const segments = useMemo(() => buildSegments(cleanText, spans), [cleanText, spans]);

  return (
    <div className="relative rounded-xl border border-border bg-surface p-5 shadow-sm">
      <div className="note-text text-foreground">
        {segments.map((seg, i) => {
          const content = cleanText.slice(seg.start, seg.end);
          if (seg.spans.length === 0) {
            return <span key={i}>{withBreaks(content)}</span>;
          }
          const primary = seg.spans[0];
          const mark = (
            <mark className={`span-highlight ${TONE_CLASS[primary.tone]}`} title={primary.label}>
              {withBreaks(content)}
            </mark>
          );
          if (primary.ruleId || primary.tooltip) {
            return (
              <SpanTooltip key={i} span={primary}>
                {mark}
              </SpanTooltip>
            );
          }
          return <span key={i}>{mark}</span>;
        })}
      </div>
      {children}
    </div>
  );
}
