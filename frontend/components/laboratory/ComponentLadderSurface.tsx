"use client";

import { useMemo, useState, type ReactNode } from "react";
import {
  Layers3,
  TrendingUp,
  TrendingDown,
  ArrowRight,
  Plus,
  Minus,
  Pencil,
  MousePointerClick,
  Eye,
  EyeOff,
} from "lucide-react";
import type { DatasetDescriptor, DatasetTone } from "@/lib/datasets";
import { TONE_CLASSES } from "@/lib/datasets";
import {
  biggestMover,
  ladderDomain,
  type ComponentLadder,
  type LadderArchitecture,
  type LadderStage,
} from "@/lib/componentLadder";
import type {
  Exectv2ComponentTransitionsResponse,
  Exectv2TransitionArchitecture,
  Exectv2TransitionChange,
  Exectv2TransitionExample,
  Exectv2TransitionMention,
  Exectv2TransitionStage,
} from "@/lib/types";
import {
  SurfaceHeader,
  SurfaceLayout,
  DecisionBadge,
} from "@/components/surface";

/** Solid bar fills per tone — static strings so Tailwind keeps them in the build. */
const BAR_FILL: Record<DatasetTone, string> = {
  deterministic: "bg-deterministic",
  "deterministic-alt": "bg-deterministic-alt",
  llm: "bg-llm",
  hybrid: "bg-hybrid",
  success: "bg-success",
  error: "bg-error",
  muted: "bg-muted",
};

/** Score → two decimals (0.92). The shared "fewer decimals" rule. */
function fmtScore(value: number | null | undefined): string {
  if (typeof value !== "number" || Number.isNaN(value)) return "—";
  return value.toFixed(2);
}

/** Delta → signed points, no decimals (+4, −3, ~0). */
function fmtPts(value: number | null | undefined): string {
  if (typeof value !== "number" || Number.isNaN(value)) return "—";
  const pts = Math.round(value * 100);
  if (pts === 0) return "~0";
  return `${pts > 0 ? "+" : "−"}${Math.abs(pts)}`;
}

function ptsTone(value: number): string {
  if (Math.abs(value) < 0.005) return "text-muted";
  return value > 0 ? "text-success" : "text-error";
}

function StageChip({ stage }: { stage: LadderStage }) {
  return (
    <span
      className={`shrink-0 rounded border px-1.5 py-0.5 text-[9px] font-medium ${TONE_CLASSES[stage.tone]}`}
    >
      {stage.componentTypeLabel}
    </span>
  );
}

/**
 * One waterfall row on a fixed 0–100 axis. The baseline (first, biggest) block
 * runs from 0 up to its score; every later stage is a smaller block that starts
 * where the running total left off and adds its contribution on top — solid and
 * colored by component type (red when it regresses). A faint base behind each
 * block shows the accumulated score it builds on, so the blocks staircase to the
 * right toward the final score.
 */
function WaterfallRow({
  stage,
  previousScore,
  metricLabel,
  interactive = false,
  selected = false,
  onSelect,
}: {
  stage: LadderStage;
  previousScore: number;
  metricLabel: string;
  interactive?: boolean;
  selected?: boolean;
  onSelect?: () => void;
}) {
  const pct = (value: number) => value * 100;

  const carriedTo = stage.isBaseline ? 0 : Math.min(previousScore, stage.score);
  const lo = stage.isBaseline ? 0 : Math.min(previousScore, stage.score);
  const hi = stage.isBaseline ? stage.score : Math.max(previousScore, stage.score);
  const regressed = !stage.isBaseline && stage.score < previousScore;
  const tone: DatasetTone = regressed ? "error" : stage.tone;

  const RowTag = interactive ? "button" : "div";

  return (
    <RowTag
      {...(interactive
        ? {
            type: "button" as const,
            onClick: onSelect,
            "aria-pressed": selected,
          }
        : {})}
      className={`flex w-full items-center gap-3 rounded py-1 text-left transition-colors ${
        interactive ? "cursor-pointer px-1.5 hover:bg-surface-raised/60" : ""
      } ${selected ? "bg-deterministic/8 ring-1 ring-inset ring-deterministic/30" : ""}`}
    >
      <div className="flex w-56 shrink-0 flex-col items-start gap-1">
        <span className="max-w-full truncate text-[11px] font-medium text-foreground" title={stage.label}>
          {stage.label}
        </span>
        <StageChip stage={stage} />
      </div>
      <div className="relative h-7 flex-1 overflow-hidden rounded bg-surface-raised/30 ring-1 ring-inset ring-border/60">
        {/* fixed 0–100 gridlines */}
        {[25, 50, 75].map((g) => (
          <div key={g} className="absolute top-0 h-full w-px bg-border/60" style={{ left: `${g}%` }} />
        ))}
        {/* accumulated base this contribution builds on */}
        {carriedTo > 0 && (
          <div
            className="absolute top-0 h-full bg-muted/12"
            style={{ left: 0, width: `${pct(carriedTo)}%` }}
          />
        )}
        {/* this stage's contribution */}
        <div
          className={`absolute top-0 h-full ${BAR_FILL[tone]}`}
          style={{ left: `${pct(lo)}%`, width: `${Math.max(pct(hi) - pct(lo), 0.8)}%` }}
          title={`${stage.label}: ${fmtScore(stage.score)} ${metricLabel}`}
        />
      </div>
      <div className="w-12 shrink-0 text-right font-mono text-[12px] font-semibold text-foreground">
        {fmtScore(stage.score)}
      </div>
      <div
        className={`w-12 shrink-0 text-right font-mono text-[12px] font-semibold ${
          stage.isBaseline ? "text-muted" : ptsTone(stage.deltaFromPrevious)
        }`}
      >
        {stage.isBaseline ? "base" : fmtPts(stage.deltaFromPrevious)}
      </div>
    </RowTag>
  );
}

/** The 0–100 tick labels, aligned under the bar track. */
function WaterfallAxis({ inset = false }: { inset?: boolean }) {
  return (
    <div className={`flex items-center gap-3 pt-1.5 ${inset ? "px-1.5" : ""}`}>
      <div className="w-56 shrink-0" />
      <div className="flex flex-1 justify-between font-mono text-[9px] text-muted">
        {["0.0", "0.25", "0.5", "0.75", "1.0"].map((tick) => (
          <span key={tick}>{tick}</span>
        ))}
      </div>
      <div className="w-12 shrink-0" />
      <div className="w-12 shrink-0" />
    </div>
  );
}

function Waterfall({
  arch,
  metricLabel,
  interactive = false,
  selectedStageId,
  onSelectStage,
}: {
  arch: LadderArchitecture;
  metricLabel: string;
  interactive?: boolean;
  selectedStageId?: string;
  onSelectStage?: (stageId: string) => void;
}) {
  return (
    <section className="overflow-hidden rounded-md border border-border bg-surface">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-wider text-muted">
          <Layers3 className="h-3.5 w-3.5" />
          Stage contribution
        </div>
        <div className="flex items-center gap-3 font-mono text-[9px] uppercase tracking-wider text-muted">
          {interactive && (
            <span className="flex items-center gap-1 normal-case tracking-normal text-muted">
              <MousePointerClick className="h-3 w-3" />
              click a stage
            </span>
          )}
          <span>{metricLabel}</span>
          <span>·</span>
          <span>Δ points</span>
        </div>
      </div>
      <div className="px-4 py-3">
        {arch.stages.map((stage, index) => (
          <WaterfallRow
            key={stage.id}
            stage={stage}
            previousScore={index === 0 ? stage.score : arch.stages[index - 1].score}
            metricLabel={metricLabel}
            interactive={interactive}
            selected={interactive && stage.id === selectedStageId}
            onSelect={() => onSelectStage?.(stage.id)}
          />
        ))}
        <WaterfallAxis inset={interactive} />
      </div>
    </section>
  );
}

function Hero({
  arch,
  metricLabel,
}: {
  arch: LadderArchitecture;
  metricLabel: string;
}) {
  const mover = biggestMover(arch);
  const Trend =
    mover && mover.deltaFromPrevious < 0 ? TrendingDown : TrendingUp;
  return (
    <section className="grid grid-cols-1 gap-3 md:grid-cols-[200px_1fr]">
      <div className="rounded-md border border-border bg-surface p-4">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
          {metricLabel}
        </div>
        <div className="mt-1 font-mono text-4xl font-semibold leading-none text-foreground">
          {fmtScore(arch.finalScore)}
        </div>
        <div className="mt-2 flex items-center gap-2">
          <DecisionBadge decision={arch.decision} />
          <span className="font-mono text-[9px] text-muted">{arch.model}</span>
        </div>
      </div>
      <div className="rounded-md border border-border bg-surface p-4">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
          Biggest contributor
        </div>
        {mover ? (
          <div className="mt-1 flex items-baseline gap-3">
            <Trend
              className={`h-5 w-5 shrink-0 self-center ${ptsTone(mover.deltaFromPrevious)}`}
            />
            <span className="text-[18px] font-semibold text-foreground">
              {mover.label}
            </span>
            <span
              className={`font-mono text-[18px] font-semibold ${ptsTone(mover.deltaFromPrevious)}`}
            >
              {fmtPts(mover.deltaFromPrevious)}
            </span>
            <StageChip stage={mover} />
          </div>
        ) : (
          <div className="mt-1 text-[13px] text-muted">
            Single-stage pipeline — one pass, no staged build-up.
          </div>
        )}
        {mover?.interpretation && (
          <p className="mt-2 max-w-[64ch] text-[11px] leading-relaxed text-muted">
            {mover.interpretation}
          </p>
        )}
      </div>
    </section>
  );
}

/** Compact selector strip: each architecture as a mini final-score bar. */
function CompareStrip({
  ladder,
  selectedId,
  onSelect,
}: {
  ladder: ComponentLadder;
  selectedId: string;
  onSelect: (id: string) => void;
}) {
  const domain = useMemo(
    () => ladderDomain(ladder.architectures.flatMap((a) => a.stages)),
    [ladder.architectures]
  );
  const range = domain.max - domain.min || 1;
  return (
    <details className="group rounded-md border border-border bg-surface" open>
      <summary className="cursor-pointer list-none px-4 py-3 text-[11px] font-semibold uppercase tracking-wider text-muted">
        Compare architectures ({ladder.architectures.length})
      </summary>
      <div className="space-y-1 px-4 pb-3">
        {ladder.architectures.map((arch) => {
          const active = arch.id === selectedId;
          const width = ((arch.finalScore - domain.min) / range) * 100;
          return (
            <button
              key={arch.id}
              onClick={() => onSelect(arch.id)}
              className={`flex w-full items-center gap-3 rounded px-2 py-1.5 text-left transition-colors ${
                active ? "bg-deterministic/8" : "hover:bg-surface-raised/70"
              }`}
            >
              <span
                className={`w-44 shrink-0 truncate text-[11px] ${
                  active ? "font-semibold text-foreground" : "text-muted"
                }`}
              >
                {arch.label}
              </span>
              <span className="relative h-2.5 flex-1 rounded-sm bg-surface-raised/60">
                <span
                  className={`absolute left-0 top-0 h-full rounded-sm ${
                    active ? "bg-deterministic" : "bg-muted/50"
                  }`}
                  style={{ width: `${Math.max(width, 2)}%` }}
                />
              </span>
              <span className="w-10 shrink-0 text-right font-mono text-[11px] font-semibold text-foreground">
                {fmtScore(arch.finalScore)}
              </span>
            </button>
          );
        })}
      </div>
    </details>
  );
}

function StageDetail({
  arch,
  ladder,
}: {
  arch: LadderArchitecture;
  ladder: ComponentLadder;
}) {
  const stages = arch.stages.filter((s) => !s.isBaseline);
  return (
    <details className="group rounded-md border border-border bg-surface">
      <summary className="cursor-pointer list-none px-4 py-3 text-[11px] font-semibold uppercase tracking-wider text-muted">
        Stage detail &amp; per-category breakdown
      </summary>
      <div className="overflow-x-auto px-2 pb-3">
        <table className="w-full border-collapse text-[11px]">
          <thead>
            <tr className="border-b border-border text-[9px] uppercase tracking-wider text-muted">
              <th className="px-2 py-2 text-left font-semibold">Stage</th>
              <th className="px-2 py-2 text-right font-semibold">Score</th>
              <th className="px-2 py-2 text-right font-semibold">Δ</th>
              <th className="px-2 py-2 text-right font-semibold">P / R</th>
              {ladder.categories.map((cat) => (
                <th key={cat.id} className="px-2 py-2 text-right font-semibold">
                  {cat.shortLabel}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {stages.map((stage) => (
              <tr key={stage.id} className="border-b border-border/50 last:border-b-0">
                <td className="px-2 py-2">
                  <div className="flex items-center gap-2">
                    <StageChip stage={stage} />
                    <span className="text-[11px] text-foreground">{stage.label}</span>
                  </div>
                </td>
                <td className="px-2 py-2 text-right font-mono text-foreground">
                  {fmtScore(stage.score)}
                </td>
                <td
                  className={`px-2 py-2 text-right font-mono font-semibold ${ptsTone(stage.deltaFromPrevious)}`}
                >
                  {fmtPts(stage.deltaFromPrevious)}
                </td>
                <td className="px-2 py-2 text-right font-mono text-muted">
                  {fmtScore(stage.precision)} / {fmtScore(stage.recall)}
                </td>
                {ladder.categories.map((cat) => {
                  const delta = stage.categoryDeltas[cat.id];
                  return (
                    <td
                      key={cat.id}
                      className={`px-2 py-2 text-right font-mono ${
                        typeof delta === "number" ? ptsTone(delta) : "text-muted"
                      }`}
                    >
                      {fmtPts(delta)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  );
}

// ── Per-letter transition sidebar (illustrative worked example) ──────────────

const MAX_LIST = 6;

type DiffKind = "added" | "dropped" | "changed" | "emitted";

/** Static accent strings per diff kind — kept literal so Tailwind keeps them. */
const DIFF_ACCENT: Record<
  DiffKind,
  { border: string; bg: string; text: string; Icon: typeof Plus; label: string }
> = {
  added: { border: "border-success/60", bg: "bg-success/5", text: "text-success", Icon: Plus, label: "Added" },
  dropped: { border: "border-error/60", bg: "bg-error/5", text: "text-error", Icon: Minus, label: "Dropped" },
  changed: { border: "border-llm/60", bg: "bg-llm/5", text: "text-llm", Icon: Pencil, label: "Changed" },
  emitted: { border: "border-border", bg: "bg-surface-raised/30", text: "text-muted", Icon: Plus, label: "Emitted" },
};

function attrSummary(attributes: Record<string, string>): string {
  return Object.entries(attributes)
    .filter(([, value]) => value && value !== "")
    .map(([key, value]) => `${key} ${value}`)
    .join(" · ");
}

/** Field names that differ between a mention's before/after (concept + attributes). */
function changedFields(
  before: Exectv2TransitionMention,
  after: Exectv2TransitionMention
): string[] {
  const attrKeys = Array.from(
    new Set([...Object.keys(before.attributes), ...Object.keys(after.attributes)])
  ).filter((key) => (before.attributes[key] ?? "") !== (after.attributes[key] ?? ""));
  return [...(before.concept !== after.concept ? ["concept"] : []), ...attrKeys];
}

function EntityTag({ entity }: { entity: string }) {
  return (
    <span className="shrink-0 rounded bg-surface-raised px-1 py-0.5 font-mono text-[8px] uppercase tracking-wide text-muted">
      {entity}
    </span>
  );
}

/** Compact-by-default add/drop/emit row. Concept always shows on its own line;
 *  attributes + evidence only when `detailed`. */
function MentionLine({
  mention,
  kind,
  detailed,
}: {
  mention: Exectv2TransitionMention;
  kind: DiffKind;
  detailed: boolean;
}) {
  const accent = DIFF_ACCENT[kind];
  const attrs = attrSummary(mention.attributes);
  return (
    <div className={`rounded-r border-l-2 ${accent.border} ${accent.bg} px-2 py-1.5`}>
      <div className="flex items-baseline gap-1.5">
        <EntityTag entity={mention.entity} />
        <span className={`text-[11px] font-medium ${kind === "dropped" ? "text-muted line-through" : "text-foreground"}`}>
          {mention.text || "—"}
        </span>
      </div>
      {mention.concept && (
        <p className="mt-0.5 truncate font-mono text-[9px] text-muted" title={mention.concept}>
          {mention.concept}
        </p>
      )}
      {detailed && attrs && <p className="mt-0.5 font-mono text-[9px] text-muted">{attrs}</p>}
      {detailed && mention.evidence && (
        <p className="mt-0.5 line-clamp-2 text-[9px] italic leading-snug text-muted/80">“{mention.evidence}”</p>
      )}
    </div>
  );
}

/** Compact-by-default changed row: a one-line "which fields changed" summary,
 *  expanding to full before→after values when `detailed`. */
function ChangedLine({
  change,
  detailed,
}: {
  change: Exectv2TransitionChange;
  detailed: boolean;
}) {
  const { before, after } = change;
  const conceptChanged = before.concept !== after.concept;
  const fields = changedFields(before, after);
  const attrKeys = fields.filter((field) => field !== "concept");
  const accent = DIFF_ACCENT.changed;
  return (
    <div className={`rounded-r border-l-2 ${accent.border} ${accent.bg} px-2 py-1.5`}>
      <div className="flex items-baseline gap-1.5">
        <EntityTag entity={after.entity} />
        <span className="text-[11px] font-medium text-foreground">{after.text || "—"}</span>
      </div>
      {!detailed ? (
        fields.length > 0 && (
          <p className="mt-0.5 font-mono text-[9px] text-muted">
            <span className="text-llm">changed</span> {fields.join(" · ")}
          </p>
        )
      ) : (
        <>
          {conceptChanged && (
            <div className="mt-1 flex items-center gap-1.5 font-mono text-[9px]">
              <span className="text-muted line-through">{before.concept || "∅"}</span>
              <ArrowRight className="h-2.5 w-2.5 text-llm" />
              <span className="text-foreground">{after.concept || "∅"}</span>
            </div>
          )}
          {attrKeys.map((key) => (
            <div key={key} className="mt-0.5 flex items-center gap-1.5 font-mono text-[9px]">
              <span className="text-muted">{key}</span>
              <span className="text-muted line-through">{before.attributes[key] ?? "∅"}</span>
              <ArrowRight className="h-2.5 w-2.5 text-llm" />
              <span className="text-foreground">{after.attributes[key] ?? "∅"}</span>
            </div>
          ))}
        </>
      )}
    </div>
  );
}

function DetailToggle({
  detailed,
  onToggle,
}: {
  detailed: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-pressed={detailed}
      className="flex shrink-0 items-center gap-1 rounded border border-border px-1.5 py-0.5 text-[9px] uppercase tracking-wider text-muted transition-colors hover:bg-surface-raised/70"
    >
      {detailed ? <Eye className="h-3 w-3" /> : <EyeOff className="h-3 w-3" />}
      {detailed ? "Less" : "Detail"}
    </button>
  );
}

function DiffSection({
  kind,
  count,
  children,
}: {
  kind: DiffKind;
  count: number;
  children: ReactNode;
}) {
  if (count === 0) return null;
  const accent = DIFF_ACCENT[kind];
  return (
    <div>
      <div className={`mb-1 flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wider ${accent.text}`}>
        <accent.Icon className="h-3 w-3" />
        {accent.label}
        <span className="font-mono">{count}</span>
      </div>
      <div className="space-y-1">{children}</div>
    </div>
  );
}

function TransitionSidebar({
  archTransitions,
  ladderStages,
  exampleIndex,
  onSelectExample,
  selectedStageId,
}: {
  archTransitions: Exectv2TransitionArchitecture;
  ladderStages: LadderStage[];
  exampleIndex: number;
  onSelectExample: (index: number) => void;
  selectedStageId: string;
}) {
  const [detailed, setDetailed] = useState(false);
  const example: Exectv2TransitionExample | undefined =
    archTransitions.examples[exampleIndex] ?? archTransitions.examples[0];
  const stage: Exectv2TransitionStage | undefined = example?.stages.find(
    (s) => s.stage_id === selectedStageId
  );
  const ladderStage = ladderStages.find((s) => s.id === selectedStageId);

  return (
    <aside className="flex flex-col overflow-hidden rounded-md border border-border bg-surface">
      <div className="border-b border-border px-4 py-3">
        <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-wider text-muted">
          <MousePointerClick className="h-3.5 w-3.5" />
          Worked example
        </div>
        <p className="mt-1 text-[10px] text-muted">
          What this stage does to one real letter — illustrative, not a scoring surface.
        </p>
      </div>

      {/* letter selector */}
      <div className="flex flex-wrap items-center gap-1.5 border-b border-border px-4 py-2.5">
        <span className="mr-1 text-[9px] uppercase tracking-wider text-muted">Letter</span>
        {archTransitions.examples.map((ex, index) => (
          <button
            key={ex.letter_id}
            type="button"
            onClick={() => onSelectExample(index)}
            className={`rounded border px-1.5 py-0.5 font-mono text-[10px] transition-colors ${
              index === exampleIndex
                ? "border-deterministic/40 bg-deterministic/10 text-deterministic"
                : "border-border text-muted hover:bg-surface-raised/70"
            }`}
          >
            {ex.letter_id}
          </button>
        ))}
        {example && (
          <span className="ml-auto font-mono text-[9px] text-muted">
            gold {example.gold_count} · final {example.final_count ?? "—"}
          </span>
        )}
      </div>

      {/* selected stage transition */}
      <div className="flex-1 px-4 py-3">
        {!stage || !ladderStage ? (
          <p className="text-[11px] text-muted">Select a stage to see its effect.</p>
        ) : (
          <>
            <div className="flex items-center gap-2">
              <StageChip stage={ladderStage} />
              <span className="text-[12px] font-semibold text-foreground">{stage.label}</span>
            </div>
            <p className="mt-1 text-[10px] leading-relaxed text-muted">{stage.interpretation}</p>

            {!stage.has_transition ? (
              <p className="mt-3 rounded border border-dashed border-border px-2 py-2 text-[10px] text-muted">
                {stage.note ?? "No per-mention surface at this stage."}
              </p>
            ) : stage.is_baseline ? (
              <div className="mt-3 space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <div className="text-[10px] text-muted">
                    <span className="font-mono font-semibold text-foreground">{stage.mention_count}</span>{" "}
                    candidate mentions emitted by the producer lanes — the floor everything else builds on.
                  </div>
                  <DetailToggle detailed={detailed} onToggle={() => setDetailed((d) => !d)} />
                </div>
                <div className="space-y-1">
                  {stage.added.slice(0, MAX_LIST).map((mention, i) => (
                    <MentionLine key={`${mention.entity}:${mention.text}:${i}`} mention={mention} kind="emitted" detailed={detailed} />
                  ))}
                  {stage.added.length > MAX_LIST && (
                    <p className="text-[9px] text-muted">+{stage.added.length - MAX_LIST} more candidates</p>
                  )}
                </div>
              </div>
            ) : (
              <div className="mt-3 space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-[10px]">
                    <span className="text-success">+{stage.added.length} added</span>
                    <span className="text-error">−{stage.dropped.length} dropped</span>
                    <span className="text-llm">~{stage.changed.length} changed</span>
                    <span className="text-muted">={stage.kept} kept</span>
                  </div>
                  <DetailToggle detailed={detailed} onToggle={() => setDetailed((d) => !d)} />
                </div>
                {stage.added.length === 0 &&
                stage.dropped.length === 0 &&
                stage.changed.length === 0 ? (
                  <p className="rounded border border-dashed border-border px-2 py-2 text-[10px] text-muted">
                    No change for this letter — every mention passed straight through this stage.
                  </p>
                ) : (
                  <>
                    <DiffSection kind="changed" count={stage.changed.length}>
                      {stage.changed.slice(0, MAX_LIST).map((change, i) => (
                        <ChangedLine key={`${change.after.entity}:${change.after.text}:${i}`} change={change} detailed={detailed} />
                      ))}
                    </DiffSection>
                    <DiffSection kind="added" count={stage.added.length}>
                      {stage.added.slice(0, MAX_LIST).map((mention, i) => (
                        <MentionLine key={`${mention.entity}:${mention.text}:${i}`} mention={mention} kind="added" detailed={detailed} />
                      ))}
                    </DiffSection>
                    <DiffSection kind="dropped" count={stage.dropped.length}>
                      {stage.dropped.slice(0, MAX_LIST).map((mention, i) => (
                        <MentionLine key={`${mention.entity}:${mention.text}:${i}`} mention={mention} kind="dropped" detailed={detailed} />
                      ))}
                    </DiffSection>
                  </>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </aside>
  );
}

export interface ComponentLadderSurfaceProps {
  ladder: ComponentLadder;
  dataset: DatasetDescriptor;
  description: string;
  selectedArchitectureId?: string;
  onSelectArchitecture: (id: string) => void;
  /** Extra header actions (cross-surface links, live-run controls). */
  headerRight?: ReactNode;
  /** Optional banner above the ladder (e.g. a preview/mock disclaimer). */
  banner?: ReactNode;
  /**
   * Optional illustrative per-letter transition examples. When present, the
   * stage rows become clickable and a worked-example sidebar shows what the
   * selected stage does to one real letter. Explanatory only — not a scoring
   * surface. Datasets without examples (e.g. Gan) simply omit this.
   */
  transitions?: Exectv2ComponentTransitionsResponse;
}

export default function ComponentLadderSurface({
  ladder,
  dataset,
  description,
  selectedArchitectureId,
  onSelectArchitecture,
  headerRight,
  banner,
  transitions,
}: ComponentLadderSurfaceProps) {
  const selected = useMemo(
    () =>
      ladder.architectures.find((a) => a.id === selectedArchitectureId) ??
      ladder.architectures[0],
    [ladder.architectures, selectedArchitectureId]
  );

  const archTransitions = useMemo(
    () => transitions?.architectures.find((a) => a.run_id === selected?.id),
    [transitions, selected?.id]
  );
  const hasTransitions = Boolean(archTransitions && archTransitions.examples.length > 0);

  // Default the inspected stage to the biggest mover (most score-relevant), else
  // the first non-baseline stage.
  const defaultStageId = useMemo(() => {
    if (!selected) return undefined;
    const mover = biggestMover(selected);
    const firstReal = selected.stages.find((s) => !s.isBaseline);
    return (mover ?? firstReal ?? selected.stages[0])?.id;
  }, [selected]);

  const [selectedStageId, setSelectedStageId] = useState<string | undefined>(defaultStageId);
  const [exampleIndex, setExampleIndex] = useState(0);

  // Reset the inspected stage + example letter when the architecture changes,
  // using the "adjust state during render" pattern (no effect needed).
  const [prevArchId, setPrevArchId] = useState(selected?.id);
  if (selected?.id !== prevArchId) {
    setPrevArchId(selected?.id);
    setSelectedStageId(defaultStageId);
    setExampleIndex(0);
  }

  const activeStageId = selectedStageId ?? defaultStageId;

  const header = (
    <SurfaceHeader
      surface="laboratory"
      dataset={dataset}
      description={description}
      right={
        <>
          {ladder.architectures.length > 1 && selected && (
            <select
              value={selected.id}
              onChange={(event) => onSelectArchitecture(event.target.value)}
              className="rounded-md border border-border bg-surface px-2 py-1 text-[11px] text-foreground focus:outline-none"
            >
              {ladder.architectures.map((arch) => (
                <option key={arch.id} value={arch.id}>
                  {arch.label} ({arch.decision})
                </option>
              ))}
            </select>
          )}
          {headerRight}
        </>
      }
    />
  );

  return (
    <SurfaceLayout variant="report" maxWidth={1200} contentClassName="space-y-4" header={header}>
      {banner}
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[10px] text-muted">
        <span className="font-semibold uppercase tracking-wider">{ladder.method}</span>
        <span>·</span>
        <span className="font-mono">{ladder.methodNote}</span>
      </div>

      {selected && <Hero arch={selected} metricLabel={ladder.metricLabel} />}
      {selected &&
        (hasTransitions && archTransitions && activeStageId ? (
          <div className="grid grid-cols-1 gap-3 lg:grid-cols-[1fr_minmax(320px,380px)] lg:items-start">
            <Waterfall
              arch={selected}
              metricLabel={ladder.metricLabel}
              interactive
              selectedStageId={activeStageId}
              onSelectStage={setSelectedStageId}
            />
            <TransitionSidebar
              archTransitions={archTransitions}
              ladderStages={selected.stages}
              exampleIndex={exampleIndex}
              onSelectExample={setExampleIndex}
              selectedStageId={activeStageId}
            />
          </div>
        ) : (
          <Waterfall arch={selected} metricLabel={ladder.metricLabel} />
        ))}
      {ladder.architectures.length > 1 && selected && (
        <CompareStrip
          ladder={ladder}
          selectedId={selected.id}
          onSelect={onSelectArchitecture}
        />
      )}
      {selected && <StageDetail arch={selected} ladder={ladder} />}
    </SurfaceLayout>
  );
}
