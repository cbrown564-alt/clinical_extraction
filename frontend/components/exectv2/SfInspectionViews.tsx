"use client";

import type {
  SfAttributeRow,
  SfComponentMeta,
  SfInspectionLetter,
  SfInspectionScorecard,
  SfLayerAPair,
  SfLayerBComponent,
  SfLineage,
  SfMentionRow,
} from "@/lib/types";

// ── Component order (must match the backend COMPONENT_ORDER) ──
//
// The 11 FrequencyStateScores, ordered burden -> direction/magnitude axes ->
// filtered states -> attribute-level exact matches.

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

// ── Status / match presentation tokens ──

export const STATUS_META: Record<
  SfMentionRow["status"],
  { label: string; tone: string }
> = {
  tp: { label: "TP", tone: "text-success" },
  fp: { label: "FP", tone: "text-error" },
  fn: { label: "FN", tone: "text-error" },
  skip: { label: "—", tone: "text-muted" },
};

export const MATCH_META: Record<
  SfAttributeRow["match"],
  { symbol: string; tone: string }
> = {
  ok: { symbol: "✓", tone: "text-success" },
  bad: { symbol: "✗", tone: "text-error" },
  absent: { symbol: "—", tone: "text-muted" },
};

export const VALIDITY_LABEL: Record<SfAttributeRow["validity"], string> = {
  ok: "ok",
  absent: "—",
  illegal_value: "OUT OF VOCAB",
  illegal_attr: "ILLEGAL ATTR",
  noise: "noise attr",
};

export const VALIDITY_TONE: Record<SfAttributeRow["validity"], string> = {
  ok: "text-success",
  absent: "text-muted",
  illegal_value: "text-error font-semibold",
  illegal_attr: "text-error font-semibold",
  noise: "text-muted",
};

function fmtVal(v: string): string {
  return v === "" ? "—" : v;
}

// ── Scorecard table (the 11-component F1/P/R/TP/FP/FN grid) ──

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
            const isDir = name === "state_profile_directional";
            const isMag = name === "state_profile_magnitude";
            return (
              <tr key={name} className="odd:bg-surface">
                <td
                  className={`border border-border px-2 py-1 font-mono ${
                    isDir || isMag ? "font-semibold text-foreground" : "text-foreground"
                  }`}
                >
                  {name}
                  {isDir && <span className="ml-1 text-[8px] text-deterministic">anchor</span>}
                  {isMag && <span className="ml-1 text-[8px] text-deterministic">anchor</span>}
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

// ── Master list row ──

export function LetterRow({
  letter,
  active,
  onClick,
}: {
  letter: SfInspectionLetter;
  active: boolean;
  onClick: () => void;
}) {
  const { direction_errors: dir, magnitude_errors: mag, total_errors: total } = letter;
  const hasErr = total > 0;

  return (
    <button
      onClick={onClick}
      className={`flex w-full items-center gap-2 border-b border-border px-3 py-1.5 text-left transition-colors ${
        active ? "bg-deterministic/10" : "hover:bg-surface-raised"
      }`}
    >
      <span className="font-mono text-[10px] font-semibold text-foreground">
        {letter.letter_id}
      </span>
      <span className="text-[9px] text-muted">
        g{letter.gold_count}/p{letter.pred_count}
      </span>
      {!letter.has_activity ? (
        <span className="ml-auto rounded border border-border bg-surface-raised px-1.5 py-0 text-[8px] text-muted">
          no SF
        </span>
      ) : !hasErr ? (
        <span className="ml-auto rounded border border-success/30 bg-success/10 px-1.5 py-0 text-[8px] text-success">
          clean
        </span>
      ) : (
        <span className="ml-auto flex items-center gap-1">
          <span className="rounded border border-error/30 bg-error/10 px-1.5 py-0 font-mono text-[8px] text-error">
            dir {dir.fp}f+{dir.fn}n
          </span>
          <span className="rounded border border-error/30 bg-error/10 px-1.5 py-0 font-mono text-[8px] text-error">
            mag {mag.fp}f+{mag.fn}n
          </span>
          <span className="rounded border border-llm/30 bg-llm/10 px-1.5 py-0 font-mono text-[8px] font-semibold text-llm">
            {total}
          </span>
        </span>
      )}
    </button>
  );
}

// ── Layer A: schema attribute pairs ──

export function LayerA({ pairs }: { pairs: SfLayerAPair[] }) {
  if (!pairs.length) {
    return (
      <p className="px-1 py-2 text-[10px] text-muted">
        No SeizureFrequency mentions (gold or prediction) for this letter.
      </p>
    );
  }
  return (
    <div className="space-y-2">
      <p className="text-[9px] leading-relaxed text-muted">
        <span className="font-semibold text-foreground">Layer A — schema attributes.</span>{" "}
        Gold↔prediction pairs use the scorer&apos;s max-cardinality phrase-overlap
        matcher. For each predicted attribute the chain shown is:{" "}
        <span className="font-semibold">raw</span> →{" "}
        <span className="font-semibold">closed-vocab validity</span> →{" "}
        <span className="font-semibold">canonicalized</span> → compared to gold.
        Out-of-vocab or unexpected attributes are flagged.
      </p>
      {pairs.map((pair, i) => (
        <AttrPair key={i} pair={pair} />
      ))}
    </div>
  );
}

function pairTone(side: SfLayerAPair["side"]): string {
  if (side === "fn") return "border-l-error bg-error/5";
  if (side === "fp") return "border-l-error bg-error/5";
  return "border-l-gold";
}

function pairLabelTone(side: SfLayerAPair["side"]): string {
  if (side === "fn" || side === "fp") return "text-error";
  return "text-llm";
}

function AttrPair({ pair }: { pair: SfLayerAPair }) {
  return (
    <div
      className={`rounded-r border border-t border-r border-b border-border border-l-2 ${pairTone(
        pair.side
      )} p-2`}
    >
      <p
        className={`mb-1.5 text-[9px] font-semibold uppercase tracking-wide ${pairLabelTone(
          pair.side
        )}`}
      >
        {pair.label}
      </p>
      <table className="w-full border-collapse text-[10px]">
        <thead>
          <tr>
            <th className="border border-border bg-surface-raised px-1.5 py-0.5 text-left font-semibold text-muted">
              attribute
            </th>
            <th className="border border-border bg-surface-raised px-1.5 py-0.5 text-left font-semibold text-muted">
              gold (raw)
            </th>
            <th className="border border-border bg-surface-raised px-1.5 py-0.5 text-left font-semibold text-muted">
              pred (raw)
            </th>
            <th className="border border-border bg-surface-raised px-1.5 py-0.5 text-left font-semibold text-muted">
              validity
            </th>
            <th className="border border-border bg-surface-raised px-1.5 py-0.5 text-left font-semibold text-muted">
              canon
            </th>
            <th className="border border-border bg-surface-raised px-1.5 py-0.5 text-center font-semibold text-muted">
              ✓
            </th>
          </tr>
        </thead>
        <tbody>
          {/* phrase row */}
          <tr className="bg-surface-raised/50">
            <td className="border border-border px-1.5 py-0.5 font-semibold text-foreground">
              text (norm)
            </td>
            <td className="border border-border px-1.5 py-0.5 text-muted">
              {fmtVal(pair.gold_phrase)} → {fmtVal(pair.gold_normalized)}
            </td>
            <td className="border border-border px-1.5 py-0.5 text-foreground">
              {fmtVal(pair.pred_phrase)}
            </td>
            <td className="border border-border px-1.5 py-0.5 text-muted">—</td>
            <td className="border border-border px-1.5 py-0.5 text-foreground">
              {fmtVal(pair.pred_normalized)}
            </td>
            <td
              className={`border border-border px-1.5 py-0.5 text-center font-semibold ${MATCH_META[pair.phrase_match].tone}`}
            >
              {MATCH_META[pair.phrase_match].symbol}
            </td>
          </tr>
          {pair.attributes.map((attr) => (
            <tr key={attr.key}>
              <td className="border border-border px-1.5 py-0.5 font-semibold text-foreground">
                {attr.key}
              </td>
              <td className="border border-border px-1.5 py-0.5 text-muted">
                {fmtVal(attr.gold)}
              </td>
              <td className="border border-border px-1.5 py-0.5 text-foreground">
                {fmtVal(attr.pred)}
              </td>
              <td
                className={`border border-border px-1.5 py-0.5 ${VALIDITY_TONE[attr.validity]}`}
              >
                {VALIDITY_LABEL[attr.validity]}
              </td>
              <td className="border border-border px-1.5 py-0.5 font-mono text-foreground">
                {attr.canonical ? attr.canonical : "—"}
              </td>
              <td
                className={`border border-border px-1.5 py-0.5 text-center font-semibold ${MATCH_META[attr.match].tone}`}
              >
                {MATCH_META[attr.match].symbol}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ── Layer B: the 11 scoring components ──

export function LayerB({
  components,
  componentsMeta,
}: {
  components: SfLayerBComponent[];
  componentsMeta: SfComponentMeta[];
}) {
  const metaByName = new Map(componentsMeta.map((c) => [c.name, c.info]));
  return (
    <div className="space-y-2">
      <p className="text-[9px] leading-relaxed text-muted">
        <span className="font-semibold text-foreground">Layer B — scoring components.</span>{" "}
        Each of the 11 FrequencyStateScores projects every mention through a
        different rule into a hashable key; letters are scored by multiset
        (order-independent) match. Each table shows a mention&apos;s inputs →
        count-state → projected state → final key, with TP/FP/FN for this letter.
      </p>
      {components.map((comp) => (
        <ComponentBlock key={comp.name} comp={comp} info={metaByName.get(comp.name) ?? ""} />
      ))}
    </div>
  );
}

function ComponentBlock({ comp, info }: { comp: SfLayerBComponent; info: string }) {
  return (
    <div
      className={`rounded border p-2 ${
        comp.has_error ? "border-error/30 bg-error/5" : "border-border bg-surface"
      }`}
    >
      <div className="mb-1.5 flex flex-wrap items-center gap-2">
        <span className="font-mono text-[10px] font-semibold text-foreground">
          {comp.name}
        </span>
        {comp.has_error ? (
          <span className="text-[9px] font-semibold text-error">
            tp={comp.tp} · fp={comp.fp} · fn={comp.fn}
          </span>
        ) : (
          <span className="text-[9px] font-semibold text-success">
            clean (tp={comp.tp})
          </span>
        )}
        <p className="basis-full text-[9px] leading-relaxed text-muted">{info}</p>
      </div>
      <table className="w-full border-collapse text-[10px]">
        <thead>
          <tr>
            <th className="border border-border bg-surface-raised px-1.5 py-0.5 text-left font-semibold text-muted">
              side
            </th>
            <th className="border border-border bg-surface-raised px-1.5 py-0.5 text-left font-semibold text-muted">
              phrase
            </th>
            <th className="border border-border bg-surface-raised px-1.5 py-0.5 text-left font-semibold text-muted">
              counts
            </th>
            <th className="border border-border bg-surface-raised px-1.5 py-0.5 text-left font-semibold text-muted">
              FreqChg
            </th>
            <th className="border border-border bg-surface-raised px-1.5 py-0.5 text-left font-semibold text-muted">
              cnt→st
            </th>
            <th className="border border-border bg-surface-raised px-1.5 py-0.5 text-left font-semibold text-muted">
              proj
            </th>
            <th className="border border-border bg-surface-raised px-1.5 py-0.5 text-left font-semibold text-muted">
              key
            </th>
            <th className="border border-border bg-surface-raised px-1.5 py-0.5 text-center font-semibold text-muted">
              ●
            </th>
          </tr>
        </thead>
        <tbody>
          {comp.rows.length === 0 && (
            <tr>
              <td colSpan={8} className="border border-border px-1.5 py-1 text-center text-muted">
                no SeizureFrequency mentions
              </td>
            </tr>
          )}
          {comp.rows.map((row, i) => (
            <MentionRowView key={i} row={row} />
          ))}
        </tbody>
      </table>
    </div>
  );
}

function MentionRowView({ row }: { row: SfMentionRow }) {
  const isSkip = row.status === "skip";
  return (
    <tr className={isSkip ? "opacity-50" : ""}>
      <td
        className={`border border-border px-1.5 py-0.5 font-semibold ${
          row.side === "gold" ? "text-gold" : "text-llm"
        }`}
      >
        {row.side}
      </td>
      <td className="border border-border px-1.5 py-0.5 text-foreground">{row.phrase}</td>
      <td className="border border-border px-1.5 py-0.5 text-muted">{row.counts}</td>
      <td className="border border-border px-1.5 py-0.5 text-muted">
        {row.frequency_change || "—"}
      </td>
      <td className="border border-border px-1.5 py-0.5 text-muted">
        {row.count_state || "—"}
      </td>
      <td className="border border-border px-1.5 py-0.5 font-semibold text-foreground">
        {isSkip ? "— filtered —" : row.projected_state}
      </td>
      <td className="border border-border px-1.5 py-0.5 font-mono text-[9px] text-foreground">
        {isSkip ? "(no key)" : row.key}
      </td>
      <td
        className={`border border-border px-1.5 py-0.5 text-center font-semibold ${
          STATUS_META[row.status].tone
        }`}
      >
        {STATUS_META[row.status].label}
      </td>
    </tr>
  );
}

// ── Lineage panel ──

export function LineagePanel({ lineage }: { lineage: SfLineage }) {
  const spans = lineage.candidate_spans;
  const override = lineage.override;
  return (
    <div className="rounded border border-border bg-surface-raised p-2.5">
      <p className="text-[9px] font-semibold uppercase tracking-wider text-muted">
        Prediction lineage
      </p>
      <p className="mt-1 text-[9px] leading-relaxed text-muted">
        SeizureFrequency is rules-owned: the deterministic SeizureFrequencyDictionaryLens
        mapped candidate spans (phrase→CUI, count/range extraction, state inference) into the
        scored mentions. Where the magnitude complement fired, the LLM overwrote{" "}
        <span className="font-mono">FrequencyChange</span> — shown below.
      </p>

      {override && override.applied && (
        <div className="mt-2 rounded border border-hybrid/30 bg-hybrid/10 p-2">
          <p className="text-[9px] font-semibold text-hybrid">
            LLM magnitude-complement override applied
          </p>
          <ul className="mt-1 space-y-0.5">
            {override.items?.map((item, i) => (
              <li key={i} className="font-mono text-[9px] text-foreground">
                <span className="text-muted">{item.applies_to}</span>:{" "}
                <span className="text-error line-through">
                  {item.prior_frequency_change || "(none)"}
                </span>{" "}
                → <span className="font-semibold text-foreground">{item.assembled_magnitude}</span>{" "}
                <span className="text-muted">
                  (selector {item.selection_mode}, candidate {item.selected_candidate_id})
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
      {override && !override.applied && (
        <div className="mt-2 rounded border border-border bg-surface p-2 text-[9px] text-muted">
          FrequencyChange differs from baseline v08 (baseline {JSON.stringify(override.baseline)}{" "}
          vs complement {JSON.stringify(override.complement)}).
        </div>
      )}

      <p className="mt-2 text-[9px] font-semibold uppercase tracking-wider text-muted">
        Candidate spans (decision_lane=active_rate) · {spans.length}
      </p>
      {spans.length === 0 ? (
        <p className="mt-0.5 text-[9px] text-muted">no candidate_spans recorded</p>
      ) : (
        <ul className="mt-0.5 space-y-0.5">
          {spans.slice(0, 8).map((span, i) => (
            <li key={i} className="text-[9px]">
              <span className="font-mono text-foreground">{span.text_hint}</span>{" "}
              <span className="text-muted">
                [{span.candidate_type} · {span.source}]
              </span>{" "}
              <span className="text-muted">{span.evidence}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
