"use client";

import { useState, type ReactNode } from "react";
import {
  ArrowRight,
  Plus,
  Minus,
  Pencil,
  MousePointerClick,
  Eye,
  EyeOff,
} from "lucide-react";
import type { LadderStage } from "@/lib/componentLadder";
import type {
  Exectv2TransitionArchitecture,
  Exectv2TransitionChange,
  Exectv2TransitionExample,
  Exectv2TransitionMention,
  Exectv2TransitionStage,
} from "@/lib/types";
import { StageChip } from "@/components/laboratory/ComponentLadderSurface";

// ── Per-letter transition sidebar (illustrative worked example) ──────────────
//
// ExECTv2's prediction is a *set* of mentions, so its worked example is a
// mention-level diff: at the producer floor everything is freshly emitted, and
// each later stage adds / drops / changes individual mentions. (Gan's prediction
// is a single label, so it gets a separate label-trajectory sidebar.)

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

export default function Exectv2TransitionSidebar({
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
