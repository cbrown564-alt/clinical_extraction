"use client";

import {
  displayPayload,
  hasMentionList,
  parseStationFact,
  type StationFactView,
} from "@/lib/assemblyLine";
import { attributeRank, sortedAttributeKeys, type AttributeRank } from "@/lib/attributeOrder";
import { EXECTV2_FAMILIES } from "@/lib/datasets/exectv2";
import type { DatasetTone } from "@/lib/datasets/types";

type AttributeMark = "same" | "changed" | "added" | "removed";

function familyMeta(family: string): { label: string; tone: DatasetTone } {
  const found = EXECTV2_FAMILIES.find((item) => item.id === family);
  return { label: found?.label ?? family, tone: found?.tone ?? "muted" };
}

function toneBadgeClass(tone: DatasetTone): string {
  switch (tone) {
    case "deterministic":
      return "border-deterministic/25 bg-deterministic/10 text-deterministic";
    case "deterministic-alt":
      return "border-deterministic-alt/25 bg-deterministic-alt/10 text-deterministic-alt";
    case "llm":
      return "border-llm/25 bg-llm/10 text-llm";
    case "hybrid":
      return "border-hybrid/25 bg-hybrid/10 text-hybrid";
    case "success":
      return "border-success/25 bg-success/10 text-success";
    case "error":
      return "border-error/25 bg-error/10 text-error";
    case "muted":
      return "border-border bg-surface-raised text-muted";
    default: {
      const _exhaustive: never = tone;
      return _exhaustive;
    }
  }
}

function attributeNameClass(rank: AttributeRank, family: string): string {
  const { tone } = familyMeta(family);
  if (rank === "identity" || rank === "qualifier") return "text-muted/70";
  if (rank === "primary") return `${toneTextClass(tone)} font-medium`;
  return "text-muted";
}

function attributeValueClass(rank: AttributeRank, family: string): string {
  const { tone } = familyMeta(family);
  if (rank === "identity" || rank === "qualifier") return "text-muted";
  if (rank === "primary") return `${toneTextClass(tone)} font-medium`;
  return "text-foreground";
}

function toneTextClass(tone: DatasetTone): string {
  switch (tone) {
    case "deterministic":
      return "text-deterministic";
    case "deterministic-alt":
      return "text-deterministic-alt";
    case "llm":
      return "text-llm";
    case "hybrid":
      return "text-hybrid";
    case "success":
      return "text-success";
    case "error":
      return "text-error";
    case "muted":
      return "text-muted";
    default: {
      const _exhaustive: never = tone;
      return _exhaustive;
    }
  }
}

function rowMarkClass(mark: AttributeMark): string | undefined {
  switch (mark) {
    case "changed":
      return "bg-llm/8";
    case "added":
      return "bg-success/8";
    case "removed":
      return "bg-muted/10";
    case "same":
      return undefined;
    default: {
      const _exhaustive: never = mark;
      return _exhaustive;
    }
  }
}

function FamilyBadge({ family }: { family: string }) {
  if (!family || family === "GanEvent") return null;
  const { label, tone } = familyMeta(family);
  return (
    <span
      className={`rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${toneBadgeClass(tone)}`}
    >
      {label}
    </span>
  );
}

function AttributeTable({
  family,
  previous,
  current,
}: {
  family: string;
  previous?: Record<string, string>;
  current: Record<string, string>;
}) {
  const compare = previous !== undefined;
  const keys = sortedAttributeKeys(
    [...Object.keys(previous ?? {}), ...Object.keys(current)],
    family
  );
  if (keys.length === 0) return null;

  return (
    <div className="mt-2.5 overflow-hidden rounded border border-border/70 bg-surface-raised/40 text-[11px]">
      <table className="w-full border-collapse text-left">
        <thead>
          <tr className="border-b border-border/70 bg-surface-raised font-mono text-[10px] uppercase tracking-wider text-muted">
            <th className="px-2 py-1 font-medium">Attribute</th>
            {compare ? <th className="px-2 py-1 font-medium">Before</th> : null}
            <th className="px-2 py-1 font-medium">{compare ? "After" : "Value"}</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border/40 font-mono">
          {keys.map((key) => {
            const before = previous?.[key];
            const after = current[key];
            let mark: AttributeMark = "same";
            if (compare) {
              if (before === undefined) mark = "added";
              else if (after === undefined) mark = "removed";
              else if (before !== after) mark = "changed";
            }
            const rank = attributeRank(key, family);
            return (
              <tr key={key} className={rowMarkClass(mark)}>
                <td className={`px-2 py-1 ${attributeNameClass(rank, family)}`}>{key}</td>
                {compare ? (
                  <td className={`px-2 py-1 ${attributeValueClass(rank, family)}`}>
                    {before ?? <span className="text-muted/40">—</span>}
                  </td>
                ) : null}
                <td className={`px-2 py-1 ${attributeValueClass(rank, family)}`}>
                  {after ?? <span className="text-muted/40">—</span>}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function GanExtractBody({
  fact,
  previous,
}: {
  fact: Extract<StationFactView, { kind: "gan_extract" }>;
  previous?: Extract<StationFactView, { kind: "gan_extract" }>;
}) {
  const previousById = new Map(
    (previous?.events ?? []).map((event) => [event.attributes.event_id ?? event.phrase, event])
  );
  return (
    <div className="space-y-3">
      {fact.events.map((event, index) => (
        <div key={event.attributes.event_id ?? `${event.phrase}:${index}`}>
          {fact.events.length > 1 ? (
            <p className="mb-1 text-[10px] font-semibold uppercase tracking-wider text-muted">
              Event {event.attributes.event_id || index + 1}
            </p>
          ) : null}
          <StructuredBody
            fact={event}
            previous={previousById.get(event.attributes.event_id ?? event.phrase)}
          />
        </div>
      ))}
      {fact.selection ? (
        <div className="border-t border-border/60 pt-3">
          <p className="mb-1 text-[10px] font-semibold uppercase tracking-wider text-muted">
            Selection
          </p>
          <StructuredBody
            fact={fact.selection}
            previous={previous?.selection ?? undefined}
          />
        </div>
      ) : null}
    </div>
  );
}

function StructuredBody({
  fact,
  previous,
}: {
  fact: Extract<StationFactView, { kind: "structured" }>;
  previous?: Extract<StationFactView, { kind: "structured" }>;
}) {
  const phraseChanged = Boolean(previous && previous.phrase !== fact.phrase);
  return (
    <div>
      <div className="flex flex-wrap items-center gap-2">
        <FamilyBadge family={fact.family} />
        {fact.family === "GanEvent" && fact.attributes.kind ? (
          <span className="rounded border border-deterministic/25 bg-deterministic/10 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-deterministic">
            {fact.attributes.kind.replace(/_/g, " ")}
          </span>
        ) : null}
        <p
          className={`font-serif text-base leading-snug text-foreground ${
            phraseChanged ? "rounded bg-llm/10 px-1" : ""
          }`}
        >
          {fact.phrase}
        </p>
      </div>
      {fact.evidence ? (
        <p className="mt-2 text-[13px] leading-snug text-muted">“{fact.evidence}”</p>
      ) : null}
      <AttributeTable
        family={fact.family}
        previous={previous?.attributes}
        current={fact.attributes}
      />
      {(fact.confidence || fact.rationale) &&
      !fact.attributes.confidence &&
      !fact.attributes.rationale ? (
        <p className="mt-2 text-[10px] font-semibold uppercase tracking-wider text-muted">
          {[fact.confidence, fact.rationale].filter(Boolean).join(" · ")}
        </p>
      ) : null}
    </div>
  );
}

function FactBody({
  raw,
  compareRaw,
}: {
  raw: string;
  compareRaw?: string;
}) {
  const fact = parseStationFact(raw);
  const previous = compareRaw ? parseStationFact(compareRaw) : undefined;
  const flattened = Boolean(compareRaw && hasMentionList(compareRaw) && !hasMentionList(raw));
  switch (fact.kind) {
    case "structured":
      return (
        <div>
          {flattened ? (
            <p className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-llm">
              Event → mention
            </p>
          ) : null}
          <StructuredBody
            fact={fact}
            previous={previous?.kind === "structured" ? previous : undefined}
          />
        </div>
      );
    case "gan_extract":
      return (
        <GanExtractBody
          fact={fact}
          previous={previous?.kind === "gan_extract" ? previous : undefined}
        />
      );
    case "prose":
      return fact.text ? (
        <p className="mt-1 font-serif text-base leading-snug text-foreground">{fact.text}</p>
      ) : null;
    default: {
      const _exhaustive: never = fact;
      return _exhaustive;
    }
  }
}

function RawToggle({ value }: { value: string }) {
  const body = displayPayload(value);
  if (!body) return null;
  return (
    <details className="mt-2">
      <summary className="cursor-pointer text-[10px] font-semibold uppercase tracking-wider text-muted">
        Raw
      </summary>
      <pre className="mt-2 whitespace-pre-wrap break-words font-mono text-[11px] leading-relaxed text-muted">
        {body}
      </pre>
    </details>
  );
}

export default function StationFactCard({
  raw,
  compareRaw,
}: {
  raw: string;
  compareRaw?: string;
}) {
  return (
    <div className="mt-2">
      <FactBody raw={raw} compareRaw={compareRaw} />
      <RawToggle value={raw} />
    </div>
  );
}
