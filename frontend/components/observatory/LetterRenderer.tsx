"use client";

import { useMemo } from "react";

interface HighlightSpan {
  start: number;
  end: number;
  kind: "gold" | "deterministic" | "llm" | string;
  label?: string;
}

interface LetterRendererProps {
  text: string;
  highlights?: HighlightSpan[];
  children?: React.ReactNode; // extra content below letter (gold label card etc)
}

function unescapeText(text: string): string {
  return text
    .replace(/\\n/g, "\n")
    .replace(/\\t/g, "\t")
    .replace(/\\r/g, "\r");
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
          className="mb-4 border-b border-border pb-3 text-sm leading-relaxed text-muted"
        >
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

function kindToClass(kind: string): string {
  switch (kind) {
    case "gold":
      return "span-highlight--gold";
    case "deterministic":
      return "span-highlight--deterministic";
    case "llm":
      return "span-highlight--llm";
    case "hybrid":
      return "span-highlight--hybrid";
    case "success":
      return "span-highlight--success";
    case "error":
      return "span-highlight--repair";
    default:
      return "";
  }
}

export default function LetterRenderer({ text, highlights = [], children }: LetterRendererProps) {
  const cleanText = useMemo(() => unescapeText(text), [text]);

  const segments = useMemo(
    () => buildSegments(cleanText, highlights),
    [cleanText, highlights]
  );

  const hasHighlights = highlights.length > 0;

  return (
    <div className="relative rounded-xl border border-border bg-surface p-5 shadow-sm">
      <div className="note-text text-foreground">
        {!hasHighlights ? (
          formatNoteAsLetter(cleanText)
        ) : (
          segments.map((seg, i) => {
            const content = cleanText.slice(seg.start, seg.end);
            if (seg.spans.length === 0) {
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
            return (
              <mark key={i} className={`span-highlight ${kindClass}`} title={primary.label}>
                {content.split("\n").map((line, j, arr) => (
                  <span key={j}>
                    {line}
                    {j < arr.length - 1 && <br />}
                  </span>
                ))}
              </mark>
            );
          })
        )}
      </div>
      {children}
    </div>
  );
}
