"use client";

import { ArrowRight, Check, MousePointerClick, X } from "lucide-react";
import type { DatasetTone } from "@/lib/datasets";
import { TONE_CLASSES } from "@/lib/datasets";
import type { LadderStage } from "@/lib/componentLadder";
import type {
  Gan2026LadderCategory,
  Gan2026TransitionArchitecture,
  Gan2026TransitionExample,
  Gan2026TransitionStage,
} from "@/lib/types";
import { StageChip } from "@/components/laboratory/ComponentLadderSurface";

// ── Gan per-note label-trajectory sidebar (illustrative worked example) ──────
//
// A Gan prediction is a single seizure-frequency label, not a set of mentions, so
// the worked example is a label *trajectory*: for one real note, the predicted
// label at each rung and the purist boundary band it lands in, with the clicked
// stage focused (before → after) and the whole trajectory shown beneath for
// context. Explanatory only – never a scoring surface.

interface BandStyle {
  label: string;
  tone: DatasetTone;
}

function bandLookup(categories: Gan2026LadderCategory[]): (band: string | null) => BandStyle {
  const byId = new Map<string, BandStyle>(
    categories.map((c) => [c.id, { label: c.short_label, tone: c.tone as DatasetTone }])
  );
  return (band) => byId.get(band ?? "") ?? { label: band ?? "–", tone: "muted" };
}

function BandChip({ label, tone }: BandStyle) {
  return (
    <span
      className={`shrink-0 rounded border px-1.5 py-0.5 text-[11px] font-medium ${TONE_CLASSES[tone]}`}
    >
      {label}
    </span>
  );
}

/** A predicted label + its band chip on one line. */
function LabelBand({
  predictedLabel,
  band,
  strike = false,
}: {
  predictedLabel: string;
  band: BandStyle;
  strike?: boolean;
}) {
  return (
    <span className="flex min-w-0 items-center gap-1.5">
      <span
        className={`truncate text-xs font-medium ${strike ? "text-muted line-through" : "text-foreground"}`}
        title={predictedLabel}
      >
        {predictedLabel}
      </span>
      <BandChip {...band} />
    </span>
  );
}

function CorrectMark({ correct }: { correct: boolean }) {
  return correct ? (
    <Check className="h-3 w-3 shrink-0 text-success" aria-label="matches gold band" />
  ) : (
    <X className="h-3 w-3 shrink-0 text-error" aria-label="differs from gold band" />
  );
}

/** The clicked stage's effect on this note: floor, before → after, or pass-through. */
function StageFocus({
  stage,
  bandOf,
}: {
  stage: Gan2026TransitionStage;
  bandOf: (band: string | null) => BandStyle;
}) {
  if (stage.is_baseline) {
    return (
      <div className="mt-3 space-y-1.5">
        <p className="text-[11px] text-muted">
          Producer floor – the model&apos;s starting label, before any deterministic stage.
        </p>
        <div className="flex items-center justify-between gap-2 rounded border border-border bg-surface-raised/30 px-2 py-1.5">
          <LabelBand predictedLabel={stage.predicted_label} band={bandOf(stage.band)} />
          <CorrectMark correct={stage.correct} />
        </div>
      </div>
    );
  }
  if (!stage.changed) {
    return (
      <p className="mt-3 rounded border border-dashed border-border px-2 py-2 text-[11px] text-muted">
        No change for this note – the label passed through this stage unchanged.
      </p>
    );
  }
  return (
    <div className="mt-3 space-y-1.5">
      <div className="flex items-center gap-1 text-[11px] font-semibold uppercase tracking-wider text-llm">
        Changed
        {stage.band_changed && <span className="font-mono text-muted">· band moved</span>}
      </div>
      <div className="rounded border border-llm/40 bg-llm/5 px-2 py-1.5">
        <div className="flex items-center gap-2">
          <LabelBand
            predictedLabel={stage.previous_label ?? "–"}
            band={bandOf(stage.previous_band)}
            strike
          />
        </div>
        <div className="mt-1 flex items-center gap-2">
          <ArrowRight className="h-3 w-3 shrink-0 text-llm" />
          <LabelBand predictedLabel={stage.predicted_label} band={bandOf(stage.band)} />
          <CorrectMark correct={stage.correct} />
        </div>
      </div>
    </div>
  );
}

/** The whole rung-by-rung trajectory for context, with the clicked stage lit. */
function Trajectory({
  example,
  selectedStageId,
  bandOf,
}: {
  example: Gan2026TransitionExample;
  selectedStageId: string;
  bandOf: (band: string | null) => BandStyle;
}) {
  const goldBand = bandOf(example.gold_band);
  return (
    <div className="mt-4 border-t border-border pt-3">
      <div className="mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted">
        Trajectory
      </div>
      <div className="space-y-0.5">
        {example.stages.map((stage) => {
          const active = stage.stage_id === selectedStageId;
          return (
            <div
              key={stage.stage_id}
              className={`flex items-center gap-2 rounded px-1.5 py-1 ${
                active ? "bg-deterministic/8 ring-1 ring-inset ring-deterministic/30" : ""
              }`}
            >
              <span
                className="w-28 shrink-0 truncate text-[11px] uppercase tracking-wide text-muted"
                title={stage.label}
              >
                {stage.label}
              </span>
              <span className="min-w-0 flex-1">
                <LabelBand predictedLabel={stage.predicted_label} band={bandOf(stage.band)} />
              </span>
              {stage.changed ? (
                <CorrectMark correct={stage.correct} />
              ) : (
                <span className="h-3 w-3 shrink-0" />
              )}
            </div>
          );
        })}
        {/* gold reference row */}
        <div className="flex items-center gap-2 rounded border-t border-dashed border-border px-1.5 pt-1.5">
          <span className="w-28 shrink-0 truncate text-[11px] font-semibold uppercase tracking-wide text-success">
            gold
          </span>
          <span className="min-w-0 flex-1">
            <LabelBand predictedLabel={example.gold_label} band={goldBand} />
          </span>
          <span className="h-3 w-3 shrink-0" />
        </div>
      </div>
    </div>
  );
}

export default function GanTransitionSidebar({
  archTransitions,
  categories,
  ladderStages,
  exampleIndex,
  onSelectExample,
  selectedStageId,
}: {
  archTransitions: Gan2026TransitionArchitecture;
  categories: Gan2026LadderCategory[];
  ladderStages: LadderStage[];
  exampleIndex: number;
  onSelectExample: (index: number) => void;
  selectedStageId: string;
}) {
  const bandOf = bandLookup(categories);
  const example: Gan2026TransitionExample | undefined =
    archTransitions.examples[exampleIndex] ?? archTransitions.examples[0];
  const stage: Gan2026TransitionStage | undefined = example?.stages.find(
    (s) => s.stage_id === selectedStageId
  );
  const ladderStage = ladderStages.find((s) => s.id === selectedStageId);

  return (
    <aside className="flex flex-col overflow-hidden rounded-md border border-border bg-surface">
      <div className="border-b border-border px-4 py-3">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted">
          <MousePointerClick className="h-3.5 w-3.5" />
          Worked example
        </div>
        <p className="mt-1 text-[11px] text-muted">
          What each stage does to one real note – illustrative, not a scoring surface.
        </p>
      </div>

      {/* note selector */}
      <div className="flex flex-wrap items-center gap-1.5 border-b border-border px-4 py-2.5">
        <span className="mr-1 text-[11px] uppercase tracking-wider text-muted">Note</span>
        {archTransitions.examples.map((ex, index) => (
          <button
            key={ex.row_id ?? index}
            type="button"
            onClick={() => onSelectExample(index)}
            className={`rounded border px-1.5 py-0.5 font-mono text-[11px] transition-colors ${
              index === exampleIndex
                ? "border-deterministic/40 bg-deterministic/10 text-deterministic"
                : "border-border text-muted hover:bg-surface-raised/70"
            }`}
          >
            {ex.row_label}
          </button>
        ))}
        {example && (
          <span className="ml-auto flex items-center gap-1.5 font-mono text-[11px] text-muted">
            gold
            <span className="text-foreground" title={example.gold_label}>
              {example.gold_label}
            </span>
            <BandChip {...bandOf(example.gold_band)} />
          </span>
        )}
      </div>

      {/* selected stage focus + full trajectory */}
      <div className="flex-1 px-4 py-3">
        {!stage || !ladderStage || !example ? (
          <p className="text-xs text-muted">Select a stage to see its effect.</p>
        ) : (
          <>
            <div className="flex items-center gap-2">
              <StageChip stage={ladderStage} />
              <span className="text-xs font-semibold text-foreground">{stage.label}</span>
            </div>
            <p className="mt-1 text-[11px] leading-relaxed text-muted">{stage.interpretation}</p>

            <StageFocus stage={stage} bandOf={bandOf} />

            {stage.evidence && (
              <p className="mt-2 line-clamp-3 text-[11px] italic leading-snug text-muted/80">
                “{stage.evidence}”
              </p>
            )}

            <Trajectory
              example={example}
              selectedStageId={selectedStageId}
              bandOf={bandOf}
            />
          </>
        )}
      </div>
    </aside>
  );
}
