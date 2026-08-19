export type FamilyHighlightSpan = {
  start: number;
  end: number;
  entity: string;
  label?: string;
};

function isWhitespaceGap(letterText: string, start: number, end: number): boolean {
  if (end < start) return false;
  return /^\s*$/.test(letterText.slice(start, end));
}

function preferLabel<T extends FamilyHighlightSpan>(left: T, right: T): string | undefined {
  const leftWidth = left.end - left.start;
  const rightWidth = right.end - right.start;
  if (rightWidth > leftWidth) return right.label;
  return left.label;
}

/**
 * Paint one highlight run per family when spans overlap or are separated only
 * by spaces, tabs, or newlines. Scoring is unchanged; this is display only.
 */
export function mergeFamilyHighlights<T extends FamilyHighlightSpan>(
  spans: readonly T[],
  letterText: string
): T[] {
  const groups = new Map<string, T[]>();
  for (const span of spans) {
    const start = Math.max(0, span.start);
    const end = Math.min(letterText.length, span.end);
    if (end <= start) continue;
    const clamped = { ...span, start, end };
    const group = groups.get(span.entity) ?? [];
    group.push(clamped);
    groups.set(span.entity, group);
  }

  const merged: T[] = [];
  for (const group of groups.values()) {
    group.sort((left, right) => left.start - right.start || left.end - right.end);
    let current = group[0];
    for (let index = 1; index < group.length; index += 1) {
      const next = group[index];
      if (
        next.start <= current.end ||
        isWhitespaceGap(letterText, current.end, next.start)
      ) {
        current = {
          ...current,
          end: Math.max(current.end, next.end),
          label: preferLabel(current, next),
        };
        continue;
      }
      merged.push(current);
      current = next;
    }
    merged.push(current);
  }

  return merged.sort((left, right) => left.start - right.start || left.end - right.end);
}
