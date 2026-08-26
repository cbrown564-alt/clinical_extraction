"use client";

import { useMemo, useState } from "react";
import { FileText, Layers3 } from "lucide-react";
import LetterRenderer from "@/components/surface/LetterRenderer";
import { EXECTV2_FAMILIES } from "@/lib/datasets";
import type {
  Exectv2Entity,
  Exectv2LetterRecord,
  Exectv2Mention,
  Exectv2RunSummary,
} from "@/lib/types";
import {
  SurfaceLayout,
  SurfaceLoading,
  SurfaceError,
  SurfaceEmpty,
  MetricChips,
  ControlBar,
  ControlField,
  ControlCombobox,
  LetterPicker,
  ExplorerBody,
  LensStrip,
  formatMetricValue,
  type LensItem,
  type MetricChip,
  type HighlightTone,
} from "@/components/surface";
import {
  exectMethodChoices,
  exectMethodRequiresModel,
  exectModelsForMethod,
  exectPickerMethodId,
  exectv2OptionLabel,
  defaultExectWorkbenchRun,
  resolveExectMethodModel,
} from "@/lib/exectv2RunOptions";
import {
  attributeRank,
  workbenchAttributeKeys,
  type AttributeRank,
} from "@/lib/attributeOrder";
import { lastRuleActionLabel } from "@/lib/plainLanguageLabels";
import { mergeFamilyHighlights } from "@/lib/letterHighlights";
import { displayPredictedEvidence } from "@/lib/predictedQuote";
import {
  alignFamilyMentions,
  attributeValuesMatch,
  type MentionPair,
  type UnmatchedGold,
  type UnmatchedPred,
} from "@/lib/exectv2AlignMentions";
import {
  compactRunLabel,
  useExectv2Run,
  useExectv2Runs,
  useExectv2UrlState,
} from "./useExectv2";

const FAMILY_IDS = EXECTV2_FAMILIES.map((f) => f.id as Exectv2Entity);

type FamilyFilter = Exectv2Entity | "all";

/**
 * Family → highlight hue, derived from the one place family tones are declared.
 * The lens strip, the family-lens dots, and the letter highlights all read this,
 * so a family's colour on the letter is always the colour of its lens
 * (Diagnosis teal, Seizure Frequency amber, Prescription green, Investigations
 * blue) and the two can never drift apart.
 */
const FAMILY_TONE = Object.fromEntries(
  EXECTV2_FAMILIES.map((f) => [f.id, f.tone as HighlightTone])
) as Record<string, HighlightTone>;

function familyTone(entity: string): HighlightTone {
  return FAMILY_TONE[entity] ?? "no-reference";
}

/** Solid swatch background per tone, for the family-lens legend dots. */
const DOT_BG: Record<string, string> = {
  deterministic: "bg-deterministic",
  "deterministic-alt": "bg-deterministic-alt",
  llm: "bg-llm",
  success: "bg-success",
  hybrid: "bg-hybrid",
  error: "bg-error",
  muted: "bg-muted",
};

function familyDescriptor(family: Exectv2Entity) {
  return EXECTV2_FAMILIES.find((f) => f.id === family);
}

function familyLabel(family: string): string {
  return EXECTV2_FAMILIES.find((f) => f.id === family)?.label ?? family;
}

function familyTextClass(family: string): string {
  switch (familyDescriptor(family as Exectv2Entity)?.tone) {
    case "deterministic":
      return "text-deterministic";
    case "deterministic-alt":
      return "text-deterministic-alt";
    case "llm":
      return "text-llm";
    case "success":
      return "text-success";
    case "hybrid":
      return "text-hybrid";
    default:
      return "text-foreground";
  }
}

function attributeNameClass(rank: AttributeRank, family: string): string {
  if (rank === "identity" || rank === "qualifier") return "text-muted/70";
  if (rank === "primary") return `${familyTextClass(family)} font-medium`;
  return "text-muted";
}

function attributeValueClass(rank: AttributeRank, family: string): string {
  if (rank === "identity" || rank === "qualifier") return "text-muted";
  if (rank === "primary") return `${familyTextClass(family)} font-medium`;
  return "text-foreground";
}

function familyTint(family: string): string {
  const tone = familyDescriptor(family as Exectv2Entity)?.tone ?? "muted";
  switch (tone) {
    case "deterministic":
      return "border-deterministic/25 bg-deterministic/8";
    case "llm":
      return "border-llm/25 bg-llm/8";
    case "success":
      return "border-success/25 bg-success/10";
    case "deterministic-alt":
      return "border-deterministic-alt/25 bg-deterministic-alt/8";
    case "hybrid":
      return "border-hybrid/25 bg-hybrid/8";
    default:
      return "border-border bg-surface";
  }
}

/**
 * Letter-level gold/predicted totals against the clinical-recovery headline unit
 * (summed from the de-duplicated `family_counts`), so every count in the surface –
 * the lens strip, the letter dropdown, and the source meta – agrees with the
 * headline chips rather than the raw mention multiset.
 */
function headlineTotals(letter: Exectv2LetterRecord): { gold: number; predicted: number } {
  return {
    gold: FAMILY_IDS.reduce((n, id) => n + letter.family_counts.gold[id], 0),
    predicted: FAMILY_IDS.reduce((n, id) => n + letter.family_counts.predicted[id], 0),
  };
}

/** The family lens row – the ExECTv2 analogue of Gan's stage strip. */
function familyLensItems(letter: Exectv2LetterRecord): LensItem[] {
  const { gold: totalGold, predicted: totalPred } = headlineTotals(letter);
  return [
    {
      id: "all",
      label: "All families",
      sublabel: `${totalPred} predicted / ${totalGold} gold`,
      count: `${totalPred}/${totalGold}`,
      tone: "foreground",
      fixed: true,
    },
    ...EXECTV2_FAMILIES.map((family): LensItem => {
      const id = family.id as Exectv2Entity;
      const gold = letter.family_counts.gold[id];
      const predicted = letter.family_counts.predicted[id];
      return {
        id,
        label: family.label,
        sublabel: `${predicted} predicted / ${gold} gold`,
        count: `${predicted}/${gold}`,
        tone: family.tone,
        icon: (
          <span
            className={`h-2 w-2 shrink-0 rounded-full ${DOT_BG[family.tone] ?? "bg-muted"}`}
            aria-hidden
          />
        ),
      };
    }),
  ];
}

/** Overall + per-family F1 of the selected run, as compact header chips. */
function runMetricChips(run: Exectv2RunSummary): MetricChip[] {
  return [
    { label: "Overall", value: run.metrics.overall_f1, format: "f1", shade: true },
    ...EXECTV2_FAMILIES.map((family): MetricChip => ({
      label: family.shortLabel,
      value: run.metrics.families[family.id as Exectv2Entity]?.f1,
      format: "f1",
      shade: true,
    })),
  ];
}

/**
 * How clinical fact recovery treats a mention's scoring unit. The drill-down
 * renders every raw mention, but the score chips use the de-duplicated unit, so
 * this badge keeps the two from silently disagreeing: a deduplicated mention
 * looks like a miss but is not charged, while a distinct-assertion duplicate
 * is genuinely counted. See CONTEXT.md (`Redundant-Convention Duplicate`,
 * `Distinct-Assertion Duplicate`).
 */
function LastRuleActionLine({ mention }: { mention: Exectv2Mention }) {
  const label = mention.last_rule_label || lastRuleActionLabel(mention.last_rule_action);
  if (!label) return null;
  return (
    <p
      className="mt-1.5 text-[11px] leading-snug text-muted"
      title={mention.last_rule_action}
    >
      {label}
    </p>
  );
}

function HeadlineStatusBadge({ status }: { status: Exectv2Mention["headline_status"] }) {
  if (status === "deduplicated") {
    return (
      <span
        className="inline-block rounded border border-dashed border-muted/40 bg-surface-raised px-1.5 py-0.5 text-[11px] font-medium text-muted"
        title="Clinical fact recovery scores one unit per distinct fact; this mention's unit was already counted from an earlier mention (it differs only in a demoted attribute), so the model is not charged for it."
      >
        removed from clinical-fact scoring - deduplicated
      </span>
    );
  }
  if (status === "distinct_assertion") {
    return (
      <span
        className="inline-block rounded border border-deterministic-alt/25 bg-deterministic-alt/8 px-1.5 py-0.5 text-[11px] font-medium text-deterministic-alt"
        title="The same concept asserted again at a distinct point in the letter. The benchmark counts each occurrence, so clinical fact recovery preserves it rather than collapsing – it is a genuine required mention."
      >
        distinct assertion – counted
      </span>
    );
  }
  return null;
}

/** Compact attribute diff table comparing gold vs predicted key-value pairs */
function AttributeDiffTable({
  family,
  goldAttrs = {},
  predAttrs = {},
}: {
  family: string;
  goldAttrs?: Record<string, string>;
  predAttrs?: Record<string, string>;
}) {
  const allKeys = workbenchAttributeKeys(
    [...Object.keys(goldAttrs), ...Object.keys(predAttrs)],
    family
  );

  if (allKeys.length === 0) return null;

  return (
    <div className="mt-2.5 overflow-hidden rounded border border-border/70 bg-surface-raised/40 text-[11px]">
      <table className="w-full border-collapse text-left">
        <thead>
          <tr className="border-b border-border/70 bg-surface-raised font-mono text-[10px] uppercase tracking-wider text-muted">
            <th className="px-2 py-1 font-medium">Attribute</th>
            <th className="px-2 py-1 font-medium">Gold</th>
            <th className="px-2 py-1 font-medium">Predicted</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border/40 font-mono">
          {allKeys.map((key) => {
            const gVal = goldAttrs[key];
            const pVal = predAttrs[key];
            const isMatch = attributeValuesMatch(key, gVal, pVal);
            const isDiff =
              gVal !== undefined && pVal !== undefined && !isMatch;
            const isMissingInPred = gVal !== undefined && pVal === undefined;
            const isExtraInPred = gVal === undefined && pVal !== undefined;
            const rank = attributeRank(key, family);
            const nameTone = attributeNameClass(rank, family);
            const valueTone = attributeValueClass(rank, family);

            return (
              <tr
                key={key}
                className={
                  isDiff
                    ? "bg-error/5"
                    : isExtraInPred
                    ? "bg-deterministic-alt/5"
                    : isMissingInPred
                    ? "bg-llm/5"
                    : undefined
                }
              >
                <td className={`px-2 py-1 ${nameTone}`}>{key}</td>
                <td className={`px-2 py-1 ${valueTone}`}>
                  {gVal ?? <span className="text-muted/40">—</span>}
                </td>
                <td className={`px-2 py-1 ${valueTone}`}>
                  {pVal ?? <span className="text-muted/40">—</span>}
                  {isMatch && (
                    <span
                      className={`ml-1 font-sans ${
                        rank === "identity" || rank === "qualifier"
                          ? "text-success/60"
                          : "text-success"
                      }`}
                    >
                      ✓
                    </span>
                  )}
                  {isDiff && <span className="ml-1 text-error font-sans font-bold">≠</span>}
                  {isExtraInPred && (
                    <span className="ml-1 text-[9px] font-sans text-deterministic-alt">
                      (extra)
                    </span>
                  )}
                  {isMissingInPred && (
                    <span className="ml-1 text-[9px] font-sans text-llm">(missed)</span>
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

function MentionRow({
  mention,
  spans = [],
  label = mention.source === "gold" ? "Gold" : "Predicted",
  badgeTone,
}: {
  mention: Exectv2Mention;
  spans?: Exectv2LetterRecord["evidence_spans"];
  label?: string;
  badgeTone?: string;
}) {
  const attrs = workbenchAttributeKeys(
    Object.keys(mention.attributes),
    mention.entity
  ).flatMap((key) => {
    const value = mention.attributes[key];
    return value === undefined ? [] : [[key, value] as const];
  });
  const deduplicated = mention.headline_status === "deduplicated";
  const evidenceText =
    mention.source === "predicted"
      ? displayPredictedEvidence(mention, spans)
      : mention.evidence;

  return (
    <div
      className={`border-b border-border/60 px-3 py-2.5 last:border-b-0 ${
        deduplicated ? "opacity-60" : ""
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5">
            {badgeTone && (
              <span className={`rounded px-1.5 py-0.2 text-[10px] font-semibold uppercase ${badgeTone}`}>
                {label}
              </span>
            )}
            <p
              className={`truncate text-xs font-semibold text-foreground ${
                deduplicated ? "line-through decoration-muted/60" : ""
              }`}
              title={mention.text}
            >
              {mention.text || "(blank mention)"}
            </p>
          </div>
          <p
            className={`mt-1 line-clamp-2 text-[11px] leading-snug text-muted ${
              mention.source === "predicted" ? "italic" : ""
            }`}
            title={evidenceText}
          >
            {evidenceText || "No evidence text"}
          </p>
        </div>
        <span
          className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-medium ${
            mention.evidence_valid ? "bg-success/10 text-success" : "bg-error/10 text-error"
          }`}
        >
          {mention.evidence_valid ? "exact" : "invalid"}
        </span>
      </div>

      {mention.headline_status && (
        <div className="mt-1.5">
          <HeadlineStatusBadge status={mention.headline_status} />
        </div>
      )}

      {attrs.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {attrs.map(([key, value]) => {
            const rank = attributeRank(key, mention.entity);
            return (
              <span
                key={`${mention.id}:${key}`}
                className={`rounded border border-border bg-surface-raised px-1.5 py-0.5 font-mono text-[10px] ${attributeValueClass(rank, mention.entity)}`}
                title={`${key}: ${value}`}
              >
                {key}: {value}
              </span>
            );
          })}
        </div>
      )}

      <LastRuleActionLine mention={mention} />
    </div>
  );
}

/** Matched Concept Row with unified header and side-by-side or attribute diff */
function MatchedGroupCard({
  pair,
  spans = [],
}: {
  pair: MentionPair;
  spans?: Exectv2LetterRecord["evidence_spans"];
}) {
  const { gold, predicted } = pair;
  const deduplicated = predicted.headline_status === "deduplicated";
  const predictedQuote = displayPredictedEvidence(predicted, spans);

  return (
    <div className="rounded-md border border-border bg-surface p-3 transition-colors hover:border-foreground/20">
      <div className="flex items-center justify-between border-b border-border/50 pb-2">
        <div className="flex items-center gap-2">
          <span className="rounded bg-success/10 px-1.5 py-0.5 text-[10px] font-semibold text-success uppercase tracking-wider">
            Matched Concept
          </span>
          <h4 className="text-xs font-semibold text-foreground">
            {predicted.text || gold.text}
          </h4>
        </div>
        <span
          className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-medium ${
            predicted.evidence_valid ? "bg-success/10 text-success" : "bg-error/10 text-error"
          }`}
        >
          {predicted.evidence_valid ? "evidence valid" : "invalid evidence"}
        </span>
      </div>

      <div className="mt-2 grid grid-cols-1 gap-2 md:grid-cols-2">
        <div className="rounded bg-surface-raised/40 p-2 text-xs">
          <div className="font-mono text-[10px] font-semibold uppercase tracking-wider text-muted">
            Gold Mention
          </div>
          <p className="mt-1 font-semibold text-foreground">{gold.text}</p>
          <p className="mt-0.5 text-[11px] leading-snug text-muted">{gold.evidence || "No evidence"}</p>
        </div>
        <div className={`rounded bg-surface-raised/40 p-2 text-xs ${deduplicated ? "opacity-60" : ""}`}>
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] font-semibold uppercase tracking-wider text-muted">
              Predicted Mention
            </span>
            {predicted.headline_status && (
              <HeadlineStatusBadge status={predicted.headline_status} />
            )}
          </div>
          <p className="mt-1 font-semibold text-foreground">{predicted.text}</p>
          <p className="mt-0.5 text-[11px] italic leading-snug text-muted">{predictedQuote || "No evidence"}</p>
          <LastRuleActionLine mention={predicted} />
        </div>
      </div>

      <AttributeDiffTable
        family={gold.entity}
        goldAttrs={gold.attributes}
        predAttrs={predicted.attributes}
      />
    </div>
  );
}

function FamilyPanel({
  family,
  letter,
  viewMode,
}: {
  family: Exectv2Entity;
  letter: Exectv2LetterRecord;
  viewMode: "matched" | "raw";
}) {
  const gold = letter.gold_mentions.filter((m) => m.entity === family);
  const predicted = letter.predicted_mentions.filter((m) => m.entity === family);
  const goldUnits = letter.family_counts.gold[family];
  const predictedUnits = letter.family_counts.predicted[family];

  const alignedGroups = useMemo(() => alignFamilyMentions(gold, predicted), [gold, predicted]);

  const matched = alignedGroups.filter((g): g is MentionPair => g.type === "matched");
  const missedGold = alignedGroups.filter((g): g is UnmatchedGold => g.type === "missed_gold");
  const extraPred = alignedGroups.filter((g): g is UnmatchedPred => g.type === "extra_predicted");

  return (
    <section className={`overflow-hidden rounded-md border ${familyTint(family)}`}>
      <div className="flex items-center justify-between border-b border-border/60 bg-surface px-3 py-2">
        <div className="flex items-center gap-2">
          <h3 className="text-xs font-semibold text-foreground">{familyLabel(family)}</h3>
          {viewMode === "matched" && (
            <div className="flex items-center gap-1 text-[11px] text-muted">
              <span className="text-success font-medium">{matched.length} matched</span>
              {missedGold.length > 0 && (
                <>
                  <span>•</span>
                  <span className="text-llm font-medium">{missedGold.length} missed</span>
                </>
              )}
              {extraPred.length > 0 && (
                <>
                  <span>•</span>
                  <span className="text-deterministic-alt font-medium">{extraPred.length} extra</span>
                </>
              )}
            </div>
          )}
        </div>
        <div className="flex items-center gap-1 font-mono text-[11px] text-muted">
          <span>G {goldUnits}</span>
          <span>/</span>
          <span>P {predictedUnits}</span>
        </div>
      </div>

      {viewMode === "matched" ? (
        <div className="space-y-3 bg-surface/50 p-3">
          {alignedGroups.length === 0 ? (
            <div className="py-4 text-center text-xs text-muted">No mentions for this family</div>
          ) : (
            <>
              {/* Matched True Positives */}
              {matched.length > 0 && (
                <div className="space-y-2">
                  {matched.map((pair) => (
                    <MatchedGroupCard
                      key={`matched-${pair.gold.id}-${pair.predicted.id}`}
                      pair={pair}
                      spans={letter.evidence_spans}
                    />
                  ))}
                </div>
              )}

              {/* Missed Gold Mentions (FN) */}
              {missedGold.length > 0 && (
                <div className="rounded-md border border-llm/30 bg-llm/5 p-2.5">
                  <div className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-llm">
                    Missed Gold Mentions ({missedGold.length})
                  </div>
                  <div className="divide-y divide-llm/15 rounded border border-llm/20 bg-surface">
                    {missedGold.map((item) => (
                      <MentionRow
                        key={`missed-${item.gold.id}`}
                        mention={item.gold}
                        spans={letter.evidence_spans}
                        label="Missed Gold"
                        badgeTone="bg-llm/15 text-llm"
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Extra Predictions / Duplicates (FP) */}
              {extraPred.length > 0 && (
                <div className="rounded-md border border-deterministic-alt/30 bg-deterministic-alt/5 p-2.5">
                  <div className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-deterministic-alt">
                    Extra / Duplicate Predictions ({extraPred.length})
                  </div>
                  <div className="divide-y divide-deterministic-alt/15 rounded border border-deterministic-alt/20 bg-surface">
                    {extraPred.map((item) => (
                      <MentionRow
                        key={`extra-${item.predicted.id}`}
                        mention={item.predicted}
                        spans={letter.evidence_spans}
                        label="Extra Pred"
                        badgeTone="bg-deterministic-alt/15 text-deterministic-alt"
                      />
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      ) : (
        /* Raw 2-column view */
        <div className="grid grid-cols-1 divide-y divide-border/60 bg-surface md:grid-cols-2 md:divide-x md:divide-y-0">
          <div>
            <div className="border-b border-border/60 px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted">
              Gold
            </div>
            {gold.length === 0 ? (
              <div className="px-3 py-4 text-xs text-muted">No gold mentions</div>
            ) : (
              gold.map((mention) => (
                <MentionRow key={mention.id} mention={mention} spans={letter.evidence_spans} />
              ))
            )}
          </div>
          <div>
            <div className="border-b border-border/60 px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted">
              Predicted
            </div>
            {predicted.length === 0 ? (
              <div className="px-3 py-4 text-xs text-muted">No predicted mentions</div>
            ) : (
              predicted.map((mention) => (
                <MentionRow
                  key={mention.id}
                  mention={mention}
                  spans={letter.evidence_spans}
                />
              ))
            )}
          </div>
        </div>
      )}
    </section>
  );
}

/** The inspector pane: family gold-vs-predicted panels for the active lens. */
function FamilyInspector({
  letter,
  activeFamily,
}: {
  letter: Exectv2LetterRecord;
  activeFamily: FamilyFilter;
}) {
  const [viewMode, setViewMode] = useState<"matched" | "raw">("matched");
  const families = activeFamily === "all" ? FAMILY_IDS : [activeFamily];
  const descriptor = activeFamily === "all" ? null : familyDescriptor(activeFamily);

  return (
    <div className="flex h-full flex-col">
      {/* Compact inspector header with view switcher */}
      <div className="shrink-0 border-b border-border bg-surface px-4 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers3 className="h-3.5 w-3.5 text-muted" />
            <h3 className="text-xs font-semibold text-foreground">
              {activeFamily === "all" ? "All families" : familyLabel(activeFamily)}
            </h3>
            <span className="hidden text-[11px] text-muted sm:inline">
              {descriptor
                ? "Gold vs predicted mentions for this family."
                : "Gold vs predicted mentions across all four families."}
            </span>
          </div>

          <div className="flex items-center rounded-md border border-border bg-surface-raised p-0.5 text-[11px]">
            <button
              type="button"
              onClick={() => setViewMode("matched")}
              className={`rounded px-2 py-0.5 font-medium transition-colors ${
                viewMode === "matched"
                  ? "bg-surface font-semibold text-foreground shadow-xs"
                  : "text-muted hover:text-foreground"
              }`}
            >
              Matched Diff
            </button>
            <button
              type="button"
              onClick={() => setViewMode("raw")}
              className={`rounded px-2 py-0.5 font-medium transition-colors ${
                viewMode === "raw"
                  ? "bg-surface font-semibold text-foreground shadow-xs"
                  : "text-muted hover:text-foreground"
              }`}
            >
              Raw Lists
            </button>
          </div>
        </div>
      </div>
      {/* Panels */}
      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {families.map((family) => (
          <FamilyPanel
            key={family}
            family={family}
            letter={letter}
            viewMode={viewMode}
          />
        ))}
      </div>
    </div>
  );
}

export default function Exectv2ExampleExplorer() {
  const { runs, isLoading, error } = useExectv2Runs();
  const { get, set } = useExectv2UrlState();
  const [activeFamily, setActiveFamily] = useState<FamilyFilter>("all");
  const selectedRunSummary = useMemo(
    () => defaultExectWorkbenchRun(runs, get("run")),
    [runs, get]
  );
  const selectedRunQuery = useExectv2Run(selectedRunSummary?.run_id);
  const selectedRun = selectedRunQuery.data;

  const selectedLetter = useMemo(() => {
    if (!selectedRun) return undefined;
    return (
      selectedRun.letters.find((letter) => letter.letter_id === get("letter")) ??
      selectedRun.letters[0]
    );
  }, [get, selectedRun]);

  const letterItems = useMemo(() => {
    if (!selectedRun) return [];
    return selectedRun.letters.map((letter) => {
      const totals = headlineTotals(letter);
      return {
        value: letter.letter_id,
        label: `${letter.letter_id} – ${totals.predicted}P / ${totals.gold}G`,
      };
    });
  }, [selectedRun]);

  const selectedMethodId = selectedRunSummary
    ? exectPickerMethodId(selectedRunSummary)
    : "llm_extract";
  const methodItems = useMemo(
    () =>
      exectMethodChoices(runs).map((method) => ({
        value: method.id,
        label: method.label,
      })),
    [runs]
  );
  const modelItems = useMemo(
    () =>
      exectModelsForMethod(runs, selectedMethodId).map((run) => ({
        value: run.model,
        label: exectv2OptionLabel(run),
      })),
    [runs, selectedMethodId]
  );

  if (isLoading || selectedRunQuery.isLoading) {
    return <SurfaceLoading message="Loading ExECTv2 data…" />;
  }
  if (error || selectedRunQuery.error) {
    return (
      <SurfaceError
        title="ExECTv2 data failed to load"
        detail={String(error ?? selectedRunQuery.error)}
      />
    );
  }

  if (!selectedRun || !selectedLetter) {
    return (
      <SurfaceLayout variant="fill">
        <div className="p-5">
          <SurfaceEmpty message="No ExECTv2 architectures available." />
        </div>
      </SurfaceLayout>
    );
  }

  // Colour each evidence span by its family so the letter matches the lens
  // strip; when a single family lens is active, show only that family's spans
  // (mirroring how Gan's stage selection drives the note highlights). Overlap
  // and whitespace-only gaps collapse to one run so gold/predicted chips do
  // not punch holes in the same phrase.
  const highlightSpans = mergeFamilyHighlights(
    selectedLetter.evidence_spans.filter(
      (span) => activeFamily === "all" || span.entity === activeFamily
    ),
    selectedLetter.letter_text
  ).map((span) => ({
    start: span.start,
    end: span.end,
    kind: familyTone(String(span.entity)),
    label: span.label,
  }));

  return (
    <SurfaceLayout variant="fill">
      {/* Control bar – method on far left, letter picker next, metrics on the right */}
      <ControlBar
        left={
          <>
            <ControlField label="Method" htmlFor="exect-method-select">
              <ControlCombobox
                id="exect-method-select"
                noun="method"
                items={methodItems}
                value={selectedMethodId}
                title={selectedRun.claim_boundary}
                onChange={(methodId) => {
                  const next = resolveExectMethodModel(
                    runs,
                    methodId,
                    selectedRun.model
                  );
                  if (next) set({ run: next.run_id });
                }}
                className="min-w-0 flex-1 sm:min-w-[220px] sm:flex-none"
              />
            </ControlField>

            {exectMethodRequiresModel(selectedMethodId) && (
              <ControlField label="Model" htmlFor="exect-model-select">
                <ControlCombobox
                  id="exect-model-select"
                  noun="model"
                  items={modelItems}
                  value={selectedRun.model}
                  onChange={(model) => {
                    const next = resolveExectMethodModel(
                      runs,
                      selectedMethodId,
                      model
                    );
                    if (next) set({ run: next.run_id });
                  }}
                  className="min-w-0 flex-1 sm:min-w-[200px] sm:flex-none"
                />
              </ControlField>
            )}

            <ControlField label="Letter" htmlFor="exect-letter-select" icon={<FileText className="h-3 w-3 text-muted" />}>
              <LetterPicker
                id="exect-letter-select"
                items={letterItems}
                value={selectedLetter.letter_id}
                onChange={(letter) => set({ letter })}
                className="min-w-0 flex-1 sm:min-w-[240px] sm:flex-none"
              />
            </ControlField>
          </>
        }
        right={<MetricChips chips={runMetricChips(selectedRun)} />}
      />

      {/* Lens strip – family filter */}
      <LensStrip
        items={familyLensItems(selectedLetter)}
        activeId={activeFamily}
        onSelect={(id) => setActiveFamily(id as FamilyFilter)}
      />

      {/* Two-pane body – letter on the left, family inspector on the right */}
      <ExplorerBody
        sourceLabel="Letter"
        sourceMeta={
          <div className="flex items-center gap-2">
            <span className="rounded bg-surface-raised px-1 py-0 font-mono text-[11px] text-muted border border-border">
              {selectedLetter.letter_id}
            </span>
            <span className="text-[11px] text-muted">
              {headlineTotals(selectedLetter).predicted} predicted / {headlineTotals(selectedLetter).gold} gold
            </span>
            <span className="font-mono text-[11px] text-muted">
              {selectedLetter.letter_text.length.toLocaleString()} chars
            </span>
          </div>
        }
        source={<LetterRenderer text={selectedLetter.letter_text} highlights={highlightSpans} />}
        inspector={<FamilyInspector letter={selectedLetter} activeFamily={activeFamily} />}
      />
    </SurfaceLayout>
  );
}
