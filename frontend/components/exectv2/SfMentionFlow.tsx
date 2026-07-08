"use client";

import { useState, type ElementType } from "react";
import { AlertOctagon, AlertTriangle, CheckCircle2, Filter, Hash, Quote, Tag } from "lucide-react";
import type { SfMentionRow } from "@/lib/types";
import { buildMentionFlows, type MentionFlow } from "@/lib/sfFamilies";
import { STATUS_META } from "@/lib/sfPresentation";

/**
 * Compact mention pipeline. Matched + filtered rows stay collapsed.
 * Linked pairs show only diverge-highlighting fields; single-sided rows
 * are phrase + verdict — no ghost essays, no scorer keys by default.
 */

type StageField = "phrase" | "counts" | "freqchg" | "state";

interface Stage {
  field: StageField;
  label: string;
  value: string;
}

const STAGE_ICON: Record<StageField, ElementType> = {
  phrase: Quote,
  counts: Hash,
  freqchg: Tag,
  state: Filter,
};

const FIELD_ORDER: StageField[] = ["phrase", "counts", "freqchg", "state"];

function computeStages(row: SfMentionRow): Stage[] {
  const stages: Stage[] = [{ field: "phrase", label: "phrase", value: row.phrase }];
  if (row.counts && row.counts !== "(no counts)") stages.push({ field: "counts", label: "count", value: row.counts });
  if (row.frequency_change) stages.push({ field: "freqchg", label: "FreqChg", value: row.frequency_change });
  if (row.projected_state) stages.push({ field: "state", label: "state", value: row.projected_state });
  return stages;
}

interface AlignedStage {
  field: StageField;
  label: string;
  goldValue: string | null;
  predValue: string | null;
  diverge: boolean;
}

function alignStages(goldStages: Stage[], predStages: Stage[]): AlignedStage[] {
  const goldByField = new Map(goldStages.map((s) => [s.field, s]));
  const predByField = new Map(predStages.map((s) => [s.field, s]));
  const fields = FIELD_ORDER.filter((f) => goldByField.has(f) || predByField.has(f));
  return fields.map((field) => {
    const g = goldByField.get(field);
    const p = predByField.get(field);
    return {
      field,
      label: g?.label ?? p?.label ?? field,
      goldValue: g?.value ?? null,
      predValue: p?.value ?? null,
      diverge: (!!g && !!p && g.value !== p.value) || !g !== !p,
    };
  });
}

export function MentionFlowList({ rows }: { rows: SfMentionRow[] }) {
  const [showQuiet, setShowQuiet] = useState(false);
  const flows = buildMentionFlows(rows);
  if (flows.length === 0) {
    return <p className="text-[10px] text-muted">no mentions</p>;
  }

  const noisy = flows.filter((f) => f.kind === "linked" || f.kind === "miss" || f.kind === "extra");
  const quiet = flows.filter((f) => f.kind === "matched" || f.kind === "skip");
  const visible = showQuiet ? flows : noisy.length > 0 ? noisy : flows;

  return (
    <div className="flex flex-col gap-1.5">
      {visible.map((flow, i) => (
        <MentionFlowCard key={i} flow={flow} />
      ))}
      {noisy.length > 0 && quiet.length > 0 && (
        <button
          type="button"
          onClick={() => setShowQuiet((v) => !v)}
          className="self-start text-[9px] font-semibold text-muted hover:text-foreground"
        >
          {showQuiet ? "hide matched / filtered" : `+${quiet.length} matched / filtered`}
        </button>
      )}
    </div>
  );
}

function MentionFlowCard({ flow }: { flow: MentionFlow }) {
  if (flow.kind === "matched" && flow.gold) {
    return (
      <div className="flex items-center gap-2 border-l-2 border-success/60 bg-success/5 px-2 py-0.5 text-[10.5px]">
        <CheckCircle2 className="h-3 w-3 shrink-0 text-success" />
        <span className="font-mono text-foreground">{flow.gold.phrase}</span>
        <span className="ml-auto text-[9px] text-success">tp</span>
      </div>
    );
  }

  if (flow.kind === "skip") {
    const row = flow.gold ?? flow.pred;
    if (!row) return null;
    return (
      <div className="flex items-center gap-2 px-2 py-0.5 text-[10px] text-muted opacity-50">
        <span className="font-mono italic">{row.phrase}</span>
        <span className="ml-auto">filtered</span>
      </div>
    );
  }

  if (flow.kind === "linked" && flow.gold && flow.pred) {
    const aligned = alignStages(computeStages(flow.gold), computeStages(flow.pred));
    // Always keep phrase; drop fields that agree so the split stays loud.
    const cols = aligned.filter((a) => a.field === "phrase" || a.diverge);
    return (
      <div className="border border-error/25 bg-surface">
        <div className="flex items-center justify-between border-b border-border px-2 py-1">
          <span className="text-[9px] font-bold uppercase tracking-wide text-error">linked miss</span>
          <span className="font-mono text-[9px] text-muted">
            {STATUS_META[flow.gold.status].label}/{STATUS_META[flow.pred.status].label}
          </span>
        </div>
        <PipelineRow side="gold" cols={cols} pickValue={(a) => a.goldValue} status={flow.gold.status} />
        <PipelineRow side="pred" cols={cols} pickValue={(a) => a.predValue} status={flow.pred.status} />
      </div>
    );
  }

  if (flow.kind === "miss" && flow.gold) {
    return <SingleSidedRow row={flow.gold} />;
  }

  if (flow.kind === "extra" && flow.pred) {
    return <SingleSidedRow row={flow.pred} />;
  }

  return null;
}

function SingleSidedRow({ row }: { row: SfMentionRow }) {
  const stages = computeStages(row);
  return (
    <div
      className={`flex items-stretch gap-1 border px-1.5 py-1 ${
        row.status === "fn" || row.status === "fp" ? "border-error/30 bg-error/5" : "border-border bg-surface"
      }`}
    >
      <SideTag side={row.side} />
      {stages.map((s) => (
        <div key={s.field} className="min-w-0 flex-1 px-1.5 py-0.5">
          <div className="text-[8px] font-bold uppercase tracking-wide text-muted">{s.label}</div>
          <div className="truncate font-mono text-[11px] font-semibold text-foreground" title={s.value}>
            {s.value}
          </div>
        </div>
      ))}
      <VerdictNode status={row.status} />
    </div>
  );
}

function PipelineRow({
  side,
  cols,
  pickValue,
  status,
}: {
  side: "gold" | "pred";
  cols: AlignedStage[];
  pickValue: (a: AlignedStage) => string | null;
  status: SfMentionRow["status"];
}) {
  return (
    <div className="flex items-stretch gap-0 border-b border-border last:border-b-0">
      <SideTag side={side} />
      {cols.map((a) => {
        const value = pickValue(a);
        return (
          <div
            key={a.field}
            className={`min-w-0 flex-1 px-2 py-1 ${a.diverge ? "bg-error/10" : ""}`}
          >
            <div className="mb-0.5 flex items-center gap-1 text-[8px] font-bold uppercase tracking-wide text-muted">
              <StageIcon field={a.field} />
              {a.label}
            </div>
            <div
              className={`truncate font-mono text-[11px] font-semibold ${
                a.diverge ? "text-error" : value ? "text-foreground" : "italic text-muted"
              }`}
              title={value ?? undefined}
            >
              {value ?? "—"}
            </div>
          </div>
        );
      })}
      <VerdictNode status={status} />
    </div>
  );
}

function StageIcon({ field }: { field: StageField }) {
  const Icon = STAGE_ICON[field];
  return <Icon className="h-2.5 w-2.5" />;
}

function VerdictNode({ status }: { status: SfMentionRow["status"] }) {
  const meta = STATUS_META[status];
  const Icon = status === "tp" ? CheckCircle2 : status === "fp" ? AlertTriangle : status === "fn" ? AlertOctagon : null;
  return (
    <div
      className={`flex w-11 shrink-0 flex-col items-center justify-center gap-0.5 text-[10px] font-extrabold ${
        status === "tp"
          ? "bg-success/10 text-success"
          : status === "skip"
            ? "bg-surface-raised text-muted"
            : "bg-error/10 text-error"
      }`}
    >
      {Icon && <Icon className="h-3 w-3" />}
      {meta.label}
    </div>
  );
}

function SideTag({ side }: { side: "gold" | "pred" }) {
  return (
    <span
      className={`flex w-6 shrink-0 items-center justify-center font-mono text-[9px] font-bold ${
        side === "gold" ? "bg-gold/15 text-gold" : "bg-llm/15 text-llm"
      }`}
    >
      {side === "gold" ? "G" : "P"}
    </span>
  );
}
