"use client";

import { useMemo } from "react";
import type {
  GoldNoiseFamilySummary,
  GoldNoiseGanAuditResponse,
  GoldNoiseHypothesesResponse,
  GoldNoiseIssuesResponse,
  GoldNoiseItem,
} from "@/lib/types";

// ── Verdict / mechanism presentation ──────────────────────────────────
//
// The "ceiling" = verdict == gold_right = the genuine-model-error rate (how
// often the model truly failed). Its complement (model_defensible +
// both_defensible) is the gold-contested share — the actual "gold noise" this
// tab is about. Both are surfaced with honest numerators.

export const VERDICT_META: Record<
  string,
  { label: string; tone: string; bar: string }
> = {
  gold_right: {
    label: "Genuine model error",
    tone: "border-error/30 text-error bg-error/10",
    bar: "bg-error",
  },
  model_defensible: {
    label: "Model defensible (gold contestable)",
    tone: "border-deterministic/30 text-deterministic bg-deterministic/10",
    bar: "bg-deterministic",
  },
  both_defensible: {
    label: "Both defensible",
    tone: "border-llm/30 text-llm bg-llm/10",
    bar: "bg-llm",
  },
  unadjudicated: {
    label: "Unadjudicated",
    tone: "border-border text-muted bg-surface-raised",
    bar: "bg-muted",
  },
};

export const MECHANISM_LABELS: Record<string, string> = {
  genuine_model_error: "Genuine model error",
  gold_multiplicity_consolidation: "Gold multiplicity",
  gold_orthographic_typo: "Gold orthographic typo",
  gold_under_annotation: "Gold under-annotation",
  scorer_mechanics_artifact: "Scorer mechanics artifact",
  iaa_ambiguity: "IAA ambiguity",
  unadjudicated: "Unadjudicated",
};

export const VERDICT_ORDER = [
  "gold_right",
  "model_defensible",
  "both_defensible",
  "unadjudicated",
];

// Cross-project corroboration strip: the same gold-noise finding, measured in
// three independent codebases. Static (cited from predecessor-lessons docs).
export const CORROBORATION = [
  { source: "dissertation-recursive", value: "29.2% oracle failure", note: "Gan gold" },
  { source: "dspy_extraction", value: "13.13% G1 mismatches", note: "+ multiple sentinel" },
  { source: "this repo", value: "29.7% SF ceiling", note: "ExECT gold" },
];

// ── helpers ──

export function pct(n: number, total: number): string {
  if (!total) return "—";
  return `${((n / total) * 100).toFixed(1)}%`;
}

export function mentionText(mention: Record<string, unknown> | null): string {
  if (!mention) return "";
  return String(mention.normalized_text ?? mention.raw_text ?? "");
}

/**
 * Locate the gold + pred mention spans inside the source letter for
 * highlighting. Mirrors GoldAuditPanel's findHighlightSpans: exact, then
 * case-insensitive.
 */
export function findMentionSpans(
  letterText: string,
  item: GoldNoiseItem
): { start: number; end: number; kind: string; label: string }[] {
  const spans: { start: number; end: number; kind: string; label: string }[] = [];
  const lower = letterText.toLowerCase();
  for (const [kind, mention, label] of [
    ["gold", item.gold, "Gold mention"],
    ["repair", item.pred, "Pred mention"],
  ] as const) {
    const text = mentionText(mention);
    if (!text || text.length < 4) continue;
    let idx = letterText.indexOf(text);
    if (idx < 0) idx = lower.indexOf(text.toLowerCase());
    if (idx >= 0) spans.push({ start: idx, end: idx + text.length, kind, label });
  }
  return spans;
}

// ── Summary header tiles ──

export function CeilingTile({ fam }: { fam: GoldNoiseFamilySummary }) {
  const ceiling = fam.gold_right;
  const contestable = fam.model_defensible + fam.both_defensible;
  return (
    <div className="rounded-lg border border-border bg-surface p-3">
      <div className="flex items-baseline justify-between">
        <span className="text-[11px] font-semibold text-foreground">{fam.family}</span>
        <span className="text-[9px] text-muted">{fam.total} rows</span>
      </div>
      <div className="mt-1.5 flex items-baseline gap-1.5">
        <span className="font-mono text-xl font-semibold text-error">
          {pct(ceiling, fam.total)}
        </span>
        <span className="text-[9px] text-muted">ceiling</span>
      </div>
      <div className="text-[9px] text-muted">
        {ceiling}/{fam.total} genuine · {contestable}/{fam.total} contestable
      </div>
      <div className="mt-2 flex h-1.5 w-full overflow-hidden rounded-full bg-surface-raised">
        {VERDICT_ORDER.filter((v) => fam.by_verdict[v]).map((v) => (
          <div
            key={v}
            className={VERDICT_META[v]?.bar ?? "bg-muted"}
            style={{ width: `${(fam.by_verdict[v] / Math.max(1, fam.total)) * 100}%` }}
            title={`${VERDICT_META[v]?.label ?? v}: ${fam.by_verdict[v]}`}
          />
        ))}
      </div>
    </div>
  );
}

export function VerdictStackedBar({ families }: { families: GoldNoiseFamilySummary[] }) {
  return (
    <div className="space-y-1.5">
      {families.map((fam) => (
        <div key={fam.family} className="flex items-center gap-2">
          <span className="w-24 shrink-0 text-right text-[10px] text-muted">{fam.family}</span>
          <div className="flex h-4 flex-1 overflow-hidden rounded border border-border bg-surface-raised">
            {VERDICT_ORDER.filter((v) => fam.by_verdict[v]).map((v) => (
              <div
                key={v}
                className={`${VERDICT_META[v]?.bar ?? "bg-muted"} flex items-center justify-center`}
                style={{ width: `${(fam.by_verdict[v] / Math.max(1, fam.total)) * 100}%` }}
                title={`${VERDICT_META[v]?.label ?? v}: ${fam.by_verdict[v]}`}
              >
                {fam.by_verdict[v] >= 4 && (
                  <span className="text-[8px] font-medium text-white">{fam.by_verdict[v]}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// ── Mechanism × family matrix ──

export function MechanismMatrix({
  families,
  filter,
  onCellClick,
}: {
  families: GoldNoiseFamilySummary[];
  filter: { family: string; mechanism: string } | null;
  onCellClick: (family: string, mechanism: string) => void;
}) {
  const allMechanisms = useMemo(() => {
    const set = new Set<string>();
    for (const fam of families) for (const m of Object.keys(fam.by_mechanism)) set.add(m);
    return Array.from(set).sort((a, b) =>
      (MECHANISM_LABELS[a] ?? a).localeCompare(MECHANISM_LABELS[b] ?? b)
    );
  }, [families]);

  const max = useMemo(() => {
    let m = 0;
    for (const fam of families)
      for (const mech of allMechanisms) m = Math.max(m, fam.by_mechanism[mech] ?? 0);
    return Math.max(1, m);
  }, [families, allMechanisms]);

  return (
    <div className="overflow-auto">
      <div className="min-w-max">
        <div className="flex">
          <div className="w-44 shrink-0" />
          {families.map((fam) => (
            <div
              key={fam.family}
              className="flex w-24 items-end justify-center pb-1 text-[9px] font-medium text-muted"
            >
              {fam.family}
            </div>
          ))}
        </div>
        {allMechanisms.map((mech) => (
          <div key={mech} className="flex items-center">
            <div className="w-44 shrink-0 pr-2 text-right text-[9px] text-muted">
              {MECHANISM_LABELS[mech] ?? mech}
            </div>
            {families.map((fam) => {
              const count = fam.by_mechanism[mech] ?? 0;
              const selected = filter?.family === fam.family && filter?.mechanism === mech;
              const isGoldSide = mech.startsWith("gold_");
              return (
                <div key={fam.family} className="flex w-24 justify-center p-0.5">
                  <button
                    disabled={count === 0}
                    onClick={() => onCellClick(fam.family, mech)}
                    className={`flex h-7 w-full items-center justify-center rounded border text-[10px] font-medium transition-all disabled:cursor-default ${
                      count === 0
                        ? "border-border text-muted/40"
                        : selected
                          ? "border-hybrid ring-1 ring-hybrid"
                          : isGoldSide
                            ? "border-deterministic/30 text-deterministic hover:border-deterministic"
                            : "border-error/30 text-error hover:border-error"
                    }`}
                    style={
                      count > 0
                        ? {
                            backgroundColor: isGoldSide
                              ? `rgba(129, 178, 154, ${0.08 + (count / max) * 0.4})`
                              : `rgba(224, 122, 95, ${0.08 + (count / max) * 0.4})`,
                          }
                        : undefined
                    }
                    title={`${fam.family} · ${MECHANISM_LABELS[mech] ?? mech}: ${count}`}
                  >
                    {count > 0 ? count : ""}
                  </button>
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Item list ──

export function ItemRow({
  item,
  active,
  onClick,
}: {
  item: GoldNoiseItem;
  active: boolean;
  onClick: () => void;
}) {
  const v = VERDICT_META[item.verdict];
  return (
    <button
      onClick={onClick}
      className={`w-full border-b border-border px-3 py-2 text-left transition-all border-l-2 ${
        active ? "bg-llm/5 border-l-llm" : "hover:bg-surface-raised border-l-transparent"
      }`}
    >
      <div className="flex items-center gap-2">
        <span className="text-[10px] font-mono text-muted">{item.letter_id}</span>
        <span className="text-[9px] text-muted">{item.disagreement_type}</span>
        <span className={`rounded border px-1 py-0 text-[9px] font-medium ${v?.tone ?? ""}`}>
          {item.verdict}
        </span>
      </div>
      <div className="mt-0.5 truncate text-[11px] font-medium text-foreground">
        {item.match_key}
      </div>
      <div className="truncate text-[9px] text-muted">
        {MECHANISM_LABELS[item.mechanism] ?? item.mechanism}
      </div>
    </button>
  );
}

// ── Gan RQ10 view ──

export function GanAuditView({ data }: { data: GoldNoiseGanAuditResponse }) {
  if (!data.audit) {
    return <p className="text-[11px] text-muted">No Gan RQ10 audit file present.</p>;
  }
  const audit = data.audit;
  const metrics = (audit.metrics ?? {}) as Record<string, number>;
  const classCounts = (audit.primary_class_counts ?? {}) as Record<string, number>;
  const byFamily = (audit.by_hidden_family ?? {}) as Record<
    string,
    { rows: number; main_primary_class: string; primary_class_counts?: Record<string, number> }
  >;
  const rowCount = typeof audit.row_count === "number" ? audit.row_count : "—";
  const claimLanguage = typeof audit.claim_language === "string" ? audit.claim_language : "";
  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-llm/20 bg-llm/5 p-2.5 text-[10px] text-muted">
        <span className="font-medium text-llm">Different taxonomy. </span>
        {data.taxonomy_note}
      </div>
      <div>
        <h4 className="mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted">
          Primary class counts ({rowCount} hard rows)
        </h4>
        <div className="flex flex-wrap gap-1.5">
          {Object.entries(classCounts).map(([cls, n]) => (
            <span key={cls} className="rounded border border-border bg-surface px-2 py-0.5 text-[10px]">
              <span className="font-mono text-foreground">{n}</span>{" "}
              <span className="text-muted">{cls}</span>
            </span>
          ))}
        </div>
      </div>
      <div>
        <h4 className="mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted">
          Headline metrics
        </h4>
        <div className="grid grid-cols-2 gap-1.5 sm:grid-cols-3">
          {Object.entries(metrics).map(([k, v]) => (
            <div key={k} className="rounded border border-border bg-surface px-2 py-1 text-[10px]">
              <div className="font-mono text-foreground">
                {typeof v === "number"
                  ? k.includes("rate")
                    ? `${(v * 100).toFixed(1)}%`
                    : v
                  : String(v)}
              </div>
              <div className="truncate text-[9px] text-muted">{k}</div>
            </div>
          ))}
        </div>
      </div>
      <div>
        <h4 className="mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted">
          By hidden family
        </h4>
        <div className="overflow-hidden rounded-lg border border-border">
          <table className="w-full text-[10px]">
            <thead className="bg-surface-raised text-[9px] uppercase text-muted">
              <tr>
                <th className="px-2 py-1 text-left">Family</th>
                <th className="px-2 py-1 text-right">Rows</th>
                <th className="px-2 py-1 text-left">Main class</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(byFamily)
                .sort((a, b) => b[1].rows - a[1].rows)
                .map(([name, info]) => (
                  <tr key={name} className="border-t border-border">
                    <td className="px-2 py-1 font-mono text-foreground">{name}</td>
                    <td className="px-2 py-1 text-right">{info.rows}</td>
                    <td className="px-2 py-1 text-muted">{info.main_primary_class}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
      {claimLanguage && (
        <p className="rounded border border-border bg-surface-raised p-2 text-[9px] italic text-muted">
          {claimLanguage}
        </p>
      )}
    </div>
  );
}

// ── Hypotheses view ──

export function HypothesesView({ data }: { data: GoldNoiseHypothesesResponse }) {
  if (data.count === 0) {
    return <p className="text-[11px] text-muted">No hypothesis registry entries.</p>;
  }
  const verdictTone: Record<string, string> = {
    CONFIRMED: "border-success/30 text-success bg-success/10",
    REFUTED: "border-error/30 text-error bg-error/10",
    PARTIAL: "border-llm/30 text-llm bg-llm/10",
    OPEN: "border-border text-muted bg-surface-raised",
  };
  return (
    <div className="space-y-4">
      {Object.entries(data.by_family)
        .sort((a, b) => a[0].localeCompare(b[0]))
        .map(([family, entries]) => (
          <div key={family}>
            <h4 className="mb-1 text-[10px] font-semibold uppercase tracking-wider text-muted">
              {family} ({entries.length})
            </h4>
            <div className="space-y-1.5">
              {entries.map((e) => (
                <div key={e.hypothesis_id} className="rounded-lg border border-border bg-surface p-2.5">
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-mono text-[9px] text-muted">{e.date}</span>
                    <span
                      className={`shrink-0 rounded border px-1.5 py-0 text-[9px] font-medium ${
                        verdictTone[e.verdict] ?? verdictTone.OPEN
                      }`}
                    >
                      {e.verdict}
                    </span>
                  </div>
                  <p className="mt-0.5 text-[11px] text-foreground">{e.statement}</p>
                  {e.notes && <p className="mt-1 text-[10px] text-muted">{e.notes}</p>}
                </div>
              ))}
            </div>
          </div>
        ))}
    </div>
  );
}

// ── Defects view ──

export function DefectsView({ data }: { data: GoldNoiseIssuesResponse }) {
  if (data.count === 0) {
    return <p className="text-[11px] text-muted">No genuine gold defects recorded.</p>;
  }
  return (
    <div className="space-y-2">
      <p className="text-[10px] text-muted">
        Confirmed genuine gold defects (frozen corpus NOT edited). {data.count} recorded.
      </p>
      {data.issues.map((issue, i) => {
        const letterId = String(issue.letter_id ?? "—");
        const entity = String(issue.entity ?? "—");
        const field = String(issue.field ?? "—");
        const date = String(issue.date ?? "—");
        const goldValue = String(issue.gold_value ?? "—");
        const conflicting =
          typeof issue.conflicting_evidence === "string" ? issue.conflicting_evidence : "";
        const notes = typeof issue.notes === "string" ? issue.notes : "";
        return (
          <div key={i} className="rounded-lg border border-error/20 bg-error/5 p-3">
            <div className="flex items-center gap-2">
              <span className="font-mono text-[11px] font-semibold text-foreground">{letterId}</span>
              <span className="rounded border border-border bg-surface px-1.5 py-0 text-[9px] text-muted">
                {entity} · {field}
              </span>
              <span className="ml-auto text-[9px] text-muted">{date}</span>
            </div>
            <p className="mt-1.5 text-[11px] text-foreground">
              <span className="text-muted">Gold value: </span>
              <span className="font-mono">{goldValue}</span>
            </p>
            {conflicting && <p className="mt-1 text-[10px] text-muted">{conflicting}</p>}
            {notes && <p className="mt-1 text-[9px] italic text-muted">{notes}</p>}
          </div>
        );
      })}
    </div>
  );
}
