"use client";

import { useMemo, type ReactNode } from "react";
import { Layers3, TrendingUp, TrendingDown } from "lucide-react";
import type { DatasetDescriptor, DatasetTone } from "@/lib/datasets";
import { TONE_CLASSES } from "@/lib/datasets";
import {
  biggestMover,
  ladderDomain,
  type ComponentLadder,
  type LadderArchitecture,
  type LadderStage,
} from "@/lib/componentLadder";
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
}: {
  stage: LadderStage;
  previousScore: number;
  metricLabel: string;
}) {
  const pct = (value: number) => value * 100;

  const carriedTo = stage.isBaseline ? 0 : Math.min(previousScore, stage.score);
  const lo = stage.isBaseline ? 0 : Math.min(previousScore, stage.score);
  const hi = stage.isBaseline ? stage.score : Math.max(previousScore, stage.score);
  const regressed = !stage.isBaseline && stage.score < previousScore;
  const tone: DatasetTone = regressed ? "error" : stage.tone;

  return (
    <div className="flex items-center gap-3 py-1">
      <div className="flex w-52 shrink-0 items-center gap-2">
        <span className="truncate text-[11px] font-medium text-foreground" title={stage.label}>
          {stage.label}
        </span>
      </div>
      <div className="flex w-20 shrink-0 justify-start">
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
    </div>
  );
}

/** The 0–100 tick labels, aligned under the bar track. */
function WaterfallAxis() {
  return (
    <div className="flex items-center gap-3 pt-1.5">
      <div className="w-52 shrink-0" />
      <div className="w-20 shrink-0" />
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
}: {
  arch: LadderArchitecture;
  metricLabel: string;
}) {
  return (
    <section className="overflow-hidden rounded-md border border-border bg-surface">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-wider text-muted">
          <Layers3 className="h-3.5 w-3.5" />
          Stage contribution
        </div>
        <div className="flex items-center gap-3 font-mono text-[9px] uppercase tracking-wider text-muted">
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
          />
        ))}
        <WaterfallAxis />
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
}

export default function ComponentLadderSurface({
  ladder,
  dataset,
  description,
  selectedArchitectureId,
  onSelectArchitecture,
  headerRight,
  banner,
}: ComponentLadderSurfaceProps) {
  const selected = useMemo(
    () =>
      ladder.architectures.find((a) => a.id === selectedArchitectureId) ??
      ladder.architectures[0],
    [ladder.architectures, selectedArchitectureId]
  );

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
      {selected && <Waterfall arch={selected} metricLabel={ladder.metricLabel} />}
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
