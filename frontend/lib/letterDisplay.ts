/** Display-only letter spacing. Scoring and stored artifacts stay unchanged. */

export type NormalizedLetterDisplay = {
  text: string;
  remap: (originalIndex: number) => number;
};

type LineKind =
  | "blank"
  | "section"
  | "salutation"
  | "signoff"
  | "list"
  | "prose"
  | "field";

type Line = {
  start: number;
  end: number;
  text: string;
  kind: LineKind;
};

const SECTION_HEAD =
  /^(diagnosis|medication|current(?:\s+antiepileptic)?\s+medication|investigations?|past medical history|social history|drug history|allergies|impression|plan|examination)\b/i;
const SALUTATION = /^dear\b/i;
const SIGNOFF =
  /^(yours\s+sincerely|yours\s+faithfully|best\s+wishes|kind\s+regards|regards)\b/i;

function classifyLine(text: string): LineKind {
  if (/^\s*$/.test(text)) return "blank";
  const trimmed = text.trim();
  if (SALUTATION.test(trimmed)) return "salutation";
  if (SIGNOFF.test(trimmed)) return "signoff";
  if (SECTION_HEAD.test(trimmed)) return "section";
  if (/^\s*(?:\d+\.|[-*•])/.test(text)) return "list";
  if (
    trimmed.length >= 70 ||
    /[.!?]["']?\s/.test(trimmed) ||
    /[.!?]["']?$/.test(trimmed)
  ) {
    return "prose";
  }
  return "field";
}

function shouldSeparate(previous: Line, next: Line): boolean {
  if (
    next.kind === "section" ||
    next.kind === "salutation" ||
    next.kind === "signoff"
  ) {
    return true;
  }
  if (previous.kind === "salutation" || previous.kind === "signoff") {
    return true;
  }
  if (
    (previous.kind === "section" || previous.kind === "field") &&
    next.kind === "prose"
  ) {
    return true;
  }
  if (previous.kind === "prose" && next.kind === "prose") {
    return (
      /[.!?]["']?$/.test(previous.text.trim()) && /^[A-Z]/.test(next.text.trim())
    );
  }
  return false;
}

function nextLineBreak(source: string, from: number): {
  textEnd: number;
  breakEnd: number;
} | null {
  for (let cursor = from; cursor < source.length; cursor += 1) {
    if (source.startsWith("\r\n", cursor)) {
      return { textEnd: cursor, breakEnd: cursor + 2 };
    }
    if (source[cursor] === "\n" || source[cursor] === "\r") {
      return { textEnd: cursor, breakEnd: cursor + 1 };
    }
  }
  return null;
}

function splitLines(source: string): Line[] {
  const lines: Line[] = [];
  let index = 0;
  while (index <= source.length) {
    const br = nextLineBreak(source, index);
    if (!br) {
      lines.push({
        start: index,
        end: source.length,
        text: source.slice(index),
        kind: classifyLine(source.slice(index)),
      });
      break;
    }
    const text = source.slice(index, br.textEnd);
    lines.push({
      start: index,
      end: br.textEnd,
      text,
      kind: classifyLine(text),
    });
    index = br.breakEnd;
    if (index === source.length) {
      break;
    }
  }
  return lines;
}

function mapOriginalChars(
  origToNew: Int32Array,
  originalStart: number,
  originalEnd: number,
  emittedStart: number,
  emittedLength: number
): void {
  const originalLength = originalEnd - originalStart;
  for (let offset = 0; offset < originalLength; offset += 1) {
    const emittedOffset =
      emittedLength === 0 ? 0 : Math.min(offset, emittedLength - 1);
    origToNew[originalStart + offset] = emittedStart + emittedOffset;
  }
}

/**
 * Collapse extra blank lines and insert a single paragraph break between
 * jammed sections. Highlight offsets remap onto the display string.
 */
export function normalizeLetterDisplay(raw: string): NormalizedLetterDisplay {
  const source = raw;
  const origToNew = new Int32Array(source.length + 1);
  origToNew.fill(-1);
  const content = splitLines(source).filter((line) => line.kind !== "blank");
  let out = "";

  const emitGap = (originalStart: number, originalEnd: number, gap: string) => {
    const emittedStart = out.length;
    out += gap;
    mapOriginalChars(
      origToNew,
      originalStart,
      originalEnd,
      emittedStart,
      gap.length
    );
  };

  if (content.length === 0) {
    origToNew[source.length] = 0;
    return { text: "", remap: () => 0 };
  }

  if (content[0].start > 0) {
    emitGap(0, content[0].start, "");
  }

  content.forEach((line, index) => {
    const emittedStart = out.length;
    out += line.text;
    mapOriginalChars(
      origToNew,
      line.start,
      line.end,
      emittedStart,
      line.text.length
    );

    const next = content[index + 1];
    if (!next) {
      if (line.end < source.length) {
        emitGap(line.end, source.length, "");
      }
      return;
    }
    emitGap(line.end, next.start, shouldSeparate(line, next) ? "\n\n" : "\n");
  });

  origToNew[source.length] = out.length;
  for (let index = 0; index <= source.length; index += 1) {
    if (origToNew[index] < 0) {
      origToNew[index] = index === 0 ? 0 : origToNew[index - 1];
    }
  }

  return {
    text: out,
    remap: (originalIndex: number) => {
      const clamped = Math.max(0, Math.min(source.length, originalIndex));
      return origToNew[clamped];
    },
  };
}
