"use client";

import { useMemo, useState } from "react";
import { FileText, Layers3 } from "lucide-react";
import LetterRenderer from "@/components/observatory/LetterRenderer";
import { exectv2Dataset, EXECTV2_FAMILIES } from "@/lib/datasets";
import type {
  Exectv2Entity,
  Exectv2LetterRecord,
  Exectv2Mention,
  Exectv2RunSummary,
} from "@/lib/types";
import {
  SurfaceHeader,
  SurfaceLayout,
  SurfaceLoading,
  SurfaceError,
  SurfaceEmpty,
  MetricChips,
  SurfaceLink,
  ControlBar,
  ControlField,
  ControlSelect,
  ExplorerBody,
  LensStrip,
  formatMetricValue,
  type LensItem,
  type MetricChip,
  type HighlightTone,
} from "@/components/surface";
import { groupExectv2Runs, resolveExectv2RunId } from "@/lib/exectv2RunOptions";
import {
  compactRunLabel,
  useExectv2Run,
  useExectv2Runs,
  useExectv2UrlState,
} from "./useExectv2";
import { Exectv2ModeBadge } from "./Exectv2ModeBadge";

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

function MentionRow({ mention }: { mention: Exectv2Mention }) {
  const attrs = Object.entries(mention.attributes).slice(0, 6);
  const deduplicated = mention.headline_status === "deduplicated";
  return (
    <div className={`border-b border-border/60 px-3 py-2 last:border-b-0 ${deduplicated ? "opacity-60" : ""}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p
            className={`truncate text-xs font-semibold text-foreground ${deduplicated ? "line-through decoration-muted/60" : ""}`}
            title={mention.text}
          >
            {mention.text || "(blank mention)"}
          </p>
          <p className="mt-1 line-clamp-2 text-[11px] leading-snug text-muted" title={mention.evidence}>
            {mention.evidence || "No evidence text"}
          </p>
        </div>
        <span
          className={`shrink-0 rounded px-1.5 py-0.5 text-[11px] font-medium ${
            mention.evidence_valid ? "bg-success/10 text-success" : "bg-error/10 text-error"
          }`}
        >
          {mention.evidence_valid ? "exact" : "invalid"}
        </span>
      </div>
      {mention.headline_status && (
        <div className="mt-2">
          <HeadlineStatusBadge status={mention.headline_status} />
        </div>
      )}
      {attrs.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {attrs.map(([key, value]) => (
            <span
              key={`${mention.id}:${key}`}
              className="rounded border border-border bg-surface-raised px-1.5 py-0.5 font-mono text-[11px] text-muted"
              title={`${key}: ${value}`}
            >
              {key}: {value}
            </span>
          ))}
        </div>
      )}
      {(mention.component_owner || mention.source_lane) && (
        <p className="mt-2 truncate font-mono text-[11px] text-muted">
          {mention.component_owner || "owner unknown"}
          {mention.source_lane ? ` / ${mention.source_lane}` : ""}
        </p>
      )}
    </div>
  );
}

function FamilyPanel({
  family,
  letter,
}: {
  family: Exectv2Entity;
  letter: Exectv2LetterRecord;
}) {
  const gold = letter.gold_mentions.filter((m) => m.entity === family);
  const predicted = letter.predicted_mentions.filter((m) => m.entity === family);
  // Counts are the headline-unit counts (deduplicated mentions excluded), so the
  // panel header agrees with the headline chips rather than the raw multiset of
  // rendered rows below it.
  const goldUnits = letter.family_counts.gold[family];
  const predictedUnits = letter.family_counts.predicted[family];
  return (
    <section className={`overflow-hidden rounded-md border ${familyTint(family)}`}>
      <div className="flex items-center justify-between border-b border-border/60 px-3 py-2">
        <h3 className="text-xs font-semibold text-foreground">{familyLabel(family)}</h3>
        <div className="flex items-center gap-1 font-mono text-[11px] text-muted">
          <span>G {goldUnits}</span>
          <span>/</span>
          <span>P {predictedUnits}</span>
        </div>
      </div>
      <div className="grid grid-cols-1 divide-y divide-border/60 bg-surface md:grid-cols-2 md:divide-x md:divide-y-0">
        <div>
          <div className="border-b border-border/60 px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted">
            Gold
          </div>
          {gold.length === 0 ? (
            <div className="px-3 py-4 text-xs text-muted">No gold mentions</div>
          ) : (
            gold.map((mention) => <MentionRow key={mention.id} mention={mention} />)
          )}
        </div>
        <div>
          <div className="border-b border-border/60 px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted">
            Predicted
          </div>
          {predicted.length === 0 ? (
            <div className="px-3 py-4 text-xs text-muted">No predicted mentions</div>
          ) : (
            predicted.map((mention) => <MentionRow key={mention.id} mention={mention} />)
          )}
        </div>
      </div>
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
  const families = activeFamily === "all" ? FAMILY_IDS : [activeFamily];
  const descriptor = activeFamily === "all" ? null : familyDescriptor(activeFamily);
  return (
    <div className="flex h-full flex-col">
      {/* Compact inspector header, mirroring Gan's StageInspector */}
      <div className="shrink-0 border-b border-border bg-surface px-4 py-2">
        <div className="flex items-center gap-2">
          <Layers3 className="h-3.5 w-3.5 text-muted" />
          <h3 className="text-xs font-semibold text-foreground">
            {activeFamily === "all" ? "All families" : familyLabel(activeFamily)}
          </h3>
          <span className="text-[11px] text-muted">
            {descriptor
              ? "Gold vs predicted mentions for this family."
              : "Gold vs predicted mentions across all four families."}
          </span>
        </div>
      </div>
      {/* Panels */}
      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {families.map((family) => (
          <FamilyPanel key={family} family={family} letter={letter} />
        ))}
      </div>
    </div>
  );
}

export default function Exectv2ExampleExplorer() {
  const { runs, isLoading, error } = useExectv2Runs();
  const { get, set } = useExectv2UrlState();
  const [activeFamily, setActiveFamily] = useState<FamilyFilter>("all");
  const runGroups = useMemo(() => groupExectv2Runs(runs), [runs]);

  const selectedRunSummary = useMemo(
    () => {
      const requested = get("run");
      const resolved = requested ? resolveExectv2RunId(runs, requested) : null;
      return runs.find((run) => run.run_id === resolved) ?? runs[0];
    },
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
      <SurfaceLayout variant="fill" header={<SurfaceHeader surface="workbench" dataset={exectv2Dataset} />}>
        <div className="p-5">
          <SurfaceEmpty message="No ExECTv2 architectures available." />
        </div>
      </SurfaceLayout>
    );
  }

  // Colour each evidence span by its family so the letter matches the lens
  // strip; when a single family lens is active, show only that family's spans
  // (mirroring how Gan's stage selection drives the note highlights).
  const highlightSpans = selectedLetter.evidence_spans
    .filter((span) => activeFamily === "all" || span.entity === activeFamily)
    .map((span) => ({
      start: span.start,
      end: span.end,
      kind: familyTone(String(span.entity)),
      label: span.label,
    }));

  return (
    <SurfaceLayout
      variant="fill"
      header={
        <SurfaceHeader
          surface="workbench"
          dataset={exectv2Dataset}
          description="How a prediction matures per family, with evidence highlighting on the source letter."
          right={
            <>
              <MetricChips chips={runMetricChips(selectedRun)} />
              <span className="rounded border border-success/25 bg-success/10 px-2 py-1 text-[11px] font-medium text-success">
                exact evidence {formatMetricValue(selectedRun.operational.exact_evidence_rate, "rate")}
              </span>
              <SurfaceLink surface="observatory" datasetId="exectv2" params={{ runs: selectedRun.run_id }} label="Aggregate" />
              <SurfaceLink surface="gallery" datasetId="exectv2" params={{ runs: selectedRun.run_id }} label="Errors" />
            </>
          }
        />
      }
    >
      {/* Control bar – specimen (letter) on the left, variant (architecture) on the right */}
      <ControlBar
        left={
          <ControlField label="Letter" htmlFor="exect-letter-select" icon={<FileText className="h-3 w-3 text-muted" />}>
            <ControlSelect
              id="exect-letter-select"
              value={selectedLetter.letter_id}
              onChange={(event) => set({ letter: event.target.value })}
              className="min-w-0 flex-1 sm:min-w-[200px] sm:flex-none"
            >
              {selectedRun.letters.map((letter) => {
                const totals = headlineTotals(letter);
                return (
                  <option key={letter.letter_id} value={letter.letter_id}>
                    {letter.letter_id} – {totals.predicted}P / {totals.gold}G
                  </option>
                );
              })}
            </ControlSelect>
          </ControlField>
        }
        right={
          <ControlField label="Architecture" htmlFor="exect-architecture-select" icon={<Layers3 className="h-3 w-3 text-muted" />}>
            <ControlSelect
              id="exect-architecture-select"
              value={selectedRun.run_id}
              title={selectedRun.claim_boundary}
              onChange={(event) => set({ run: event.target.value })}
              className="min-w-0 flex-1 sm:min-w-[200px] sm:flex-none"
            >
              {runGroups.map((group) => (
                <optgroup key={group.method} label={group.label}>
                  {group.runs.map((run) => (
                    <option key={run.run_id} value={run.run_id}>
                      {compactRunLabel(run)} · {run.model}
                    </option>
                  ))}
                </optgroup>
              ))}
            </ControlSelect>
            <Exectv2ModeBadge run={selectedRun} />
            <span className="rounded border border-border bg-surface-raised px-1.5 py-0.5 font-mono text-[11px] text-muted">
              {selectedRun.split} / {selectedRun.row_count}
            </span>
          </ControlField>
        }
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
