"use client";

import { useState } from "react";
import { AlertOctagon, AlertTriangle, CheckCircle2 } from "lucide-react";
import type { SfMentionRow } from "@/lib/types";
import { buildMentionFlows, type MentionFlow } from "@/lib/sfFamilies";
import {
  formatScorerCounts,
  formatScorerFreqChg,
  formatScorerState,
  STATUS_META,
} from "@/lib/sfPresentation";

/**
 * Per-lens mention outcomes — how the scorer projected each mention into
 * keys and labelled it TP / FP / FN. Shown inside Scorer breakdown.
 */

interface ScorerField {
  label: string;
  value: string;
}

function scorerFields(row: SfMentionRow): ScorerField[] {
  const fields: ScorerField[] = [{ label: "Phrase", value: row.phrase }];
  const counts = formatScorerCounts(row.counts);
  if (counts !== "no count attributes") fields.push({ label: "Count key", value: counts });
  const fc = formatScorerFreqChg(row.frequency_change);
  if (fc) fields.push({ label: "FreqChg", value: fc.replace(/^change: /, "") });
  const state = formatScorerState(row.projected_state);
  if (state) fields.push({ label: "State", value: state.replace(/^projected state: /, "") });
  return fields;
}

function divergingFields(gold: SfMentionRow, pred: SfMentionRow): ScorerField[] {
  const goldFields = scorerFields(gold);
  const predByLabel = new Map(scorerFields(pred).map((f) => [f.label, f.value]));
  return goldFields.filter((f) => {
    const pVal = predByLabel.get(f.label);
    return pVal === undefined || pVal !== f.value;
  });
}

export function MentionFlowList({ rows }: { rows: SfMentionRow[] }) {
  const [showQuiet, setShowQuiet] = useState(false);
  const flows = buildMentionFlows(rows);
  if (flows.length === 0) {
    return <p className="text-[11px] text-muted">No mentions scored in this lens.</p>;
  }

  const noisy = flows.filter((f) => f.kind === "linked" || f.kind === "miss" || f.kind === "extra");
  const quiet = flows.filter((f) => f.kind === "matched" || f.kind === "skip");
  const visible = showQuiet ? flows : noisy.length > 0 ? noisy : flows;

  return (
    <div className="flex flex-col gap-2">
      {visible.map((flow, i) => (
        <MentionFlowCard key={i} flow={flow} />
      ))}
      {noisy.length > 0 && quiet.length > 0 && (
        <button
          type="button"
          onClick={() => setShowQuiet((v) => !v)}
          className="self-start text-[10px] font-semibold text-muted hover:text-foreground"
        >
          {showQuiet ? "Hide matched mentions" : `Show ${quiet.length} matched / filtered`}
        </button>
      )}
    </div>
  );
}

function MentionFlowCard({ flow }: { flow: MentionFlow }) {
  if (flow.kind === "matched" && flow.gold) {
    return (
      <div className="flex items-center gap-2 border-l-[3px] border-l-success/60 px-3 py-2 text-[12px]">
        <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-success" />
        <span className="font-semibold text-foreground">{flow.gold.phrase}</span>
        <span className="ml-auto text-[10px] font-semibold text-success">scorer keys match</span>
      </div>
    );
  }

  if (flow.kind === "skip") {
    const row = flow.gold ?? flow.pred;
    if (!row) return null;
    return (
      <div className="px-3 py-1.5 text-[11px] text-muted opacity-60">
        <span className="font-mono italic">{row.phrase}</span>
        <span className="ml-2">· filtered out by this lens</span>
      </div>
    );
  }

  if (flow.kind === "linked" && flow.gold && flow.pred) {
    const diffFields = divergingFields(flow.gold, flow.pred);
    const phrase = flow.gold.phrase;
    return (
      <div className="overflow-hidden rounded-md border border-error/30 bg-surface">
        <div className="border-b border-error/20 bg-error/5 px-3 py-2">
          <p className="text-[12px] font-semibold text-foreground">{phrase}</p>
          <p className="mt-0.5 text-[11px] text-muted">
            Phrase matches, but this lens builds different scorer keys → counts as{" "}
            <span className="font-semibold text-error">FN</span> (gold) +{" "}
            <span className="font-semibold text-error">FP</span> (pred)
          </p>
        </div>
        <ComparisonTable gold={flow.gold} pred={flow.pred} highlightLabels={new Set(diffFields.map((f) => f.label))} />
        <ScorerKeyDetails gold={flow.gold} pred={flow.pred} />
      </div>
    );
  }

  if (flow.kind === "miss" && flow.gold) {
    return (
      <SingleMentionCard
        row={flow.gold}
        title="Gold mention — scorer missed (FN)"
        subtitle="Prediction has no matching key in this lens."
      />
    );
  }

  if (flow.kind === "extra" && flow.pred) {
    return (
      <SingleMentionCard
        row={flow.pred}
        title="Extra prediction — no gold match (FP)"
        subtitle="Scorer counted a key with no gold counterpart."
      />
    );
  }

  return null;
}

function ComparisonTable({
  gold,
  pred,
  highlightLabels,
}: {
  gold: SfMentionRow;
  pred: SfMentionRow;
  highlightLabels: Set<string>;
}) {
  const labels = ["Phrase", "Count key", "FreqChg", "State"].filter((label) => {
    const gVal = fieldValue(gold, label);
    const pVal = fieldValue(pred, label);
    return gVal !== null || pVal !== null;
  });

  if (labels.length === 0) return null;

  return (
    <table className="w-full border-collapse text-[11px]">
      <thead>
        <tr className="border-b border-border bg-surface-raised">
          <th className="px-3 py-1.5 text-left font-semibold text-muted" />
          <th className="px-3 py-1.5 text-left font-semibold text-gold">Gold</th>
          <th className="px-3 py-1.5 text-left font-semibold text-llm">Pred</th>
        </tr>
      </thead>
      <tbody>
        {labels.map((label) => {
          const diverge = highlightLabels.has(label);
          return (
            <tr key={label} className={`border-b border-border last:border-b-0 ${diverge ? "bg-error/8" : ""}`}>
              <td className="px-3 py-2 font-semibold text-muted">{label}</td>
              <td className={`px-3 py-2 font-mono ${diverge ? "font-semibold text-error" : "text-foreground"}`}>
                {fieldValue(gold, label) ?? "—"}
              </td>
              <td className={`px-3 py-2 font-mono ${diverge ? "font-semibold text-error" : "text-foreground"}`}>
                {fieldValue(pred, label) ?? "—"}
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

function fieldValue(row: SfMentionRow, label: string): string | null {
  if (label === "Phrase") return row.phrase;
  if (label === "Count key") {
    const v = formatScorerCounts(row.counts);
    return v === "no count attributes" ? null : v;
  }
  if (label === "FreqChg") return row.frequency_change.trim() || null;
  if (label === "State") return row.projected_state.trim() || null;
  return null;
}

function ScorerKeyDetails({ gold, pred }: { gold: SfMentionRow; pred: SfMentionRow }) {
  const [open, setOpen] = useState(false);
  if (!gold.key && !pred.key) return null;
  return (
    <div className="border-t border-border px-3 py-1.5">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="text-[10px] font-semibold text-muted hover:text-foreground"
      >
        {open ? "Hide raw scorer keys" : "Show raw scorer keys"}
      </button>
      {open && (
        <dl className="mt-1.5 space-y-1 font-mono text-[10px] text-muted">
          {gold.key && (
            <div>
              <dt className="inline text-gold">Gold key </dt>
              <dd className="inline break-all text-foreground">{gold.key}</dd>
            </div>
          )}
          {pred.key && (
            <div>
              <dt className="inline text-llm">Pred key </dt>
              <dd className="inline break-all text-foreground">{pred.key}</dd>
            </div>
          )}
        </dl>
      )}
    </div>
  );
}

function SingleMentionCard({
  row,
  title,
  subtitle,
}: {
  row: SfMentionRow;
  title: string;
  subtitle: string;
}) {
  const fields = scorerFields(row);
  const Icon = row.status === "fn" ? AlertOctagon : AlertTriangle;
  return (
    <div className="overflow-hidden rounded-md border border-error/30 bg-surface">
      <div className="flex items-start gap-2 border-b border-error/20 bg-error/5 px-3 py-2">
        <Icon className="mt-0.5 h-3.5 w-3.5 shrink-0 text-error" />
        <div>
          <p className="text-[12px] font-semibold text-foreground">{title}</p>
          <p className="text-[11px] text-muted">{subtitle}</p>
        </div>
        <span className={`ml-auto shrink-0 text-[10px] font-bold ${STATUS_META[row.status].tone}`}>
          {STATUS_META[row.status].label}
        </span>
      </div>
      <dl className="divide-y divide-border">
        {fields.map((f) => (
          <div key={f.label} className="grid grid-cols-[7rem_1fr] gap-2 px-3 py-2 text-[11px]">
            <dt className="font-semibold text-muted">{f.label}</dt>
            <dd className="font-mono font-semibold text-foreground">{f.value}</dd>
          </div>
        ))}
      </dl>
      {row.key && (
        <div className="border-t border-border px-3 py-1.5 font-mono text-[10px] text-muted">
          Scorer key: <span className="break-all text-foreground">{row.key}</span>
        </div>
      )}
    </div>
  );
}
