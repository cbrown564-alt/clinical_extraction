"use client";

import type { SfLayerAPair } from "@/lib/types";
import { buildComparisonColumns, describePairDivergence } from "@/lib/sfSchema";

/**
 * Layer A evidence: one-line divergence cue + gold/pred table.
 * Only diverge (and identity) columns by default – matching slots stay hidden.
 */
export function AttributeSchemaCard({
  pair,
  divergeOnly = true,
}: {
  pair: SfLayerAPair;
  divergeOnly?: boolean;
}) {
  const divergence = describePairDivergence(pair);
  const allColumns = buildComparisonColumns(pair);
  // Prefer diverge columns only – matching identity (CUI) is noise once the
  // phrase header already establishes which mention this is.
  const columns = divergeOnly
    ? allColumns.filter((c) => c.state === "diverge")
    : allColumns;
  // Never fall back to an all-green same-column table – that contradicts a
  // mismatch framing. Empty means attributes already agree.
  if (columns.length === 0) {
    return divergence ? (
      <div className="flex flex-col gap-2.5">
        <DivergenceCue divergence={divergence} />
      </div>
    ) : null;
  }

  return (
    <div className="flex flex-col gap-2.5">
      {divergence && <DivergenceCue divergence={divergence} />}
      <ComparisonTable columns={columns} />
    </div>
  );
}

function DivergenceCue({
  divergence,
}: {
  divergence: NonNullable<ReturnType<typeof describePairDivergence>>;
}) {
  if (divergence.kind === "structural") {
    return (
      <p className="text-xs leading-relaxed text-foreground">
        <span className="font-semibold text-hybrid">Shape mismatch</span>
        <span className="mx-1.5 text-muted">·</span>
        <span className="text-gold">G</span> {divergence.goldShape}
        <span className="mx-1 text-muted">→</span>
        <span className="text-llm">P</span> {divergence.predShape}
      </p>
    );
  }

  return (
    <p className="text-xs leading-relaxed text-foreground">
      <span className="font-semibold text-error">Value mismatch</span>
      <span className="mx-1.5 text-muted">·</span>
      {divergence.diffs.map((d, i) => (
        <span key={d.label} className="inline-flex items-baseline gap-1">
          {i > 0 && <span className="mx-1 text-muted">·</span>}
          <span className="font-mono text-xs font-semibold text-muted">{d.label}</span>
          <span className="font-mono text-gold">{d.gold || "–"}</span>
          <span className="text-muted">/</span>
          <span className="font-mono text-llm">{d.pred || "–"}</span>
        </span>
      ))}
    </p>
  );
}

function ComparisonTable({ columns }: { columns: ReturnType<typeof buildComparisonColumns> }) {
  let zebra = false;
  let prevGroup: string | null = null;
  const zebraByGroup = new Map<string, boolean>();
  for (const col of columns) {
    if (col.groupId !== prevGroup) {
      zebra = !zebra;
      prevGroup = col.groupId;
    }
    zebraByGroup.set(col.groupId, zebra);
  }

  const groupSpans: { groupId: string; groupLabel: string; span: number }[] = [];
  for (const col of columns) {
    const last = groupSpans[groupSpans.length - 1];
    if (last && last.groupId === col.groupId) last.span += 1;
    else groupSpans.push({ groupId: col.groupId, groupLabel: col.groupLabel, span: 1 });
  }

  return (
    <div className="overflow-x-auto rounded-md border border-border">
      <table className="min-w-full border-collapse text-xs">
        <thead>
          <tr>
            <th className="sticky left-0 w-8 border-b border-border bg-surface px-2.5 py-1.5" />
            {groupSpans.map((g) => (
              <th
                key={g.groupId + g.groupLabel}
                colSpan={g.span}
                className={`border-b border-l border-border px-3 py-1.5 text-left text-[11px] font-bold uppercase tracking-wider text-muted ${
                  zebraByGroup.get(g.groupId) ? "bg-surface-raised" : "bg-surface"
                }`}
              >
                {g.groupLabel}
              </th>
            ))}
          </tr>
          <tr>
            <th className="sticky left-0 border-b border-border bg-surface px-2.5 py-1.5" />
            {columns.map((c) => (
              <th
                key={c.key}
                className={`border-b border-l border-border px-3 py-1.5 text-left font-mono text-xs font-semibold ${
                  c.state === "diverge"
                    ? "bg-error/10 text-error"
                    : zebraByGroup.get(c.groupId)
                      ? "bg-surface-raised text-muted"
                      : "bg-surface text-muted"
                }`}
              >
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            <td className="sticky left-0 border-b border-border bg-surface px-2.5 py-2.5 font-mono text-xs font-extrabold text-gold">
              G
            </td>
            {columns.map((c) => (
              <ValueCell key={c.key} value={c.gold} state={c.state} zebra={!!zebraByGroup.get(c.groupId)} />
            ))}
          </tr>
          <tr>
            <td className="sticky left-0 bg-surface px-2.5 py-2.5 font-mono text-xs font-extrabold text-llm">
              P
            </td>
            {columns.map((c) => (
              <ValueCell key={c.key} value={c.pred} state={c.state} zebra={!!zebraByGroup.get(c.groupId)} />
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}

function ValueCell({
  value,
  state,
  zebra,
}: {
  value: string;
  state: "same" | "diverge";
  zebra: boolean;
}) {
  const filled = !!value;
  const tone = !filled
    ? `italic text-muted ${zebra ? "bg-surface-raised" : "bg-surface"}`
    : state === "same"
      ? "bg-success/10 text-success font-semibold"
      : "bg-error/10 text-error font-bold";
  return (
    <td className={`border-l border-border px-3 py-2.5 font-mono text-xs ${tone}`}>
      {filled ? value : "–"}
    </td>
  );
}
