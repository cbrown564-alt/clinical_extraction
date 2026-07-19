"use client";

import { SourceDocument, type HighlightTone, type RenderSpan } from "@/components/surface";

interface HighlightSpan {
  start: number;
  end: number;
  /** A highlight tone, or any string (legacy callers); unknowns render plain. */
  kind: HighlightTone | string;
  label?: string;
}

interface LetterRendererProps {
  text: string;
  highlights?: HighlightSpan[];
  /** Extra content below the letter (gold label card etc). */
  children?: React.ReactNode;
}

const KNOWN_TONES: HighlightTone[] = [
  "deterministic",
  "deterministic-alt",
  "llm",
  "repair",
  "hybrid",
  "success",
  "gold",
  "no-reference",
];

/** Map a legacy `kind` onto a render tone, tolerating a couple of aliases. */
function toTone(kind: string): HighlightTone | null {
  if ((KNOWN_TONES as string[]).includes(kind)) return kind as HighlightTone;
  if (kind === "error") return "repair";
  return null;
}

/**
 * Thin adapter over the shared {@link SourceDocument}. Kept as a named surface
 * for the observatory gold-audit panel and the ExECTv2 explorer, which pass
 * pre-resolved highlight tones (ExECTv2 resolves them from the family so the
 * letter matches the lens strip).
 */
export default function LetterRenderer({ text, highlights = [], children }: LetterRendererProps) {
  const spans: RenderSpan[] = [];
  for (const h of highlights) {
    const tone = toTone(h.kind);
    if (tone) spans.push({ start: h.start, end: h.end, tone, label: h.label });
  }

  return (
    <SourceDocument text={text} spans={spans}>
      {children}
    </SourceDocument>
  );
}
