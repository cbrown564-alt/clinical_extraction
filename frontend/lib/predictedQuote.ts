type QuoteMention = {
  text: string;
  evidence: string;
  entity: string;
};

type QuoteSpan = {
  kind: string;
  entity: string;
  text: string;
};

function samePhrase(left: string, right: string): boolean {
  return left.trim().toLowerCase() === right.trim().toLowerCase();
}

/**
 * The muted line under a predicted mention should be the letter quote, not the
 * answer. Some models copy `text` into `evidence`; fall back to a longer
 * overlapping letter span in that case.
 */
export function displayPredictedEvidence(
  mention: QuoteMention,
  spans: readonly QuoteSpan[]
): string {
  const evidence = mention.evidence.trim();
  const text = mention.text.trim();
  if (evidence && !samePhrase(evidence, text)) return mention.evidence;

  const quotes = spans
    .filter(
      (span) =>
        span.kind === "llm" &&
        span.entity === mention.entity &&
        Boolean(text) &&
        span.text.toLowerCase().includes(text.toLowerCase()) &&
        !samePhrase(span.text, text)
    )
    .sort((left, right) => right.text.length - left.text.length);

  return quotes[0]?.text ?? mention.evidence;
}
