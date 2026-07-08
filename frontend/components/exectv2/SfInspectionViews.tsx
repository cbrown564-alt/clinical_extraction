"use client";

import { useMemo, useState, type ReactNode } from "react";
import { AlertOctagon, AlertTriangle, CheckCircle2, ChevronRight, CircleDashed } from "lucide-react";
import type {
  SfCandidateSpan,
  SfComponentMeta,
  SfInspectionLetter,
  SfInspectionScorecard,
  SfLayerAPair,
} from "@/lib/types";
import {
  cellSeverity,
  connectOverridesToErrors,
  familyHasAnyError,
  familyTriageStatus,
  letterVerdict,
  rootF1,
  SF_FAMILIES,
  type SfFamily,
} from "@/lib/sfFamilies";
import { fmtVal, STATUS_META, phraseSurfaceKind } from "@/lib/sfPresentation";
import { AttributeSchemaCard } from "./SfAttributeSchema";
import { MentionFlowList } from "./SfMentionFlow";
import { describePairDivergence } from "@/lib/sfSchema";

// ── Component order (must match the backend COMPONENT_ORDER) ──
//
// The 11 FrequencyStateScores, ordered burden -> direction/magnitude axes ->
// filtered states -> attribute-level exact matches. This is a TREE, not a
// flat peer list — see lib/sfFamilies.ts for the 3-root-family grouping
// (headline state / change state / strict benchmark) that drives the views
// below.

export const COMPONENT_ORDER = [
  "clinical_headline",
  "state_profile",
  "state_profile_directional",
  "state_profile_direction_deconf",
  "state_profile_magnitude",
  "active_rate",
  "active_rate_fidelity",
  "seizure_free",
  "unknown",
  "exact_semantic",
  "benchmark_with_cui",
] as const;

const FAMILY_TONE: Record<
  SfFamily["id"],
  { text: string; bg: string; border: string; dot: string; topBorder: string; leftBorder: string }
> = {
  headline: {
    text: "text-deterministic",
    bg: "bg-deterministic/10",
    border: "border-deterministic/30",
    dot: "bg-deterministic",
    topBorder: "border-t-deterministic",
    leftBorder: "border-l-deterministic",
  },
  change: {
    text: "text-hybrid",
    bg: "bg-hybrid/10",
    border: "border-hybrid/30",
    dot: "bg-hybrid",
    topBorder: "border-t-hybrid",
    leftBorder: "border-l-hybrid",
  },
  bench: {
    text: "text-muted",
    bg: "bg-surface-raised",
    border: "border-border",
    dot: "bg-muted",
    topBorder: "border-t-border",
    leftBorder: "border-l-border",
  },
};

// ── Family legend (shared by overview + inspector) ──

export function FamilyLegend() {
  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[9.5px] text-muted">
      {SF_FAMILIES.map((f) => (
        <span key={f.id} className="flex items-center gap-1">
          <span className={`inline-block h-1.5 w-1.5 rounded-full ${FAMILY_TONE[f.id].dot}`} />
          <span className={`font-semibold ${FAMILY_TONE[f.id].text}`}>{f.label.split(" ")[0]}</span>
        </span>
      ))}
      <span>
        <span className="text-gold">G</span>/<span className="text-llm">P</span>
        <span className="mx-1 text-border">·</span>
        <span className="text-success">TP</span>
        <span className="mx-1 text-border">·</span>
        <span className="text-error">FP/FN</span>
      </span>
    </div>
  );
}

// ── Verdict — short status line, not an essay ──

export function VerdictBanner({ letter }: { letter: SfInspectionLetter }) {
  const verdict = useMemo(() => letterVerdict(letter), [letter]);

  if (verdict.severity === "no-activity") {
    return (
      <VerdictShell tone="muted" icon={<CircleDashed className="h-4 w-4" />}>
        No SF activity
      </VerdictShell>
    );
  }

  if (verdict.severity === "clean") {
    return (
      <VerdictShell tone="success" icon={<CheckCircle2 className="h-4 w-4" />}>
        Clean
        {verdict.benchErr ? (
          <span className="ml-2 font-normal text-muted">· bench disagrees (expected)</span>
        ) : null}
      </VerdictShell>
    );
  }

  const comp = verdict.primaryComponent;
  const stat = comp ? `fp${comp.fp}/fn${comp.fn}` : "";

  if (verdict.severity === "change-only") {
    return (
      <VerdictShell tone="hybrid" icon={<AlertTriangle className="h-4 w-4" />}>
        Change miss
        {comp ? (
          <>
            {" · "}
            <span className="font-mono">{comp.name}</span> {stat}
          </>
        ) : null}
      </VerdictShell>
    );
  }

  return (
    <VerdictShell tone="error" icon={<AlertOctagon className="h-4 w-4" />}>
      Headline miss
      {comp ? (
        <>
          {" · "}
          <span className="font-mono">{comp.name}</span> {stat}
        </>
      ) : null}
    </VerdictShell>
  );
}

const VERDICT_TONE: Record<string, string> = {
  success: "border-l-success bg-success/10 text-success",
  hybrid: "border-l-hybrid bg-hybrid/10 text-hybrid",
  error: "border-l-error bg-error/10 text-error",
  muted: "border-l-border bg-surface-raised text-muted",
};

function VerdictShell({
  tone,
  icon,
  children,
}: {
  tone: keyof typeof VERDICT_TONE;
  icon: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className={`flex items-center gap-2 border-l-[3px] px-3 py-2 ${VERDICT_TONE[tone]}`}>
      <span className="shrink-0">{icon}</span>
      <p className="text-[13px] font-semibold text-foreground">{children}</p>
    </div>
  );
}

// ── Family cards (overview) — 3 roots instead of 11 flat rows ──

export function FamilyCards({ scorecard }: { scorecard: SfInspectionScorecard }) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const toggle = (id: string) =>
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
      {SF_FAMILIES.map((family) => {
        const tone = FAMILY_TONE[family.id];
        const root = rootF1(scorecard, family);
        const isOpen = expanded.has(family.id);
        return (
          <div
            key={family.id}
            className={`rounded-lg border border-border border-t-[3px] ${tone.topBorder} bg-surface p-3.5 shadow-sm`}
          >
            <div className={`mb-1.5 flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wide ${tone.text}`}>
              <span className={`h-1.5 w-1.5 rounded-full ${tone.dot}`} />
              {family.label}
            </div>
            {root ? (
              <>
                <div className="mb-1 flex items-baseline gap-2">
                  <span className="font-mono text-2xl font-bold tracking-tight text-foreground">
                    {root.f1.toFixed(4)}
                  </span>
                  <span className="text-[9.5px] text-muted">F1 · {family.root}</span>
                </div>
                <div className="mb-1 flex h-1 overflow-hidden rounded-full bg-surface-raised">
                  <div className={`${tone.dot} opacity-80`} style={{ width: `${root.precision * 100}%` }} />
                </div>
                <div className="mb-2 flex justify-between font-mono text-[9.5px] text-muted">
                  <span>P {root.precision.toFixed(4)}</span>
                  <span>R {root.recall.toFixed(4)}</span>
                </div>
              </>
            ) : (
              <p className="mb-2 text-[10px] text-muted">no scorecard entry</p>
            )}
            <p className="mb-2.5 min-h-[54px] text-[10.5px] leading-relaxed text-muted">{family.blurb}</p>
            <div className="border-t border-border pt-1.5">
              <button
                onClick={() => toggle(family.id)}
                className={`flex w-full items-center gap-1 text-[10px] font-semibold ${tone.text}`}
              >
                <ChevronRight className={`h-2.5 w-2.5 transition-transform ${isOpen ? "rotate-90" : ""}`} />
                {family.children.length} child lens{family.children.length === 1 ? "" : "es"}
              </button>
              {isOpen && (
                <ul className="mt-1.5 flex flex-col gap-1">
                  {family.children.map((childName) => {
                    const cf1 = scorecard[childName];
                    const low = cf1 && root && cf1.f1 < root.f1 - 0.05;
                    return (
                      <li
                        key={childName}
                        className={`flex items-center justify-between gap-2 rounded px-1.5 py-0.5 text-[10px] ${
                          low ? "bg-error/10" : "bg-surface-raised"
                        }`}
                      >
                        <span className="font-mono text-foreground">{childName}</span>
                        <span className={`font-mono font-semibold ${low ? "text-error" : "text-foreground"}`}>
                          {cf1 ? cf1.f1.toFixed(4) : "—"}
                          {low && <span className="ml-1 text-[8.5px] font-bold">↓</span>}
                        </span>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ── Letter x family matrix (overview) — replaces the flat letter list ──

const SEVERITY_CLASS: Record<string, string> = {
  clean: "bg-success/10 text-success",
  err1: "bg-error/15 text-error",
  err2: "bg-error/25 text-error",
  na: "text-muted",
};

function CellPill({ status, letterHasActivity }: { status: { fp: number; fn: number; tp: number }; letterHasActivity: boolean }) {
  const sev = cellSeverity(status, letterHasActivity);
  if (sev === "na") {
    return <span className={`inline-block min-w-[52px] rounded px-1.5 py-0.5 text-center font-mono text-[9.5px] ${SEVERITY_CLASS.na}`}>—</span>;
  }
  const label = sev === "clean" ? "clean" : `fp${status.fp}/fn${status.fn}`;
  return (
    <span className={`inline-block min-w-[52px] rounded px-1.5 py-0.5 text-center font-mono text-[9.5px] font-bold ${SEVERITY_CLASS[sev]}`}>
      {label}
    </span>
  );
}

export function LetterMatrix({
  letters,
  selectedLetterId,
  onSelect,
  onInspect,
  inspectableIds,
  compact = false,
}: {
  letters: SfInspectionLetter[];
  selectedLetterId: string | null;
  onSelect: (id: string) => void;
  onInspect: (id: string) => void;
  /** Letters that actually have data to drill into (everything, from the live backend). */
  inspectableIds?: Set<string>;
  /** Sidebar triage density — shorter family headers, tighter rows. */
  compact?: boolean;
}) {
  const cellPad = compact ? "px-2 py-1" : "px-3 py-1.5";
  const headPad = compact ? "px-2 py-1.5" : "px-3 py-2";
  return (
    <div className={compact ? "" : "overflow-hidden overflow-x-auto rounded-lg border border-border bg-surface shadow-sm"}>
      <table className={`w-full border-collapse ${compact ? "text-[10px]" : "min-w-[560px] text-[10.5px]"}`}>
        <thead className={compact ? "sticky top-0 z-10" : undefined}>
          <tr>
            <th className={`border-b border-border bg-surface-raised ${headPad} text-left text-[9px] font-bold uppercase tracking-wide text-muted`}>
              letter
            </th>
            <th className={`border-b border-border bg-surface-raised ${headPad} text-left text-[9px] font-bold uppercase tracking-wide text-muted`}>
              {compact ? "g/p" : "gold / pred"}
            </th>
            {SF_FAMILIES.map((f) => (
              <th
                key={f.id}
                title={f.label}
                className={`border-b border-border bg-surface-raised ${headPad} text-center text-[9px] font-bold uppercase tracking-wide ${FAMILY_TONE[f.id].text}`}
              >
                {compact ? f.label.split(" ")[0] : f.label}
              </th>
            ))}
            <th className={`border-b border-border bg-surface-raised ${headPad}`} />
          </tr>
        </thead>
        <tbody>
          {letters.map((letter) => {
            const active = selectedLetterId === letter.letter_id;
            const canInspect = !inspectableIds || inspectableIds.has(letter.letter_id);
            return (
              <tr
                key={letter.letter_id}
                onClick={() => onSelect(letter.letter_id)}
                onDoubleClick={() => {
                  if (letter.has_activity && canInspect) onInspect(letter.letter_id);
                }}
                className={`cursor-pointer border-b border-border transition-colors last:border-b-0 ${
                  active ? "bg-hybrid/15 ring-1 ring-inset ring-hybrid/30" : "hover:bg-surface-raised"
                } ${!letter.has_activity ? "italic text-muted" : ""}`}
              >
                <td className={`${cellPad} font-mono font-bold text-foreground`}>{letter.letter_id}</td>
                <td className={`${cellPad} font-mono text-muted`}>
                  g{letter.gold_count}/p{letter.pred_count}
                </td>
                {SF_FAMILIES.map((f) => (
                  <td key={f.id} className={`${cellPad} text-center`}>
                    <CellPill status={familyTriageStatus(letter, f)} letterHasActivity={letter.has_activity} />
                  </td>
                ))}
                <td className={`${cellPad} text-right`}>
                  {letter.has_activity && canInspect && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onInspect(letter.letter_id);
                      }}
                      className="text-[9px] font-bold text-hybrid hover:underline"
                      title="Open deep dive"
                    >
                      {compact ? "→" : "inspect →"}
                    </button>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

// ── Layer A: schema attribute pairs ──

export function LayerA({
  letter,
  hideClean = false,
}: {
  letter: SfInspectionLetter;
  hideClean?: boolean;
}) {
  const isDirty = (p: SfLayerAPair) => {
    if (p.side !== "pair") return true;
    const attrsDirty = p.attributes.some(
      (a) => a.key !== "CUIPhrase" && a.match !== "ok" && a.match !== "absent"
    );
    if (attrsDirty) return true;
    // Phrase-only noise (hyphen/plural) is not dirty enough to keep in preview.
    return phraseSurfaceKind(p.gold_phrase, p.pred_phrase) === "substantive";
  };

  const pairs = hideClean ? letter.layer_a.pairs.filter(isDirty) : letter.layer_a.pairs;
  const hiddenClean = letter.layer_a.pairs.length - pairs.length;

  if (!letter.layer_a.pairs.length) {
    return <p className="py-2 text-[11px] text-muted">No SF mentions</p>;
  }
  if (!pairs.length) {
    return <p className="py-2 text-[11px] text-muted">All pairs match</p>;
  }

  return (
    <div className="flex flex-col gap-4">
      {pairs.map((pair, i) => (
        <AttrPair key={i} pair={pair} />
      ))}
      {hiddenClean > 0 && (
        <p className="text-[11px] text-muted">+{hiddenClean} full match</p>
      )}
    </div>
  );
}

function AttrPair({ pair }: { pair: SfLayerAPair }) {
  const phraseOk = pair.phrase_match === "ok";
  const nonCui = pair.attributes.filter((a) => a.key !== "CUIPhrase");
  const attrsClean = nonCui.every((a) => a.match === "ok" || a.match === "absent");
  const surface =
    pair.side === "pair" ? phraseSurfaceKind(pair.gold_phrase, pair.pred_phrase) : "identical";
  // Scorer phrase_match can be "bad" for hyphen/plural-only noise. Treat that
  // as clean when attributes agree, so we don't alarm with a red pair card.
  const isFullyClean =
    pair.side === "pair" && attrsClean && (phraseOk || surface !== "substantive");

  if (isFullyClean) {
    const phrase =
      surface === "identical" || surface === "surface"
        ? fmtVal(pair.pred_phrase || pair.gold_phrase)
        : fmtVal(pair.gold_phrase);
    return (
      <div className="flex items-center gap-2.5 border-l-[3px] border-l-success/60 px-3 py-2 text-[12px]">
        <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-success" />
        <span className="min-w-0 flex-1 font-semibold text-foreground">{phrase}</span>
        <span className="ml-auto shrink-0 text-[10px] font-semibold text-success">
          {surface === "surface" ? "attrs match · spelling differs" : "match"}
        </span>
      </div>
    );
  }

  const accent =
    pair.side === "fp" || pair.side === "fn" || surface === "substantive" || !attrsClean
      ? "border-l-error"
      : "border-l-border";

  const divergence = pair.side === "pair" ? describePairDivergence(pair) : null;
  const showAttrs = pair.side === "pair" && (!attrsClean || divergence !== null);

  return (
    <div className={`border-l-[3px] ${accent} bg-surface px-3 py-3`}>
      <PhraseCompare pair={pair} surface={surface} phraseOk={phraseOk} attrsClean={attrsClean} />

      {showAttrs && (
        <div className="mt-3">
          <AttributeSchemaCard pair={pair} />
        </div>
      )}

      {pair.side === "pair" && attrsClean && surface === "substantive" && (
        <p className="mt-2.5 text-[11px] text-muted">Attributes match — only the phrase text differs.</p>
      )}
    </div>
  );
}

/** The gold↔pred phrase block — the primary thing the eye should land on. */
function PhraseCompare({
  pair,
  surface,
  phraseOk,
  attrsClean,
}: {
  pair: SfLayerAPair;
  surface: ReturnType<typeof phraseSurfaceKind>;
  phraseOk: boolean;
  attrsClean: boolean;
}) {
  if (pair.side === "fp") {
    return (
      <div className="overflow-hidden rounded-md border border-error/25 bg-error/5">
        <PhraseLane side="pred" phrase={fmtVal(pair.pred_phrase)} status="FP · no gold" />
      </div>
    );
  }
  if (pair.side === "fn") {
    return (
      <div className="overflow-hidden rounded-md border border-error/25 bg-error/5">
        <PhraseLane side="gold" phrase={fmtVal(pair.gold_phrase)} status="FN · no pred" />
      </div>
    );
  }

  if (surface === "identical" || (phraseOk && surface !== "substantive")) {
    return (
      <div className="overflow-hidden rounded-md border border-border bg-surface-raised">
        <PhraseLane side="both" phrase={fmtVal(pair.gold_phrase)} />
      </div>
    );
  }

  const banner =
    surface === "surface"
      ? {
          cls: "border-t border-border bg-surface-raised text-muted",
          text: "Spelling / hyphenation only",
        }
      : {
          cls: "border-t border-error/20 bg-error/10 text-error",
          text: attrsClean ? "Different phrase text" : "Phrase mismatch",
        };

  return (
    <div className="overflow-hidden rounded-md border border-border">
      <PhraseLane side="gold" phrase={fmtVal(pair.gold_phrase)} />
      <div className="border-t border-border" />
      <PhraseLane side="pred" phrase={fmtVal(pair.pred_phrase)} />
      <div className={`px-3 py-1.5 text-[10px] font-bold uppercase tracking-wide ${banner.cls}`}>
        {banner.text}
      </div>
    </div>
  );
}

function PhraseLane({
  side,
  phrase,
  status,
}: {
  side: "gold" | "pred" | "both";
  phrase: string;
  status?: string;
}) {
  const badge =
    side === "gold"
      ? "border-gold/60 bg-gold text-foreground"
      : side === "pred"
        ? "border-llm/60 bg-llm text-white"
        : "border-border bg-foreground text-background";
  const label = side === "gold" ? "Gold" : side === "pred" ? "Pred" : "Match";
  const rowBg =
    side === "gold" ? "bg-gold/12" : side === "pred" ? "bg-llm/12" : "bg-surface-raised";
  const phraseTone =
    side === "gold" ? "text-foreground" : side === "pred" ? "text-foreground" : "text-foreground";
  const rail =
    side === "gold" ? "bg-gold" : side === "pred" ? "bg-llm" : "bg-success";

  return (
    <div className={`flex items-stretch ${rowBg}`}>
      <span className={`w-1 shrink-0 ${rail}`} aria-hidden />
      <div className="flex min-w-0 flex-1 items-start gap-3 px-3 py-3">
        <span
          className={`shrink-0 rounded border px-2 py-1 text-[10px] font-extrabold uppercase tracking-wider ${badge}`}
        >
          {label}
        </span>
        <span className={`min-w-0 flex-1 text-[15px] font-semibold leading-snug ${phraseTone}`}>
          {phrase}
        </span>
        {status && (
          <span className="shrink-0 pt-1 text-[10px] font-bold uppercase tracking-wide text-error">
            {status}
          </span>
        )}
      </div>
    </div>
  );
}

// ── Layer B: the 11 scoring components, as a 3-family tree ──

export function LayerB({
  letter,
  scorecard,
}: {
  letter: SfInspectionLetter;
  componentsMeta?: SfComponentMeta[];
  scorecard: SfInspectionScorecard;
}) {
  const verdict = useMemo(() => letterVerdict(letter), [letter]);
  const [openFamilies, setOpenFamilies] = useState<Set<string>>(
    () => new Set(verdict.primaryFamilyId ? [verdict.primaryFamilyId] : [])
  );
  const [openComponents, setOpenComponents] = useState<Set<string>>(
    () => new Set(verdict.primaryComponent ? [verdict.primaryComponent.name] : [])
  );

  const toggleFamily = (id: string) =>
    setOpenFamilies((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  const toggleComponent = (name: string) =>
    setOpenComponents((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });

  return (
    <div className="space-y-1.5">
      {SF_FAMILIES.map((family) => {
        const rootComp = letter.layer_b.components.find((c) => c.name === family.root);
        const isOpen = openFamilies.has(family.id);
        const tone = FAMILY_TONE[family.id];
        const anyError = familyHasAnyError(letter, family);
        const triage = familyTriageStatus(letter, family);
        return (
          <div key={family.id} className={`border-l-[3px] ${tone.leftBorder} bg-surface`}>
            <button
              onClick={() => toggleFamily(family.id)}
              className="flex w-full items-center gap-2 px-3 py-1.5 text-left"
            >
              <ChevronRight className={`h-3 w-3 shrink-0 text-muted transition-transform ${isOpen ? "rotate-90" : ""}`} />
              <span className={`text-[11px] font-bold ${tone.text}`}>{family.label}</span>
              <span
                className={`font-mono text-[10px] ${
                  anyError ? "font-bold text-error" : "text-success"
                }`}
              >
                {anyError ? `fp${triage.fp}/fn${triage.fn}` : "clean"}
              </span>
              {rootComp && (
                <span className="ml-auto font-mono text-[9px] text-muted">{family.root}</span>
              )}
            </button>
            {isOpen && (
              <div className="border-t border-border px-2 py-1.5">
                {family.id === "bench" && (
                  <p className="mb-1.5 text-[9px] text-muted">
                    Exact-match · F1 {scorecard[family.root]?.f1.toFixed(4) ?? "—"} (low by design)
                  </p>
                )}
                <div className="flex flex-col gap-0.5">
                  {family.children.map((childName) => {
                    const comp = letter.layer_b.components.find((c) => c.name === childName);
                    if (!comp) return null;
                    const childOpen = openComponents.has(childName);
                    return (
                      <div key={childName}>
                        <button
                          onClick={() => toggleComponent(childName)}
                          className={`flex w-full items-center gap-2 px-2 py-1 text-left text-[11px] ${
                            comp.has_error ? "bg-error/10" : "hover:bg-surface-raised"
                          }`}
                        >
                          <ChevronRight
                            className={`h-2.5 w-2.5 shrink-0 text-muted transition-transform ${
                              childOpen ? "rotate-90" : ""
                            }`}
                          />
                          <span className="font-mono font-semibold text-foreground">{childName}</span>
                          <span
                            className={`ml-auto font-mono text-[10px] ${
                              comp.has_error ? "font-bold text-error" : "text-muted"
                            }`}
                          >
                            {comp.rows.length === 0
                              ? "—"
                              : comp.has_error
                                ? `fp${comp.fp}/fn${comp.fn}`
                                : `tp${comp.tp}`}
                          </span>
                        </button>
                        {childOpen && (
                          <div className="ml-3 mt-1 mb-1.5">
                            <MentionFlowList rows={comp.rows} />
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ── Candidate spans (preview context) ──

/** Source text the extractor surfaced — shown first in preview as letter context. */
export function CandidateSpansContext({ spans }: { spans: SfCandidateSpan[] }) {
  if (spans.length === 0) return null;

  return (
    <section>
      <h3 className="mb-2 text-[10px] font-bold uppercase tracking-wider text-muted">
        Source spans
      </h3>
      <ul className="flex flex-col gap-2">
        {spans.map((span, i) => (
          <li
            key={i}
            className="overflow-hidden rounded-md border border-border bg-surface-raised"
          >
            <div className="flex items-stretch">
              <span className="w-1 shrink-0 bg-hybrid" aria-hidden />
              <div className="min-w-0 flex-1 px-3 py-2.5">
                <p className="font-mono text-[13px] font-semibold leading-snug text-foreground">
                  {span.text_hint}
                </p>
                {span.evidence && span.evidence !== span.text_hint && (
                  <p className="mt-1 text-[11px] leading-relaxed text-muted">{span.evidence}</p>
                )}
                <p className="mt-1.5 font-mono text-[9px] text-muted">
                  {span.candidate_type}
                  {span.source ? ` · ${span.source}` : ""}
                </p>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}

// ── Lineage panel, with override -> error connector ──

/** Compact cause block — override rewrites first; spans stay collapsed. */
export function LineagePanel({
  letter,
  hideSpans = false,
}: {
  letter: SfInspectionLetter;
  hideSpans?: boolean;
}) {
  const { lineage } = letter;
  const spans = lineage.candidate_spans;
  const override = lineage.override;
  const [spansOpen, setSpansOpen] = useState(false);
  const connections = useMemo(
    () => connectOverridesToErrors(letter, override?.applied ? override.items : undefined),
    [letter, override]
  );

  const hasOverride = !!override?.applied && (override.items?.length ?? 0) > 0;
  if (!hasOverride && spans.length === 0 && !(override && !override.applied)) {
    return <p className="text-[11px] text-muted">No lineage recorded</p>;
  }

  return (
    <div className="space-y-2">
      {hasOverride && (
        <div className="border-l-[3px] border-l-hybrid bg-hybrid/5 px-3 py-2">
          <p className="mb-1 text-[10px] font-bold uppercase tracking-wide text-hybrid">
            Magnitude override
          </p>
          <ul className="space-y-1">
            {override!.items!.map((item, i) => {
              const hit = connections.find((c) => c.item === item);
              return (
                <li key={i} className="font-mono text-[11px] text-foreground">
                  <span className="font-semibold">{item.applies_to}</span>
                  <span className="mx-1.5 text-muted">
                    <span className="text-error line-through">
                      {item.prior_frequency_change || "—"}
                    </span>
                    {" → "}
                    {item.assembled_magnitude}
                  </span>
                  {hit && (
                    <span className="ml-1 text-[10px] font-bold text-error">
                      → {STATUS_META[hit.row.status].label} {hit.component}
                    </span>
                  )}
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {override && !override.applied && (
        <p className="font-mono text-[10px] text-muted">
          FreqChg drift · baseline {JSON.stringify(override.baseline)} vs complement{" "}
          {JSON.stringify(override.complement)}
        </p>
      )}

      {!hideSpans && spans.length > 0 && (
        <div>
          <button
            type="button"
            onClick={() => setSpansOpen((v) => !v)}
            className="flex items-center gap-1 text-[10px] font-semibold text-muted hover:text-foreground"
          >
            <ChevronRight className={`h-2.5 w-2.5 transition-transform ${spansOpen ? "rotate-90" : ""}`} />
            {spans.length} candidate span{spans.length === 1 ? "" : "s"}
          </button>
          {spansOpen && (
            <ul className="mt-1 space-y-0.5 border-l border-border pl-2">
              {spans.map((span, i) => (
                <li key={i} className="text-[10px]">
                  <span className="font-mono text-foreground">{span.text_hint}</span>
                  <span className="ml-1.5 text-muted">
                    {span.candidate_type}
                    {span.evidence ? ` · ${span.evidence}` : ""}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

// ── Raw scorecard (all 11 lenses) — full-fidelity escape hatch ──

export function ScorecardTable({ scorecard }: { scorecard: SfInspectionScorecard }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-[10px]">
        <thead>
          <tr>
            <th className="border border-border bg-surface-raised px-2 py-1 text-left font-semibold text-muted">
              component
            </th>
            <th className="border border-border bg-surface-raised px-2 py-1 text-right font-semibold text-muted">
              F1
            </th>
            <th className="border border-border bg-surface-raised px-2 py-1 text-right font-semibold text-muted">
              P
            </th>
            <th className="border border-border bg-surface-raised px-2 py-1 text-right font-semibold text-muted">
              R
            </th>
            <th className="border border-border bg-surface-raised px-2 py-1 text-right font-semibold text-muted">
              TP
            </th>
            <th className="border border-border bg-surface-raised px-2 py-1 text-right font-semibold text-muted">
              FP
            </th>
            <th className="border border-border bg-surface-raised px-2 py-1 text-right font-semibold text-muted">
              FN
            </th>
          </tr>
        </thead>
        <tbody>
          {COMPONENT_ORDER.map((name) => {
            const cell = scorecard[name];
            if (!cell) return null;
            const family = SF_FAMILIES.find((f) => f.root === name || (f.children as readonly string[]).includes(name));
            const isRoot = family?.root === name;
            return (
              <tr key={name} className="odd:bg-surface">
                <td
                  className={`border border-border px-2 py-1 font-mono ${
                    isRoot ? `font-semibold ${family ? FAMILY_TONE[family.id].text : "text-foreground"}` : "text-foreground"
                  }`}
                >
                  {name}
                  {isRoot && <span className="ml-1 text-[8px] text-muted">root</span>}
                </td>
                <td className="border border-border px-2 py-1 text-right font-mono text-foreground">
                  {cell.f1.toFixed(4)}
                </td>
                <td className="border border-border px-2 py-1 text-right font-mono text-muted">
                  {cell.precision.toFixed(4)}
                </td>
                <td className="border border-border px-2 py-1 text-right font-mono text-muted">
                  {cell.recall.toFixed(4)}
                </td>
                <td className="border border-border px-2 py-1 text-right font-mono text-success">
                  {cell.tp}
                </td>
                <td className="border border-border px-2 py-1 text-right font-mono text-error">
                  {cell.fp}
                </td>
                <td className="border border-border px-2 py-1 text-right font-mono text-error">
                  {cell.fn}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
